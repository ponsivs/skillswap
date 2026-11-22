from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    institution = db.Column(db.String(180), nullable=True)
    education_level = db.Column(db.String(80), nullable=True) # Undergraduate, Postgraduate, High School, etc.
    bio = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(30), default='student', nullable=False) # 'student', 'admin'
    credits_balance = db.Column(db.Integer, default=15, nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    availability = db.Column(db.String(150), default='Weekday Evenings & Weekends')
    learning_interests = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_onboarded = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_skills = db.relationship('UserSkill', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sessions_teaching = db.relationship('LearningSession', foreign_keys='LearningSession.teacher_id', backref='teacher', lazy='dynamic')
    sessions_learning = db.relationship('LearningSession', foreign_keys='LearningSession.learner_id', backref='learner', lazy='dynamic')
    credit_transactions = db.relationship('CreditTransaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan', order_by='Notification.created_at.desc()')
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', backref='reviewee', lazy='dynamic')
    reviews_written = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def teaching_skills(self):
        return [us for us in self.user_skills if us.skill_type == 'teach']

    @property
    def learning_skills(self):
        return [us for us in self.user_skills if us.skill_type in ('learn', 'interested')]

    @property
    def completed_skills(self):
        return [us for us in self.user_skills if us.skill_type == 'completed' or us.progress_percentage >= 100]

    @property
    def average_rating(self):
        reviews = self.reviews_received.all()
        if not reviews:
            return 5.0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def completed_sessions_count(self):
        taught = self.sessions_teaching.filter_by(status='completed').count()
        learned = self.sessions_learning.filter_by(status='completed').count()
        return taught + learned

    @property
    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'full_name': self.full_name,
            'institution': self.institution or 'SkillSwap Member',
            'education_level': self.education_level or 'Student',
            'bio': self.bio or '',
            'role': self.role,
            'avatar_url': self.avatar_url or f"https://api.dicebear.com/7.x/initials/svg?seed={self.full_name}",
            'availability': self.availability,
            'credits_balance': self.credits_balance,
            'completed_sessions': self.completed_sessions_count,
            'average_rating': self.average_rating,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }
        if include_private:
            data['email'] = self.email
            data['is_onboarded'] = self.is_onboarded
        return data

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
