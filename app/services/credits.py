"""
Credit Exchange & Transaction Ledger Service
Ensures ACID transaction guarantees for credit balances:
- Earn 5 credits per completed teaching session
- Spend 5 credits per completed learning session
- Update learning skill progress percentage
"""
from app.extensions import db
from app.models.user import User
from app.models.skill import UserSkill
from app.models.session import LearningSession
from app.models.credit import CreditTransaction
from app.services.notification import NotificationService

class CreditService:
    DEFAULT_SESSION_CREDITS = 5

    @staticmethod
    def can_request_session(user_id, required_credits=5):
        user = User.query.get(user_id)
        if not user:
            return False, "User not found."
        if user.credits_balance < required_credits:
            return False, f"Insufficient credits. You need {required_credits} credits to book, but currently have {user.credits_balance}. Teach a peer to earn credits!"
        return True, "Credits verified."

    @staticmethod
    def complete_session(session_id, completed_by_user_id):
        session = LearningSession.query.get(session_id)
        if not session:
            return False, "Session not found."

        if session.status == 'completed':
            return False, "Session has already been marked as completed."

        if completed_by_user_id not in (session.teacher_id, session.learner_id):
            return False, "Unauthorized to update this session."

        teacher = User.query.get(session.teacher_id)
        learner = User.query.get(session.learner_id)

        if not teacher or not learner:
            return False, "Session participants could not be found."

        credit_amount = session.credits_amount or CreditService.DEFAULT_SESSION_CREDITS

        # Verify learner has enough balance to spend
        if learner.credits_balance < credit_amount:
            return False, f"Learner has insufficient credits ({learner.credits_balance} available, {credit_amount} required)."

        try:
            # 1. Update session status
            session.status = 'completed'

            # 2. Credit Teacher (+amount)
            teacher.credits_balance += credit_amount
            tx_teacher = CreditTransaction(
                user_id=teacher.id,
                amount=credit_amount,
                balance_after=teacher.credits_balance,
                transaction_type='earned_teaching',
                session_id=session.id,
                description=f"Earned for teaching {session.skill.skill_name} to {learner.full_name}"
            )
            db.session.add(tx_teacher)

            # 3. Debit Learner (-amount)
            learner.credits_balance -= credit_amount
            tx_learner = CreditTransaction(
                user_id=learner.id,
                amount=-credit_amount,
                balance_after=learner.credits_balance,
                transaction_type='spent_learning',
                session_id=session.id,
                description=f"Spent for learning {session.skill.skill_name} from {teacher.full_name}"
            )
            db.session.add(tx_learner)

            # 4. Progress Learner's skill
            learner_skill = UserSkill.query.filter_by(
                user_id=learner.id,
                skill_id=session.skill_id
            ).first()

            if learner_skill:
                learner_skill.progress_percentage = min(100, (learner_skill.progress_percentage or 0) + 25)
                if learner_skill.progress_percentage >= 100:
                    learner_skill.skill_type = 'completed'
            else:
                learner_skill = UserSkill(
                    user_id=learner.id,
                    skill_id=session.skill_id,
                    skill_type='learn',
                    proficiency_level='Beginner',
                    progress_percentage=25,
                    notes='Started through peer learning session'
                )
                db.session.add(learner_skill)

            db.session.commit()

            # 5. Dispatch in-app notifications
            NotificationService.create(
                user_id=teacher.id,
                title="Credits Earned! (+5)",
                message=f"Session with {learner.full_name} for {session.skill.skill_name} completed. You received {credit_amount} credits!",
                link="/credits",
                notification_type="credit_update"
            )

            NotificationService.create(
                user_id=learner.id,
                title="Session Completed & Progress Updated",
                message=f"Your learning session with {teacher.full_name} for {session.skill.skill_name} is complete. Your skill progress increased!",
                link=f"/skills/map",
                notification_type="session_completed"
            )

            return True, "Session marked completed. Credits and skill progress updated successfully."

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to complete session: {str(e)}"
