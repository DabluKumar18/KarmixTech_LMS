"""
Student Routes - Handles student dashboard and features
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

from models.user import db
from models.course import Course, Module, Lesson
from models.enrollment import Enrollment
from models.progress import Progress
from models.notification import Notification
from models.lesson_progress import LessonProgress, calculate_course_progress, update_enrollment_progress
from services.analytics import AnalyticsService
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService

student_bp = Blueprint('student', __name__)


def admin_required(func):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.is_admin:
            flash('Admin accounts cannot access student pages', 'warning')
            return redirect(url_for('admin.dashboard'))
        return func(*args, **kwargs)
    return decorated_view


@student_bp.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    stats = AnalyticsService.get_student_dashboard_stats(current_user.id)

    # Get recent notifications
    notifications = current_user.notifications.order_by(
        Notification.created_at.desc()
    ).limit(10).all()

    # Get in-progress courses
    in_progress = current_user.enrollments.filter_by(
        is_completed=False
    ).order_by(Enrollment.last_accessed.desc()).limit(5).all()

    # Get recommended courses
    enrolled_ids = [e.course_id for e in current_user.enrollments.all()]
    recommended = Course.query.filter(
        Course.id.notin_(enrolled_ids) if enrolled_ids else True,
        Course.is_published == True
    ).order_by(Course.created_at.desc()).limit(3).all()

    return render_template('student/dashboard.html',
                           stats=stats,
                           notifications=notifications,
                           in_progress=in_progress,
                           recommended=recommended)


@student_bp.route('/courses')
@student_bp.route('/courses/<int:page>')
@login_required
def browse_courses(page=1):
    """Browse all courses"""
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    level = request.args.get('level', '')

    query = CourseService.get_all_published(
        search=search,
        category=category if category != 'All' else None,
        level=level if level != 'All' else None
    )

    per_page = 12
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    categories = CourseService.get_categories()
    levels = CourseService.get_levels()

    return render_template('student/courses.html',
                           courses=pagination.items,
                           pagination=pagination,
                           categories=categories,
                           levels=levels,
                           search=search,
                           selected_category=category,
                           selected_level=level)


@student_bp.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    """Course details page"""
    course = CourseService.get_by_id(course_id)

    if not course:
        flash('Course not found', 'danger')
        return redirect(url_for('student.browse_courses'))

    is_enrolled = EnrollmentService.is_enrolled(current_user.id, course_id)
    enrollment = None

    if is_enrolled:
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()

    # Get modules with lesson counts
    modules_data = []
    for module in course.modules.order_by(Module.order):
        lessons = module.lessons.filter_by(is_published=True).order_by(Lesson.order).all()
        modules_data.append({
            'module': module,
            'lessons': lessons,
            'total_lessons': len(lessons)
        })

    # Get similar courses
    similar_courses = Course.query.filter(
        Course.category == course.category,
        Course.id != course.id,
        Course.is_published == True
    ).limit(3).all()

    return render_template('student/course_detail.html',
                           course=course,
                           enrollment=enrollment,
                           is_enrolled=is_enrolled,
                           modules_data=modules_data,
                           similar_courses=similar_courses)


@student_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll in a course"""
    enrollment, error = EnrollmentService.enroll(current_user.id, course_id)

    if error:
        flash(error, 'warning')
    else:
        flash('Successfully enrolled in course!', 'success')

    return redirect(url_for('student.course_detail', course_id=course_id))


@student_bp.route('/my-courses')
@login_required
def my_courses():
    """View enrolled courses"""
    enrollments = EnrollmentService.get_user_enrollments(current_user.id)

    # Group by status
    in_progress = [e for e in enrollments if not e.is_completed]
    completed = [e for e in enrollments if e.is_completed]

    return render_template('student/my_courses.html',
                           in_progress=in_progress,
                           completed=completed)


@student_bp.route('/learn/<int:course_id>')
@student_bp.route('/learn/<int:course_id>/lesson/<int:lesson_id>')
@login_required
def learn_course(course_id, lesson_id=None):
    """Learn/enrolled course view with lesson navigation"""
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        flash('Please enroll in this course first', 'warning')
        return redirect(url_for('student.course_detail', course_id=course_id))

    course = CourseService.get_by_id(course_id)

    # Get all published modules with their lessons
    modules_data = []
    all_lessons = []
    lesson_count = 0

    for module in course.modules.order_by(Module.order):
        lessons = list(module.lessons.filter_by(is_published=True).order_by(Lesson.order).all())
        modules_data.append({
            'module': module,
            'lessons': lessons
        })
        all_lessons.extend(lessons)
        lesson_count += len(lessons)

    # Determine current lesson
    current_lesson = None
    current_module = None

    if lesson_id:
        current_lesson = Lesson.query.get(lesson_id)
        if current_lesson:
            current_module = current_lesson.module
            # Verify lesson belongs to this course
            if current_module.course_id != course_id:
                current_lesson = None

    # If no lesson specified, find first lesson or last incomplete
    if not current_lesson and all_lessons:
        # Try to find first incomplete lesson
        for lesson in all_lessons:
            progress = LessonProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=lesson.id
            ).first()

            if not progress or not progress.is_completed:
                current_lesson = lesson
                current_module = lesson.module
                break

        # If all completed, show first lesson
        if not current_lesson:
            current_lesson = all_lessons[0]
            current_module = current_lesson.module

    # Get lesson progress
    lesson_progress = None
    if current_lesson:
        lesson_progress = LessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=current_lesson.id
        ).first()

    # Get next and previous lessons
    next_lesson = None
    prev_lesson = None

    if current_lesson and all_lessons:
        try:
            current_idx = all_lessons.index(current_lesson)
            if current_idx < len(all_lessons) - 1:
                next_lesson = all_lessons[current_idx + 1]
            if current_idx > 0:
                prev_lesson = all_lessons[current_idx - 1]
        except ValueError:
            pass

    # Get completed lessons count
    completed_lessons = LessonProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id,
        is_completed=True
    ).count()

    # Get all lesson progress for the sidebar
    lesson_progress_map = {}
    all_progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).all()
    for lp in all_progress:
        lesson_progress_map[lp.lesson_id] = lp

    # Update last accessed
    enrollment.last_accessed = datetime.utcnow()
    db.session.commit()

    return render_template('student/learn_enhanced.html',
                           course=course,
                           enrollment=enrollment,
                           modules_data=modules_data,
                           current_lesson=current_lesson,
                           current_module=current_module,
                           lesson_progress=lesson_progress,
                           next_lesson=next_lesson,
                           prev_lesson=prev_lesson,
                           all_lessons=all_lessons,
                           completed_lessons=completed_lessons,
                           total_lessons=len(all_lessons),
                           lesson_progress_map=lesson_progress_map)


@student_bp.route('/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def mark_lesson_completed(lesson_id):
    """Mark a lesson as completed and update course progress"""
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({'success': False, 'error': 'Lesson not found'}), 404

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=lesson.module.course_id
    ).first()

    if not enrollment:
        return jsonify({'success': False, 'error': 'Not enrolled'}), 403

    # Get or create lesson progress
    progress = LessonProgress.get_or_create(
        user_id=current_user.id,
        lesson_id=lesson_id,
        course_id=lesson.module.course_id
    )

    progress.is_completed = True
    progress.completed_at = datetime.utcnow()
    db.session.commit()

    # Update enrollment progress
    enrollment_updated = update_enrollment_progress(current_user.id, lesson.module.course_id)

    # Check if course is now complete
    if enrollment_updated and enrollment_updated.is_completed and enrollment_updated.completed_at:
        Notification.create(
            user_id=current_user.id,
            title='Course Completed!',
            message=f'Congratulations! You have completed {lesson.module.course.title}!',
            notification_type='success',
            link=url_for('student.my_courses')
        )

    return jsonify({
        'success': True,
        'lesson_id': lesson_id,
        'course_progress': enrollment.progress_percentage,
        'is_completed': enrollment.is_completed
    })


@student_bp.route('/lesson/<int:lesson_id>/progress', methods=['POST'])
@login_required
def update_lesson_progress(lesson_id):
    """Update lesson video progress"""
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({'success': False, 'error': 'Lesson not found'}), 404

    data = request.get_json() or {}
    video_position = data.get('video_position_seconds', 0)
    time_spent = data.get('time_spent_seconds', 0)

    progress = LessonProgress.get_or_create(
        user_id=current_user.id,
        lesson_id=lesson_id,
        course_id=lesson.module.course_id
    )

    if video_position:
        progress.video_position_seconds = video_position
    if time_spent:
        progress.time_spent_seconds = (progress.time_spent_seconds or 0) + time_spent

    db.session.commit()

    return jsonify({'success': True})


@student_bp.route('/certificate/<int:course_id>')
@login_required
def view_certificate(course_id):
    """View/download course completion certificate"""
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment or not enrollment.is_completed:
        flash('Certificate not available. Complete the course first.', 'warning')
        return redirect(url_for('student.my_courses'))

    course = Course.query.get(course_id)

    return render_template('student/certificate.html',
                           course=course,
                           enrollment=enrollment)


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Student profile page"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', '').strip()

        if first_name:
            current_user.first_name = first_name
        if last_name:
            current_user.last_name = last_name

        current_user.phone = phone
        current_user.bio = bio
        current_user.city = city
        current_user.country = country

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html')


@student_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not check_password_hash(current_user.password_hash, current_password):
            errors.append('Current password is incorrect')

        if len(new_password) < 8:
            errors.append('New password must be at least 8 characters')

        if not re.search(r'[A-Z]', new_password):
            errors.append('Password must contain uppercase letter')

        if not re.search(r'[a-z]', new_password):
            errors.append('Password must contain lowercase letter')

        if not re.search(r'[0-9]', new_password):
            errors.append('Password must contain a number')

        if new_password != confirm_password:
            errors.append('Passwords do not match')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('student/change_password.html')

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        # Notification
        Notification.create(
            user_id=current_user.id,
            title='Password Changed',
            message='Your password has been changed successfully.',
            notification_type='success'
        )

        flash('Password changed successfully', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/change_password.html')


@student_bp.route('/notifications')
@login_required
def notifications():
    """View all notifications"""
    page = request.args.get('page', 1, type=int)
    notifications = current_user.notifications.order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=20)

    return render_template('student/notifications.html',
                           notifications=notifications)


@student_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get(notification_id)

    if notification and notification.user_id == current_user.id:
        notification.mark_as_read()
        return jsonify({'success': True})

    return jsonify({'success': False}), 404


@student_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    current_user.notifications.update({'is_read': True})
    db.session.commit()

    flash('All notifications marked as read', 'success')
    return redirect(url_for('student.notifications'))


@student_bp.route('/progress/<int:course_id>')
@login_required
def view_progress(course_id):
    """View detailed progress for a course"""
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        flash('Not enrolled in this course', 'warning')
        return redirect(url_for('student.my_courses'))

    course = CourseService.get_by_id(course_id)

    # Get all lesson progress
    all_progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).all()

    progress_map = {p.lesson_id: p for p in all_progress}

    return render_template('student/progress.html',
                           course=course,
                           enrollment=enrollment,
                           progress_map=progress_map)
