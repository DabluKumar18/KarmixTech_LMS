"""
Analytics Service - Handles dashboard statistics and analytics
"""
from datetime import datetime, timedelta
from models.user import db, User
from models.course import Course
from models.enrollment import Enrollment
from models.progress import Progress
from models.notification import Notification


class AnalyticsService:
    """Service for generating analytics and statistics"""

    @staticmethod
    def get_admin_dashboard_stats():
        """Get comprehensive admin dashboard statistics"""
        total_students = User.query.filter_by(role='student').count()
        total_courses = Course.query.filter_by(is_published=True).count()
        total_enrollments = Enrollment.query.count()
        completed_enrollments = Enrollment.query.filter_by(is_completed=True).count()

        # Recent activity
        last_30_days = datetime.utcnow() - timedelta(days=30)
        new_students = User.query.filter(
            User.role == 'student',
            User.created_at >= last_30_days
        ).count()
        new_enrollments = Enrollment.query.filter(
            Enrollment.enrolled_at >= last_30_days
        ).count()

        return {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'completed_enrollments': completed_enrollments,
            'new_students_last_30_days': new_students,
            'new_enrollments_last_30_days': new_enrollments
        }

    @staticmethod
    def get_student_dashboard_stats(user_id):
        """Get student dashboard statistics"""
        student = User.query.get(user_id)
        total_enrolled = student.enrollments.count()
        completed = student.enrollments.filter_by(is_completed=True).count()
        in_progress = total_enrolled - completed
        total_progress = student.get_total_progress()

        # Recent activity
        recent_enrollments = student.enrollments.order_by(
            Enrollment.enrolled_at.desc()
        ).limit(5).all()

        return {
            'total_enrolled': total_enrolled,
            'completed': completed,
            'in_progress': in_progress,
            'overall_progress': total_progress,
            'recent_enrollments': recent_enrollments
        }

    @staticmethod
    def get_enrollment_trend(days=30):
        """Get enrollment trend data for charts"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        enrollments = Enrollment.query.filter(
            Enrollment.enrolled_at.between(start_date, end_date)
        ).all()

        # Group by date
        trend_data = {}
        for enrollment in enrollments:
            date_str = enrollment.enrolled_at.strftime('%Y-%m-%d')
            trend_data[date_str] = trend_data.get(date_str, 0) + 1

        return trend_data

    @staticmethod
    def get_popular_courses(limit=5):
        """Get most popular courses by enrollment count"""
        courses = Course.query.outerjoin(Enrollment).group_by(Course.id).order_by(
            db.func.count(Enrollment.id).desc()
        ).limit(limit).all()

        return courses

    @staticmethod
    def get_category_distribution():
        """Get course distribution by category"""
        result = db.session.query(
            Course.category,
            db.func.count(Course.id).label('count')
        ).group_by(Course.category).all()

        return {row.category: row.count for row in result}

    @staticmethod
    def get_course_completion_rate(course_id):
        """Calculate course completion rate"""
        total = Enrollment.query.filter_by(course_id=course_id).count()
        completed = Enrollment.query.filter_by(
            course_id=course_id, is_completed=True
        ).count()

        return (completed / total * 100) if total > 0 else 0
