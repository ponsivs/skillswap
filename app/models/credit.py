from datetime import datetime
from app.extensions import db

class CreditTransaction(db.Model):
    __tablename__ = 'credit_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False) # Positive (earned/bonus) or Negative (spent)
    balance_after = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False) # 'initial', 'earned_teaching', 'spent_learning', 'admin_adjustment', 'refund'
    session_id = db.Column(db.Integer, db.ForeignKey('learning_sessions.id', ondelete='SET NULL'), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    session = db.relationship('LearningSession', backref='credit_transactions', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'transaction_type': self.transaction_type,
            'session_id': self.session_id,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f"<CreditTransaction User:{self.user_id} {self.amount:+d} ({self.transaction_type})>"
