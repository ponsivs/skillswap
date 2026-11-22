from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.credit import CreditTransaction
from app.services.notification import NotificationService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        institution = request.form.get('institution', '').strip()
        education_level = request.form.get('education_level', 'Undergraduate')
        terms = request.form.get('terms')

        # Form Validations
        if not terms:
            flash('Please accept the Terms of Service to register.', 'warning')
            return render_template('auth/register.html')

        if not full_name or not email or not password:
            flash('Please fill in all required fields.', 'warning')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'warning')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'info')
            return redirect(url_for('auth.login'))

        # Create new student account with starting welcome credits
        user = User(
            full_name=full_name,
            email=email,
            institution=institution,
            education_level=education_level,
            credits_balance=15,
            avatar_url=f"https://api.dicebear.com/7.x/initials/svg?seed={full_name}",
            is_onboarded=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Log initial welcome credit transaction
        tx = CreditTransaction(
            user_id=user.id,
            amount=15,
            balance_after=15,
            transaction_type='initial',
            description='Welcome credit bonus for joining SkillSwap'
        )
        db.session.add(tx)

        # Welcome notification
        NotificationService.create(
            user_id=user.id,
            title="Welcome to SkillSwap!",
            message="Your account has been created with 15 free starter credits. Complete onboarding to discover skill partners!",
            link="/auth/onboarding",
            notification_type="system"
        )
        db.session.commit()

        login_user(user)
        flash('Account created successfully! Welcome to SkillSwap.', 'success')
        return redirect(url_for('auth.onboarding'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('This account has been deactivated. Please contact support.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')

        next_page = request.args.get('next')
        if not user.is_onboarded and user.role != 'admin':
            return redirect(url_for('auth.onboarding'))
        return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    skills = Skill.query.order_by(Skill.category, Skill.skill_name).all()
    categories = sorted(list(set(s.category for s in skills)))

    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()
        institution = request.form.get('institution', '').strip()
        availability = request.form.get('availability', 'Weekday Evenings & Weekends')
        
        teach_skill_ids = request.form.getlist('teach_skills')
        learn_skill_ids = request.form.getlist('learn_skills')

        current_user.bio = bio or current_user.bio
        current_user.institution = institution or current_user.institution
        current_user.availability = availability
        current_user.is_onboarded = True

        # Clear existing and add selected skills
        UserSkill.query.filter_by(user_id=current_user.id).delete()

        # Add teaching skills
        for sid in teach_skill_ids:
            try:
                skill_id = int(sid)
                level = request.form.get(f'teach_level_{skill_id}', 'Intermediate')
                db.session.add(UserSkill(
                    user_id=current_user.id,
                    skill_id=skill_id,
                    skill_type='teach',
                    proficiency_level=level,
                    progress_percentage=100
                ))
            except ValueError:
                pass

        # Add learning skills
        for sid in learn_skill_ids:
            try:
                skill_id = int(sid)
                level = request.form.get(f'learn_level_{skill_id}', 'Beginner')
                db.session.add(UserSkill(
                    user_id=current_user.id,
                    skill_id=skill_id,
                    skill_type='learn',
                    proficiency_level=level,
                    progress_percentage=10
                ))
            except ValueError:
                pass

        db.session.commit()
        flash('Onboarding complete! Your personalized skill map is now active.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/onboarding.html', skills=skills, categories=categories)
