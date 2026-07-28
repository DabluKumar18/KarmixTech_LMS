"""
Lesson Progress Model - Tracks individual lesson completion
"""
from datetime import datetime
from models.user import db


class LessonProgress(db.Model):
    """LessonProgress model for tracking individual lesson completion"""
    __tablename__ = 'lesson_progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    time_spent_seconds = db.Column(db.Integer, default=0)
    video_position_seconds = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint for user-lesson pair
    __table_args__ = (
        db.UniqueConstraint('user_id', 'lesson_id', name='unique_lesson_progress'),
    )

    def __repr__(self):
        return f'<LessonProgress user={self.user_id} lesson={self.lesson_id}>'

    def mark_completed(self):
        """Mark lesson as completed"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def update_time_spent(self, seconds):
        """Update time spent on lesson"""
        self.time_spent_seconds += seconds
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def update_video_position(self, seconds):
        """Update video playback position"""
        self.video_position_seconds = seconds
        db.session.commit()

    @staticmethod
    def get_or_create(user_id, lesson_id, course_id):
        """Get existing progress or create new record"""
        progress = LessonProgress.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()

        if not progress:
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                course_id=course_id
            )
            db.session.add(progress)
            db.session.commit()

        return progress

    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'course_id': self.course_id,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_spent_seconds': self.time_spent_seconds,
            'video_position_seconds': self.video_position_seconds
        }


def calculate_course_progress(user_id, course_id):
    """Calculate overall course progress percentage"""
    from models.course import Course

    course = Course.query.get(course_id)
    if not course:
        return 0

    total_lessons = course.total_lessons_count
    if total_lessons == 0:
        return 0

    completed_lessons = LessonProgress.query.filter_by(
        user_id=user_id,
        course_id=course_id,
        is_completed=True
    ).count()

    return round((completed_lessons / total_lessons) * 100, 1)


def update_enrollment_progress(user_id, course_id):
    """Update enrollment progress based on lesson completion"""
    from models.enrollment import Enrollment

    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()

    if enrollment:
        progress = calculate_course_progress(user_id, course_id)
        enrollment.progress_percentage = progress

        if progress >= 100:
            enrollment.is_completed = True
            enrollment.completed_at = datetime.utcnow()
        else:
            enrollment.is_completed = False
            enrollment.completed_at = None

        db.session.commit()

    return enrollment
