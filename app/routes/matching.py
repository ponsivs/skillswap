from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.services.matching import MatchingEngine

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/')
@login_required
def index():
    filter_type = request.args.get('type', 'all') # 'all', 'reciprocal', 'one_way'
    all_matches = MatchingEngine.get_matches_for_user(current_user.id, limit=30)

    if filter_type == 'reciprocal':
        filtered = [m for m in all_matches if m.get('reciprocal')]
    elif filter_type == 'one_way':
        filtered = [m for m in all_matches if not m.get('reciprocal')]
    else:
        filtered = all_matches

    reciprocal_count = len([m for m in all_matches if m.get('reciprocal')])
    one_way_count = len(all_matches) - reciprocal_count

    return render_template(
        'matching/index.html',
        matches=filtered,
        filter_type=filter_type,
        reciprocal_count=reciprocal_count,
        one_way_count=one_way_count,
        total_matches=len(all_matches)
    )
