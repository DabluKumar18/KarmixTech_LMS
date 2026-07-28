"""
Progress Model - Handles lesson progress tracking
"""
from datetime import datetime
from models.user import db


class Progress(db.Model):
    """Progress model for tracking lesson completion"""
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    time_spent_minutes = db.Column(db.Integer, default=0)
    last_position = db.Column(db.Integer, default=0)  # Video position in seconds
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint for user-lesson pair
    __table_args__ = (
        db.UniqueConstraint('user_id', 'lesson_id', name='unique_progress'),
    )

    def __repr__(self):
        return f'<Progress user={self.user_id} lesson={self.lesson_id}>'

    def mark_completed(self):
        """Mark lesson as completed"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def update_time_spent(self, minutes):
        """Update time spent on lesson"""
        self.time_spent_minutes += minutes
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'lesson_id': self.lesson_id,
            'is_completed': self.is_completed,
            'time_spent_minutes': self.time_spent_minutes,
            'last_position': self.last_position,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
