from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.session import LearningSession
from app.models.credit import CreditTransaction
from app.models.report import Report

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    total_students = User.query.filter_by(role='student').count()
    total_skills = Skill.query.count()
    total_sessions = LearningSession.query.count()
    completed_sessions = LearningSession.query.filter_by(status='completed').count()
    pending_reports = Report.query.filter_by(status='pending').count()
    total_transactions = CreditTransaction.query.count()

    recent_sessions = LearningSession.query.order_by(LearningSession.created_at.desc()).limit(6).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(6).all()
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_skills=total_skills,
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        pending_reports=pending_reports,
        total_transactions=total_transactions,
        recent_sessions=recent_sessions,
        recent_users=recent_users,
        recent_reports=recent_reports
    )

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    search = request.args.get('search', '').strip()
    query = User.query
    if search:
        query = query.filter((User.full_name.ilike(f'%{search}%')) | (User.email.ilike(f'%{search}%')))
    all_users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users, search=search)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own admin account.', 'warning')
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    db.session.commit()
    status_str = 'activated' if user.is_active else 'suspended'
    flash(f"User {user.full_name} has been {status_str}.", 'info')
    return redirect(url_for('admin.users'))

@admin_bp.route('/skills', methods=['GET', 'POST'])
@login_required
@admin_required
def skills():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            name = request.form.get('skill_name', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            icon = request.form.get('icon', 'code').strip()

            if not name or not category:
                flash('Skill name and category are required.', 'warning')
            elif Skill.query.filter_by(skill_name=name).first():
                flash('Skill already exists.', 'warning')
            else:
                s = Skill(skill_name=name, category=category, description=description, icon=icon)
                db.session.add(s)
                db.session.commit()
                flash(f'Skill "{name}" created successfully.', 'success')

        elif action == 'delete':
            skill_id = request.form.get('skill_id', type=int)
            s = Skill.query.get(skill_id)
            if s:
                db.session.delete(s)
                db.session.commit()
                flash(f'Skill "{s.skill_name}" deleted.', 'info')

        return redirect(url_for('admin.skills'))

    all_skills = Skill.query.order_by(Skill.category, Skill.skill_name).all()
    categories = sorted(list(set(s.category for s in all_skills)))
    return render_template('admin/skills.html', skills=all_skills, categories=categories)

@admin_bp.route('/reports', methods=['GET', 'POST'])
@login_required
@admin_required
def reports():
    if request.method == 'POST':
        report_id = request.form.get('report_id', type=int)
        new_status = request.form.get('status')
        report = Report.query.get(report_id)
        if report and new_status in ['pending', 'reviewed', 'dismissed']:
            report.status = new_status
            db.session.commit()
            flash(f"Report status updated to {new_status}.", 'success')
        return redirect(url_for('admin.reports'))

    all_reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin/reports.html', reports=all_reports)

@admin_bp.route('/transactions')
@login_required
@admin_required
def transactions():
    all_txs = CreditTransaction.query.order_by(CreditTransaction.created_at.desc()).limit(100).all()
    return render_template('admin/transactions.html', transactions=all_txs)
