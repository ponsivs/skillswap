from datetime import datetime
from app.extensions import db

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='book-open') # Lucide icon name
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_skills = db.relationship('UserSkill', backref='skill', lazy='dynamic', cascade='all, delete-orphan')
    sessions = db.relationship('LearningSession', backref='skill', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'category': self.category,
            'description': self.description or '',
            'icon': self.icon,
            'teachers_count': self.user_skills.filter_by(skill_type='teach').count(),
            'learners_count': self.user_skills.filter(UserSkill.skill_type.in_(['learn', 'interested'])).count()
        }

    def __repr__(self):
        return f"<Skill {self.skill_name} ({self.category})>"


class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_type = db.Column(db.String(30), nullable=False) # 'teach', 'learn', 'completed', 'interested'
    proficiency_level = db.Column(db.String(30), default='Intermediate') # 'Beginner', 'Intermediate', 'Advanced', 'Master'
    progress_percentage = db.Column(db.Integer, default=0) # 0 to 100
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'skill_id', 'skill_type', name='uq_user_skill_type'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.skill_name if self.skill else '',
            'category': self.skill.category if self.skill else '',
            'skill_type': self.skill_type,
            'proficiency_level': self.proficiency_level,
            'progress_percentage': self.progress_percentage,
            'notes': self.notes or ''
        }

    def __repr__(self):
        return f"<UserSkill User:{self.user_id} Skill:{self.skill_id} ({self.skill_type})>"
