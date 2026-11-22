import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, csrf
from app.models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Context processors for global template variables
    @app.context_processor
    def inject_global_data():
        from flask_login import current_user
        from app.services.notification import NotificationService
        
        unread_notifs = 0
        recent_notifs = []
        if current_user.is_authenticated:
            unread_notifs = NotificationService.get_unread_count(current_user.id)
            recent_notifs = current_user.notifications.limit(5).all()
            
        return {
            'unread_notifications_count': unread_notifs,
            'recent_notifications': recent_notifs
        }

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.skills import skills_bp
    from app.routes.matching import matching_bp
    from app.routes.sessions import sessions_bp
    from app.routes.credits import credits_bp
    from app.routes.profile import profile_bp
    from app.routes.notifications import notifications_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(skills_bp, url_prefix='/skills')
    app.register_blueprint(matching_bp, url_prefix='/matching')
    app.register_blueprint(sessions_bp, url_prefix='/sessions')
    app.register_blueprint(credits_bp, url_prefix='/credits')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
