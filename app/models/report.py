from datetime import datetime
from app.extensions import db

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reason = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='pending') # 'pending', 'resolved', 'dismissed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_filed')
    reported_user = db.relationship('User', foreign_keys=[reported_user_id], backref='reports_received')

    def to_dict(self):
        return {
            'id': self.id,
            'reporter': self.reporter.full_name if self.reporter else 'Anonymous',
            'reported_user': self.reported_user.full_name if self.reported_user else 'Unknown',
            'reason': self.reason,
            'details': self.details or '',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f"<Report {self.id}: {self.reason} against User {self.reported_user_id}>"
