import unittest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.session import LearningSession
from app.models.credit import CreditTransaction
from app.services.matching import MatchingEngine
from app.services.credits import CreditService

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret'
    WTF_CSRF_ENABLED = False

class SkillSwapTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration_and_password_hashing(self):
        """Test secure registration and password verification."""
        user = User(
            full_name="Test Student",
            email="test@university.edu",
            institution="Stanford",
            credits_balance=15
        )
        user.set_password("SecurePassword123!")
        db.session.add(user)
        db.session.commit()

        self.assertTrue(user.check_password("SecurePassword123!"))
        self.assertFalse(user.check_password("WrongPassword"))
        self.assertEqual(user.credits_balance, 15)

    def test_reciprocal_matching_engine(self):
        """Test rule-based reciprocal matching between Student A and Student B."""
        # Create Skills
        py = Skill(skill_name="Python", category="Programming & Technology")
        ui = Skill(skill_name="UI/UX Design", category="Design & Creativity")
        db.session.add_all([py, ui])
        db.session.commit()

        # Student A: teaches Python, learns UI/UX
        student_a = User(full_name="Student A", email="a@test.edu", credits_balance=15)
        student_a.set_password("pass")
        db.session.add(student_a)
        db.session.commit()

        db.session.add_all([
            UserSkill(user_id=student_a.id, skill_id=py.id, skill_type="teach", proficiency_level="Advanced"),
            UserSkill(user_id=student_a.id, skill_id=ui.id, skill_type="learn", proficiency_level="Beginner")
        ])

        # Student B: teaches UI/UX, learns Python
        student_b = User(full_name="Student B", email="b@test.edu", credits_balance=15)
        student_b.set_password("pass")
        db.session.add(student_b)
        db.session.commit()

        db.session.add_all([
            UserSkill(user_id=student_b.id, skill_id=ui.id, skill_type="teach", proficiency_level="Advanced"),
            UserSkill(user_id=student_b.id, skill_id=py.id, skill_type="learn", proficiency_level="Beginner")
        ])
        db.session.commit()

        matches = MatchingEngine.get_matches_for_user(student_a.id)
        self.assertTrue(len(matches) > 0)
        top_match = matches[0]
        self.assertEqual(top_match['user'].id, student_b.id)
        self.assertTrue(top_match['reciprocal'])
        self.assertGreaterEqual(top_match['compatibility_score'], 80)
        self.assertIn("Python", top_match['you_can_teach'])
        self.assertIn("UI/UX Design", top_match['can_teach_you'])

    def test_credit_exchange_and_progress_update(self):
        """Test credit debit from learner, credit add to teacher, and skill progress update."""
        from datetime import datetime

        skill = Skill(skill_name="Python", category="Tech")
        db.session.add(skill)
        db.session.commit()

        teacher = User(full_name="Teacher", email="teach@test.edu", credits_balance=10)
        learner = User(full_name="Learner", email="learn@test.edu", credits_balance=10)
        teacher.set_password("pass")
        learner.set_password("pass")
        db.session.add_all([teacher, learner])
        db.session.commit()

        # Learner has Python at 20%
        us_learner = UserSkill(
            user_id=learner.id,
            skill_id=skill.id,
            skill_type='learn',
            progress_percentage=20
        )
        db.session.add(us_learner)
        db.session.commit()

        # Create session
        session = LearningSession(
            teacher_id=teacher.id,
            learner_id=learner.id,
            skill_id=skill.id,
            session_date=datetime.utcnow(),
            duration_minutes=45,
            status='accepted',
            credits_amount=5
        )
        db.session.add(session)
        db.session.commit()

        # Complete session via CreditService
        success, msg = CreditService.complete_session(session.id, teacher.id)
        self.assertTrue(success)

        # Teacher should have 10 + 5 = 15 credits
        # Learner should have 10 - 5 = 5 credits
        self.assertEqual(teacher.credits_balance, 15)
        self.assertEqual(learner.credits_balance, 5)

        # Learner's progress should have increased by 25% (20 + 25 = 45%)
        db.session.refresh(us_learner)
        self.assertEqual(us_learner.progress_percentage, 45)

        # Check Credit Transactions
        txs = CreditTransaction.query.filter_by(session_id=session.id).all()
        self.assertEqual(len(txs), 2)

    def test_insufficient_credits_prevention(self):
        """Test that a student with 0 credits cannot request a session requiring 5 credits."""
        broke_user = User(full_name="Broke Student", email="broke@test.edu", credits_balance=2)
        broke_user.set_password("pass")
        db.session.add(broke_user)
        db.session.commit()

        can_request, msg = CreditService.can_request_session(broke_user.id, 5)
        self.assertFalse(can_request)
        self.assertIn("Insufficient credits", msg)

if __name__ == '__main__':
    unittest.main()
