from datetime import datetime
from app.extensions import db

class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    learner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False, index=True)
    
    session_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=45, nullable=False)
    status = db.Column(db.String(30), default='pending', nullable=False, index=True)
    # statuses: 'pending', 'accepted', 'rejected', 'completed', 'cancelled'
    
    credits_amount = db.Column(db.Integer, default=5, nullable=False)
    notes = db.Column(db.Text, nullable=True) # Learner request note or agenda
    meeting_link = db.Column(db.String(255), nullable=True) # Jitsi / internal room / video call URL
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    reviews = db.relationship('Review', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'learner': self.learner.to_dict() if self.learner else None,
            'skill': self.skill.to_dict() if self.skill else None,
            'session_date': self.session_date.strftime('%Y-%m-%d %H:%M'),
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'credits_amount': self.credits_amount,
            'notes': self.notes or '',
            'meeting_link': self.meeting_link or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f"<LearningSession {self.id}: Teacher {self.teacher_id} -> Learner {self.learner_id} ({self.status})>"
