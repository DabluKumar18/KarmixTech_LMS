"""
User Model - Handles user authentication and profile data
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    """User model for authentication and profile management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(255), default='default-avatar.png')
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    courses_created = db.relationship('Course', backref='creator', lazy='dynamic',
                                     foreign_keys='Course.created_by')
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic',
                                  cascade='all, delete-orphan')
    progress_records = db.relationship('Progress', backref='user', lazy='dynamic',
                                       cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='recipient', lazy='dynamic',
                                    cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_student(self):
        return self.role == 'student'

    def get_completed_courses_count(self):
        """Get count of completed courses"""
        return self.enrollments.filter_by(is_completed=True).count()

    def get_enrolled_courses_count(self):
        """Get count of enrolled courses"""
        return self.enrollments.count()

    def get_total_progress(self):
        """Calculate overall progress percentage"""
        enrollments = self.enrollments.all()
        if not enrollments:
            return 0
        total_progress = sum(e.progress_percentage for e in enrollments)
        return round(total_progress / len(enrollments), 1)

    def get_unread_notifications_count(self):
        """Get count of unread notifications"""
        return self.notifications.filter_by(is_read=False).count()

    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
