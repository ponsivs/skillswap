from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.session import LearningSession
from app.models.skill import Skill, UserSkill
from app.models.user import User
from app.models.review import Review
from app.services.credits import CreditService
from app.services.notification import NotificationService

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', 'all')
    
    query = LearningSession.query.filter(
        (LearningSession.teacher_id == current_user.id) | 
        (LearningSession.learner_id == current_user.id)
    )

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    sessions = query.order_by(LearningSession.session_date.desc()).all()

    # Counts
    pending_count = LearningSession.query.filter(
        (LearningSession.teacher_id == current_user.id) | (LearningSession.learner_id == current_user.id),
        LearningSession.status == 'pending'
    ).count()

    accepted_count = LearningSession.query.filter(
        (LearningSession.teacher_id == current_user.id) | (LearningSession.learner_id == current_user.id),
        LearningSession.status == 'accepted'
    ).count()

    completed_count = LearningSession.query.filter(
        (LearningSession.teacher_id == current_user.id) | (LearningSession.learner_id == current_user.id),
        LearningSession.status == 'completed'
    ).count()

    return render_template(
        'sessions/index.html',
        sessions=sessions,
        status_filter=status_filter,
        pending_count=pending_count,
        accepted_count=accepted_count,
        completed_count=completed_count
    )

@sessions_bp.route('/request/<int:mentor_id>', methods=['GET', 'POST'])
@login_required
def request_session(mentor_id):
    if mentor_id == current_user.id:
        flash('You cannot request a session with yourself.', 'warning')
        return redirect(url_for('matching.index'))

    mentor = User.query.get_or_404(mentor_id)

    # Check credit balance
    can_request, credit_msg = CreditService.can_request_session(current_user.id, 5)
    if not can_request:
        flash(credit_msg, 'danger')
        return redirect(url_for('credits.index'))

    # Skills the mentor can teach
    mentor_skills = [us.skill for us in mentor.teaching_skills if us.skill]

    if request.method == 'POST':
        skill_id = request.form.get('skill_id', type=int)
        session_date_str = request.form.get('session_date')
        session_time_str = request.form.get('session_time')
        duration = request.form.get('duration', 45, type=int)
        notes = request.form.get('notes', '').strip()

        if not skill_id or not session_date_str or not session_time_str:
            flash('Please specify the skill, date, and preferred time.', 'warning')
            return render_template('sessions/request.html', mentor=mentor, mentor_skills=mentor_skills)

        try:
            full_datetime_str = f"{session_date_str} {session_time_str}"
            session_dt = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            session_dt = datetime.utcnow() + timedelta(days=2)

        # Generate a private internal meeting link (e.g. Jitsi Room)
        room_name = f"skillswap-room-{mentor.id}-{current_user.id}-{int(datetime.utcnow().timestamp())}"
        meeting_link = f"https://meet.jit.si/{room_name}"

        new_session = LearningSession(
            teacher_id=mentor.id,
            learner_id=current_user.id,
            skill_id=skill_id,
            session_date=session_dt,
            duration_minutes=duration,
            status='pending',
            credits_amount=5,
            notes=notes,
            meeting_link=meeting_link
        )
        db.session.add(new_session)
        db.session.commit()

        # Notify mentor
        skill = Skill.query.get(skill_id)
        NotificationService.create(
            user_id=mentor.id,
            title="New Learning Session Request!",
            message=f"{current_user.full_name} has requested a {duration}-min session for {skill.skill_name}.",
            link=f"/sessions",
            notification_type="session_request"
        )

        flash(f'Learning request sent to {mentor.full_name}! They will review your invitation.', 'success')
        return redirect(url_for('sessions.index'))

    return render_template('sessions/request.html', mentor=mentor, mentor_skills=mentor_skills)

@sessions_bp.route('/<int:session_id>/accept', methods=['POST'])
@login_required
def accept_session(session_id):
    sess = LearningSession.query.get_or_404(session_id)
    if sess.teacher_id != current_user.id:
        flash('Only the requested mentor can accept this session.', 'danger')
        return redirect(url_for('sessions.index'))

    sess.status = 'accepted'
    db.session.commit()

    NotificationService.create(
        user_id=sess.learner_id,
        title="Session Request Accepted!",
        message=f"{current_user.full_name} accepted your session for {sess.skill.skill_name} on {sess.session_date.strftime('%b %d, %H:%M')}.",
        link=f"/sessions",
        notification_type="session_accepted"
    )

    flash('Session accepted! Meeting details and room link are now active.', 'success')
    return redirect(url_for('sessions.index'))

@sessions_bp.route('/<int:session_id>/reject', methods=['POST'])
@login_required
def reject_session(session_id):
    sess = LearningSession.query.get_or_404(session_id)
    if sess.teacher_id != current_user.id:
        flash('Only the requested mentor can decline this session.', 'danger')
        return redirect(url_for('sessions.index'))

    sess.status = 'rejected'
    db.session.commit()

    NotificationService.create(
        user_id=sess.learner_id,
        title="Session Request Declined",
        message=f"{current_user.full_name} could not accommodate the session for {sess.skill.skill_name}.",
        link=f"/sessions",
        notification_type="session_rejected"
    )

    flash('Session declined.', 'info')
    return redirect(url_for('sessions.index'))

@sessions_bp.route('/<int:session_id>/complete', methods=['POST'])
@login_required
def complete_session(session_id):
    success, message = CreditService.complete_session(session_id, current_user.id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('sessions.index'))

@sessions_bp.route('/<int:session_id>/cancel', methods=['POST'])
@login_required
def cancel_session(session_id):
    sess = LearningSession.query.get_or_404(session_id)
    if current_user.id not in (sess.teacher_id, sess.learner_id):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('sessions.index'))

    if sess.status == 'completed':
        flash('Completed sessions cannot be cancelled.', 'warning')
        return redirect(url_for('sessions.index'))

    sess.status = 'cancelled'
    db.session.commit()

    other_user_id = sess.learner_id if current_user.id == sess.teacher_id else sess.teacher_id
    NotificationService.create(
        user_id=other_user_id,
        title="Session Cancelled",
        message=f"The session for {sess.skill.skill_name} was cancelled by {current_user.full_name}.",
        link="/sessions",
        notification_type="system"
    )

    flash('Session cancelled.', 'info')
    return redirect(url_for('sessions.index'))

@sessions_bp.route('/<int:session_id>/review', methods=['POST'])
@login_required
def submit_review(session_id):
    sess = LearningSession.query.get_or_404(session_id)
    if sess.status != 'completed':
        flash('Reviews can only be submitted for completed sessions.', 'warning')
        return redirect(url_for('sessions.index'))

    if current_user.id not in (sess.teacher_id, sess.learner_id):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('sessions.index'))

    reviewee_id = sess.teacher_id if current_user.id == sess.learner_id else sess.learner_id

    # Check if already reviewed
    existing = Review.query.filter_by(session_id=sess.id, reviewer_id=current_user.id).first()
    if existing:
        flash('You have already submitted a review for this session.', 'info')
        return redirect(url_for('sessions.index'))

    rating = request.form.get('rating', 5, type=int)
    feedback = request.form.get('feedback', '').strip()
    learning_outcome = request.form.get('learning_outcome', '').strip()

    if not feedback:
        flash('Please write a brief feedback comment.', 'warning')
        return redirect(url_for('sessions.index'))

    review = Review(
        session_id=sess.id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee_id,
        rating=max(1, min(5, rating)),
        feedback=feedback,
        learning_outcome=learning_outcome
    )
    db.session.add(review)
    db.session.commit()

    NotificationService.create(
        user_id=reviewee_id,
        title="New Feedback Received!",
        message=f"{current_user.full_name} left you a {rating}★ review: \"{feedback[:60]}...\"",
        link=f"/profile/{reviewee_id}",
        notification_type="review"
    )

    flash('Thank you! Your feedback has been recorded and posted to the student profile.', 'success')
    return redirect(url_for('sessions.index'))
