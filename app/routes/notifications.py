from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.notification import Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/')
@login_required
def index():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications/index.html', notifications=notifications)

@notifications_bp.route('/read/<int:notif_id>')
@login_required
def mark_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
        if notif.link and notif.link != '#':
            return redirect(notif.link)
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.index'))
