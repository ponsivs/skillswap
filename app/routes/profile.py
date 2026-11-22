from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.report import Report
from app.models.review import Review

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/<int:user_id>')
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(reviewee_id=user.id).order_by(Review.created_at.desc()).all()
    
    return render_template(
        'profile/view.html',
        profile_user=user,
        reviews=reviews
    )

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        institution = request.form.get('institution', '').strip()
        education_level = request.form.get('education_level', '')
        bio = request.form.get('bio', '').strip()
        availability = request.form.get('availability', '').strip()
        learning_interests = request.form.get('learning_interests', '').strip()
        avatar_choice = request.form.get('avatar_choice', '')

        if full_name:
            current_user.full_name = full_name
        current_user.institution = institution
        current_user.education_level = education_level
        current_user.bio = bio
        current_user.availability = availability
        current_user.learning_interests = learning_interests
        
        if avatar_choice:
            current_user.avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={avatar_choice}"
        else:
            current_user.avatar_url = f"https://api.dicebear.com/7.x/initials/svg?seed={current_user.full_name}"

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    return render_template('profile/edit.html')

@profile_bp.route('/report/<int:user_id>', methods=['POST'])
@login_required
def report_user(user_id):
    if user_id == current_user.id:
        flash('You cannot report yourself.', 'warning')
        return redirect(url_for('dashboard.index'))

    reason = request.form.get('reason', '').strip()
    details = request.form.get('details', '').strip()

    if not reason:
        flash('Please select a report reason.', 'warning')
        return redirect(url_for('profile.view_profile', user_id=user_id))

    report = Report(
        reporter_id=current_user.id,
        reported_user_id=user_id,
        reason=reason,
        details=details,
        status='pending'
    )
    db.session.add(report)
    db.session.commit()

    flash('Report submitted. Our moderation team will review this profile promptly.', 'info')
    return redirect(url_for('profile.view_profile', user_id=user_id))
