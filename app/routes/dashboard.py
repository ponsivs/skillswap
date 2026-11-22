from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.session import LearningSession
from app.models.credit import CreditTransaction
from app.services.matching import MatchingEngine

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Recommended Skill Partners via Matching Engine
    recommendations = MatchingEngine.get_matches_for_user(current_user.id, limit=4)

    # Active & Upcoming sessions
    active_sessions = LearningSession.query.filter(
        ((LearningSession.teacher_id == current_user.id) | (LearningSession.learner_id == current_user.id)),
        LearningSession.status.in_(['pending', 'accepted'])
    ).order_by(LearningSession.session_date.asc()).limit(5).all()

    # Recent completed sessions
    recent_completed = LearningSession.query.filter(
        ((LearningSession.teacher_id == current_user.id) | (LearningSession.learner_id == current_user.id)),
        LearningSession.status == 'completed'
    ).order_by(LearningSession.updated_at.desc()).limit(3).all()

    # Recent credit ledger activities
    recent_activities = CreditTransaction.query.filter_by(
        user_id=current_user.id
    ).order_by(CreditTransaction.created_at.desc()).limit(5).all()

    # Stats
    teach_count = len(current_user.teaching_skills)
    learn_count = len(current_user.learning_skills)
    credits_balance = current_user.credits_balance
    completed_sessions = current_user.completed_sessions_count
    
    # Calculate overall learning progress
    learn_skills = current_user.learning_skills
    if learn_skills:
        avg_progress = int(sum(us.progress_percentage for us in learn_skills) / len(learn_skills))
    else:
        avg_progress = 0

    return render_template(
        'dashboard/index.html',
        recommendations=recommendations,
        active_sessions=active_sessions,
        recent_completed=recent_completed,
        recent_activities=recent_activities,
        teach_count=teach_count,
        learn_count=learn_count,
        credits_balance=credits_balance,
        completed_sessions=completed_sessions,
        avg_progress=avg_progress
    )
