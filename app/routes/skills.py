from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.skill import Skill, UserSkill
from app.models.user import User

skills_bp = Blueprint('skills', __name__)

@skills_bp.route('/explore')
def explore():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    level = request.args.get('level', '').strip()
    mode = request.args.get('mode', 'all') # 'all', 'teach', 'learn'

    skills_query = Skill.query

    if query:
        skills_query = skills_query.filter(
            (Skill.skill_name.ilike(f'%{query}%')) | 
            (Skill.description.ilike(f'%{query}%'))
        )

    if category and category != 'All':
        skills_query = skills_query.filter_by(category=category)

    skills = skills_query.order_by(Skill.category, Skill.skill_name).all()

    # Available categories
    all_categories = sorted(list(set(s[0] for s in db.session.query(Skill.category).distinct())))

    # Enhance skills with top mentors
    enhanced_skills = []
    for s in skills:
        teachers = UserSkill.query.filter_by(skill_id=s.id, skill_type='teach').all()
        # Filter out current user if logged in
        if current_user.is_authenticated:
            teachers = [t for t in teachers if t.user_id != current_user.id]

        enhanced_skills.append({
            'skill': s,
            'teachers': [t.user for t in teachers[:3] if t.user and t.user.is_active],
            'total_teachers': len(teachers)
        })

    return render_template(
        'skills/explore.html',
        enhanced_skills=enhanced_skills,
        categories=all_categories,
        selected_category=category,
        query=query,
        selected_level=level,
        selected_mode=mode
    )

@skills_bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if request.method == 'POST':
        action = request.form.get('action')
        skill_id = request.form.get('skill_id', type=int)
        skill_type = request.form.get('skill_type', 'learn')
        proficiency = request.form.get('proficiency_level', 'Beginner')
        notes = request.form.get('notes', '').strip()

        if action == 'add':
            if not skill_id:
                flash('Please select a skill.', 'warning')
                return redirect(url_for('skills.manage'))

            existing = UserSkill.query.filter_by(
                user_id=current_user.id,
                skill_id=skill_id,
                skill_type=skill_type
            ).first()

            if existing:
                flash('This skill is already in your profile.', 'info')
            else:
                progress = 100 if skill_type == 'teach' else 15
                new_skill = UserSkill(
                    user_id=current_user.id,
                    skill_id=skill_id,
                    skill_type=skill_type,
                    proficiency_level=proficiency,
                    progress_percentage=progress,
                    notes=notes
                )
                db.session.add(new_skill)
                db.session.commit()
                flash('Skill added to your profile!', 'success')

        elif action == 'remove':
            user_skill_id = request.form.get('user_skill_id', type=int)
            if user_skill_id:
                us = UserSkill.query.filter_by(id=user_skill_id, user_id=current_user.id).first()
                if us:
                    db.session.delete(us)
                    db.session.commit()
                    flash('Skill removed from your profile.', 'info')

        return redirect(url_for('skills.manage'))

    all_skills = Skill.query.order_by(Skill.category, Skill.skill_name).all()
    user_skills = UserSkill.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'skills/manage.html',
        all_skills=all_skills,
        user_skills=user_skills
    )

@skills_bp.route('/map')
@login_required
def map_view():
    return render_template('skills/map.html')

@skills_bp.route('/api/map-data')
@login_required
def map_data():
    """
    Returns nodes and edges for the Personalised Interactive Skill Map.
    Includes:
    - Root / Category nodes
    - Skill nodes: Can Teach, Learning, Want to Learn / Goals, Completed
    - Relationships and progress percentages
    """
    user_skills = UserSkill.query.filter_by(user_id=current_user.id).all()
    
    categories = {}
    nodes = [
        {
            'id': 'user_center',
            'label': current_user.full_name,
            'type': 'center',
            'radius': 30,
            'color': '#4338CA',
            'subtitle': 'Student Skill Hub'
        }
    ]
    links = []

    for us in user_skills:
        cat = us.skill.category
        if cat not in categories:
            cat_id = f"cat_{cat.replace(' ', '_').replace('&', 'and')}"
            categories[cat] = cat_id
            nodes.append({
                'id': cat_id,
                'label': cat,
                'type': 'category',
                'radius': 22,
                'color': '#7C3AED'
            })
            links.append({'source': 'user_center', 'target': cat_id, 'strength': 0.8})

        # Node color based on status
        if us.skill_type == 'teach':
            color = '#16A34A' # Green (Can Teach)
            status_label = 'Can Teach'
        elif us.skill_type == 'completed' or us.progress_percentage >= 100:
            color = '#0D9488' # Teal (Completed)
            status_label = 'Mastered / Completed'
        elif us.skill_type == 'learn':
            color = '#2563EB' # Blue (Learning)
            status_label = f"Learning ({us.progress_percentage}%)"
        else:
            color = '#F59E0B' # Amber (Interested / Goal)
            status_label = 'Future Learning Goal'

        node_id = f"skill_{us.id}"
        nodes.append({
            'id': node_id,
            'label': us.skill.skill_name,
            'category': cat,
            'type': 'skill',
            'skill_type': us.skill_type,
            'proficiency': us.proficiency_level,
            'progress': us.progress_percentage,
            'radius': 16,
            'color': color,
            'status_label': status_label,
            'notes': us.notes or '',
            'description': us.skill.description or ''
        })
        links.append({'source': categories[cat], 'target': node_id, 'strength': 0.5})

    return jsonify({
        'nodes': nodes,
        'links': links,
        'student_name': current_user.full_name,
        'stats': {
            'teach': len(current_user.teaching_skills),
            'learning': len(current_user.learning_skills),
            'completed': len(current_user.completed_skills),
        }
    })

@skills_bp.route('/api/update-progress', methods=['POST'])
@login_required
def update_progress():
    data = request.get_json() or {}
    user_skill_id = data.get('user_skill_id')
    new_progress = data.get('progress')

    if not user_skill_id or new_progress is None:
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    us = UserSkill.query.filter_by(id=user_skill_id, user_id=current_user.id).first()
    if not us:
        return jsonify({'success': False, 'message': 'Skill not found'}), 404

    us.progress_percentage = max(0, min(100, int(new_progress)))
    if us.progress_percentage >= 100 and us.skill_type == 'learn':
        us.skill_type = 'completed'
    db.session.commit()

    return jsonify({'success': True, 'progress': us.progress_percentage, 'skill_type': us.skill_type})
