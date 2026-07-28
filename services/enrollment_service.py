"""
Enrollment Service - Handles enrollment-related operations
"""
from models.user import db
from models.course import Course
from models.enrollment import Enrollment
from models.progress import Progress
from models.notification import Notification
from datetime import datetime


class EnrollmentService:
    """Service for enrollment operations"""

    @staticmethod
    def enroll(user_id, course_id):
        """Enroll a student in a course"""
        # Check if already enrolled
        existing = Enrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()

        if existing:
            return None, "Already enrolled in this course"

        # Create enrollment
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            enrolled_at=datetime.utcnow(),
            progress_percentage=0.0
        )

        db.session.add(enrollment)

        # Create notification
        course = Course.query.get(course_id)
        Notification.create(
            user_id=user_id,
            title="Course Enrollment Successful",
            message=f"You have successfully enrolled in {course.title}",
            notification_type='success',
            link=f"/student/course/{course_id}"
        )

        db.session.commit()
        return enrollment, None

    @staticmethod
    def unenroll(user_id, course_id):
        """Unenroll a student from a course"""
        enrollment = Enrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()

        if enrollment:
            db.session.delete(enrollment)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_enrollments(user_id):
        """Get all enrollments for a user"""
        return Enrollment.query.filter_by(user_id=user_id).order_by(
            Enrollment.enrolled_at.desc()
        ).all()

    @staticmethod
    def get_course_enrollments(course_id):
        """Get all enrollments for a course"""
        return Enrollment.query.filter_by(course_id=course_id).order_by(
            Enrollment.enrolled_at.desc()
        ).all()

    @staticmethod
    def is_enrolled(user_id, course_id):
        """Check if user is enrolled in course"""
        return Enrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first() is not None

    @staticmethod
    def update_progress(user_id, course_id, lesson_id=None, progress_percentage=None):
        """Update enrollment progress"""
        enrollment = Enrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()

        if enrollment:
            if progress_percentage is not None:
                enrollment.update_progress(progress_percentage)

            if lesson_id:
                # Update lesson progress
                progress = Progress.query.filter_by(
                    user_id=user_id,
                    lesson_id=lesson_id
                ).first()

                if progress:
                    progress.mark_completed()

                    # Calculate overall course progress
                    course = Course.query.get(course_id)
                    total_lessons = course.modules.join(Lesson).count()
                    completed_lessons = Progress.query.filter_by(
                        user_id=user_id,
                        course_id=course_id,
                        is_completed=True
                    ).count()

                    if total_lessons > 0:
                        new_percentage = (completed_lessons / total_lessons) * 100
                        enrollment.update_progress(new_percentage)

            db.session.commit()
            return enrollment

        return None

    @staticmethod
    def get_enrollment_stats(course_id):
        """Get enrollment statistics for a course"""
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()

        total = len(enrollments)
        completed = sum(1 for e in enrollments if e.is_completed)
        avg_progress = sum(e.progress_percentage for e in enrollments) / total if total > 0 else 0

        return {
            'total_enrolled': total,
            'completed': completed,
            'in_progress': total - completed,
            'average_progress': round(avg_progress, 1)
        }
