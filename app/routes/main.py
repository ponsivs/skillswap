from flask import Blueprint, render_template
from app.models.skill import Skill
from app.models.user import User
from app.models.session import LearningSession

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_skills = Skill.query.limit(8).all()
    total_students = User.query.filter_by(role='student').count() or 120
    total_skills = Skill.query.count() or 35
    total_sessions = LearningSession.query.filter_by(status='completed').count() or 450

    return render_template(
        'landing.html',
        featured_skills=featured_skills,
        total_students=total_students,
        total_skills=total_skills,
        total_sessions=total_sessions
    )

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')
