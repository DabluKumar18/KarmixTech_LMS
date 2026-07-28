"""
Enrollment Model - Handles student course enrollments
"""
from datetime import datetime
from models.user import db


class Enrollment(db.Model):
    """Enrollment model for tracking student course registrations"""
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    progress_percentage = db.Column(db.Float, default=0.0)
    last_accessed = db.Column(db.DateTime)
    certificate_issued = db.Column(db.Boolean, default=False)
    certificate_url = db.Column(db.String(255))

    # Unique constraint for user-course pair
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='unique_enrollment'),
    )

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'

    def update_progress(self, percentage):
        """Update enrollment progress"""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        if self.progress_percentage >= 100:
            self.is_completed = True
            self.completed_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """Convert enrollment to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'course_title': self.course.title if self.course else None,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'is_completed': self.is_completed,
            'progress_percentage': self.progress_percentage,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }
