from datetime import datetime
from extensions import db
from models.notification import Notification


def create_notification(user_id, title, message, notification_type='info', severity='info', link=None):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        severity=severity,
        link=link
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def get_user_notifications(user_id, unread_only=False, limit=50):
    query = Notification.query.filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


def mark_as_read(notification_id, user_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if notification:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
    return notification


def mark_all_as_read(user_id):
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
    db.session.commit()
    return len(notifications)


def get_unread_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()