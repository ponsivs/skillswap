from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    notification_type = db.Column(db.String(50), default='info') # 'session_request', 'session_accepted', 'session_completed', 'credit_update', 'review', 'system'
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'link': self.link or '#',
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%b %d, %H:%M')
        }

    def __repr__(self):
        return f"<Notification {self.id} for User {self.user_id}: {self.title}>"
