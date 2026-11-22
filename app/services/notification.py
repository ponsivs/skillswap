from app.extensions import db
from app.models.notification import Notification

class NotificationService:
    @staticmethod
    def create(user_id, title, message, link=None, notification_type='info'):
        try:
            notif = Notification(
                user_id=user_id,
                title=title,
                message=message,
                link=link,
                notification_type=notification_type,
                is_read=False
            )
            db.session.add(notif)
            db.session.commit()
            return notif
        except Exception:
            db.session.rollback()
            return None

    @staticmethod
    def get_unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
