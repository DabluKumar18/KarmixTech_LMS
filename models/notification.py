"""
Notification Model - Handles user notifications
"""
from datetime import datetime
from models.user import db


class Notification(db.Model):
    """Notification model for user alerts and messages"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')  # info, success, warning, error
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Notification {self.title} for user {self.user_id}>'

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        db.session.commit()

    @staticmethod
    def create(user_id, title, message, notification_type='info', link=None):
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ActivityLog(db.Model):
    """Activity log for tracking user actions"""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('activity_logs', lazy='dynamic'))

    def __repr__(self):
        return f'<ActivityLog {self.action} by user {self.user_id}>'

    @staticmethod
    def log(user_id, action, details=None, ip_address=None, user_agent=None):
        """Create activity log entry"""
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
