"""
Models package initialization
"""
from models.user import User, db
from models.course import Course, Module, Lesson, CourseReview
from models.enrollment import Enrollment
from models.progress import Progress
from models.notification import Notification, ActivityLog
from models.lesson_progress import LessonProgress, calculate_course_progress, update_enrollment_progress

__all__ = [
    'db', 'User', 'Course', 'Module', 'Lesson', 'CourseReview',
    'Enrollment', 'Progress', 'Notification', 'ActivityLog',
    'LessonProgress', 'calculate_course_progress', 'update_enrollment_progress'
]
