"""
Admin Routes - Handles admin dashboard and management
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from functools import wraps

from models.user import db, User
from models.course import Course
from models.enrollment import Enrollment
from models.progress import Progress
from models.notification import Notification, ActivityLog
from services.analytics import AnalyticsService
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.admin_login'))
        if not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    stats = AnalyticsService.get_admin_dashboard_stats()

    # Get enrollment trend (last 30 days)
    trend_data = AnalyticsService.get_enrollment_trend(30)

    # Popular courses
    popular_courses = AnalyticsService.get_popular_courses(5)

    # Recent enrollments
    recent_enrollments = Enrollment.query.order_by(
        Enrollment.enrolled_at.desc()
    ).limit(10).all()

    # Recent students
    recent_students = User.query.filter_by(role='student').order_by(
        User.created_at.desc()
    ).limit(5).all()

    # Category distribution
    category_data = AnalyticsService.get_category_distribution()

    # Activity logs
    activity_logs = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           trend_data=trend_data,
                           popular_courses=popular_courses,
                           recent_enrollments=recent_enrollments,
                           recent_students=recent_students,
                           category_data=category_data,
                           activity_logs=activity_logs)


@admin_bp.route('/courses')
@login_required
@admin_required
def manage_courses():
    """Manage courses page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Course.query

    if search:
        query = query.filter(
            db.or_(
                Course.title.ilike(f'%{search}%'),
                Course.category.ilike(f'%{search}%')
            )
        )

    courses = query.order_by(Course.created_at.desc()).paginate(
        page=page, per_page=10
    )

    return render_template('admin/courses.html',
                           courses=courses,
                           search=search)


@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    """Add new course"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        level = request.form.get('level', 'Beginner')
        duration_hours = request.form.get('duration_hours', 0, type=int)
        price = request.form.get('price', 0, type=float)
        instructor = request.form.get('instructor', '').strip()
        language = request.form.get('language', 'English')
        requirements = request.form.get('requirements', '').strip()
        what_you_learn = request.form.get('what_you_learn', '').strip()
        thumbnail = request.form.get('thumbnail', '')
        is_published = request.form.get('is_published') == 'on'
        is_free = price == 0

        errors = []

        if not title:
            errors.append('Title is required')
        if not description:
            errors.append('Description is required')
        if not category:
            errors.append('Category is required')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/course_form.html')

        course = CourseService.create(
            title=title,
            description=description,
            created_by=current_user.id,
            category=category,
            level=level,
            duration_hours=duration_hours,
            price=price,
            is_free=is_free,
            instructor=instructor,
            language=language,
            requirements=requirements,
            what_you_learn=what_you_learn,
            thumbnail=thumbnail or 'https://images.pexels.com/photos/5905485/pexels-photo-5905485.jpeg?auto=compress&cs=tinysrgb&w=500'
        )

        course.is_published = is_published
        db.session.commit()

        # Log activity
        ActivityLog.log(
            user_id=current_user.id,
            action='course_created',
            details=f'Created course: {course.title}'
        )

        flash('Course created successfully', 'success')
        return redirect(url_for('admin.manage_courses'))

    categories = CourseService.get_categories()
    levels = CourseService.get_levels()

    return render_template('admin/course_form.html',
                           categories=categories,
                           levels=levels)


@admin_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    """Edit course"""
    course = CourseService.get_by_id(course_id)

    if not course:
        flash('Course not found', 'danger')
        return redirect(url_for('admin.manage_courses'))

    if request.method == 'POST':
        update_data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category': request.form.get('category', '').strip(),
            'level': request.form.get('level', 'Beginner'),
            'duration_hours': request.form.get('duration_hours', 0, type=int),
            'price': request.form.get('price', 0, type=float),
            'instructor': request.form.get('instructor', '').strip(),
            'language': request.form.get('language', 'English'),
            'requirements': request.form.get('requirements', '').strip(),
            'what_you_learn': request.form.get('what_you_learn', '').strip(),
            'thumbnail': request.form.get('thumbnail', ''),
            'is_published': request.form.get('is_published') == 'on',
            'is_free': request.form.get('price', 0, type=float) == 0
        }

        if not update_data['title']:
            flash('Title is required', 'danger')
        else:
            CourseService.update(course_id, **update_data)

            ActivityLog.log(
                user_id=current_user.id,
                action='course_updated',
                details=f'Updated course: {course.title}'
            )

            flash('Course updated successfully', 'success')
            return redirect(url_for('admin.manage_courses'))

    categories = CourseService.get_categories()
    levels = CourseService.get_levels()

    return render_template('admin/course_form.html',
                           course=course,
                           categories=categories,
                           levels=levels)


@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    """Delete course"""
    course = CourseService.get_by_id(course_id)

    if course:
        ActivityLog.log(
            user_id=current_user.id,
            action='course_deleted',
            details=f'Deleted course: {course.title}'
        )

        CourseService.delete(course_id)
        flash('Course deleted successfully', 'success')
    else:
        flash('Course not found', 'danger')

    return redirect(url_for('admin.manage_courses'))


@admin_bp.route('/students')
@login_required
@admin_required
def manage_students():
    """Manage students page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = User.query.filter_by(role='student')

    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )

    students = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=15
    )

    return render_template('admin/students.html',
                           students=students,
                           search=search)


@admin_bp.route('/students/<int:student_id>')
@login_required
@admin_required
def student_detail(student_id):
    """View student details"""
    student = User.query.get(student_id)

    if not student or student.role != 'student':
        flash('Student not found', 'danger')
        return redirect(url_for('admin.manage_students'))

    enrollments = student.enrollments.all()

    return render_template('admin/student_detail.html',
                           student=student,
                           enrollments=enrollments)


@admin_bp.route('/students/toggle-status/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def toggle_student_status(student_id):
    """Toggle student active status"""
    student = User.query.get(student_id)

    if not student or student.role != 'student':
        flash('Student not found', 'danger')
        return redirect(url_for('admin.manage_students'))

    student.is_active = not student.is_active
    db.session.commit()

    status = 'activated' if student.is_active else 'deactivated'
    flash(f'Student account {status}', 'success')

    return redirect(url_for('admin.manage_students'))


@admin_bp.route('/enrollments')
@login_required
@admin_required
def manage_enrollments():
    """Manage enrollments page"""
    page = request.args.get('page', 1, type=int)
    course_filter = request.args.get('course', '', type=int)

    query = Enrollment.query

    if course_filter:
        query = query.filter_by(course_id=course_filter)

    enrollments = query.order_by(Enrollment.enrolled_at.desc()).paginate(
        page=page, per_page=20
    )

    courses = Course.query.all()

    return render_template('admin/enrollments.html',
                           enrollments=enrollments,
                           courses=courses,
                           course_filter=course_filter)


@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """Detailed statistics page"""
    stats = AnalyticsService.get_admin_dashboard_stats()

    # Monthly enrollment data
    months_data = []
    for i in range(12):
        date = datetime.utcnow() - timedelta(days=30 * i)
        start = date.replace(day=1, hour=0, minute=0, second=0)
        if date.month == 12:
            end = date.replace(year=date.year + 1, month=1, day=1)
        else:
            end = date.replace(month=date.month + 1, day=1)

        count = Enrollment.query.filter(
            Enrollment.enrolled_at >= start,
            Enrollment.enrolled_at < end
        ).count()

        months_data.append({
            'month': date.strftime('%b %Y'),
            'count': count
        })

    months_data.reverse()

    # Course completion rates
    courses = Course.query.all()
    completion_rates = []
    for course in courses:
        rate = AnalyticsService.get_course_completion_rate(course.id)
        completion_rates.append({
            'course': course.title,
            'rate': rate,
            'enrolled': course.enrolled_students_count
        })

    return render_template('admin/statistics.html',
                           stats=stats,
                           months_data=months_data,
                           completion_rates=completion_rates)


@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Admin settings page"""
    return render_template('admin/settings.html')


@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """Get dashboard stats as JSON"""
    stats = AnalyticsService.get_admin_dashboard_stats()
    return jsonify(stats)
