from datetime import datetime
from app.extensions import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('learning_sessions.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1 to 5 stars
    feedback = db.Column(db.Text, nullable=False)
    learning_outcome = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('session_id', 'reviewer_id', name='uq_session_reviewer'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'reviewer': self.reviewer.full_name if self.reviewer else 'Student',
            'reviewer_avatar': self.reviewer.avatar_url if self.reviewer else None,
            'reviewee': self.reviewee.full_name if self.reviewee else 'Student',
            'rating': self.rating,
            'feedback': self.feedback,
            'learning_outcome': self.learning_outcome or '',
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

    def __repr__(self):
        return f"<Review {self.id}: {self.rating} stars from {self.reviewer_id} to {self.reviewee_id}>"
