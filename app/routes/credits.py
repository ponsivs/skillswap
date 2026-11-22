from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.credit import CreditTransaction

credits_bp = Blueprint('credits', __name__)

@credits_bp.route('/')
@login_required
def index():
    transactions = CreditTransaction.query.filter_by(
        user_id=current_user.id
    ).order_by(CreditTransaction.created_at.desc()).all()

    total_earned = sum(t.amount for t in transactions if t.amount > 0)
    total_spent = abs(sum(t.amount for t in transactions if t.amount < 0))

    return render_template(
        'credits/index.html',
        transactions=transactions,
        total_earned=total_earned,
        total_spent=total_spent,
        balance=current_user.credits_balance
    )
