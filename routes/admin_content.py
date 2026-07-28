"""
Admin Content Management Routes - Handles modules and lessons
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps

from models.user import db
from models.course import Course, Module, Lesson
from models.notification import Notification, ActivityLog

admin_content = Blueprint('admin_content', __name__)


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


# ============================================================================
# MODULE MANAGEMENT
# ============================================================================

@admin_content.route('/course/<int:course_id>/modules')
@login_required
@admin_required
def manage_modules(course_id):
    """Manage course modules"""
    course = Course.query.get_or_404(course_id)
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order).all()

    return render_template('admin/modules.html',
                           course=course,
                           modules=modules)


@admin_content.route('/course/<int:course_id>/modules/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_module(course_id):
    """Add new module"""
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        order = request.form.get('order', 0, type=int)
        is_preview = request.form.get('is_preview') == 'on'

        if not title:
            flash('Module title is required', 'danger')
            return render_template('admin/module_form.html', course=course)

        # Get max order if not specified
        if order == 0:
            max_order = db.session.query(db.func.max(Module.order)).filter_by(course_id=course_id).scalar()
            order = (max_order or 0) + 1

        module = Module(
            course_id=course_id,
            title=title,
            description=description,
            order=order,
            is_preview=is_preview
        )

        db.session.add(module)
        db.session.commit()

        ActivityLog.log(
            user_id=current_user.id,
            action='module_created',
            details=f'Created module: {module.title} in course: {course.title}'
        )

        flash('Module created successfully', 'success')
        return redirect(url_for('admin_content.manage_modules', course_id=course_id))

    return render_template('admin/module_form.html', course=course)


@admin_content.route('/module/<int:module_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_module(module_id):
    """Edit module"""
    module = Module.query.get_or_404(module_id)
    course = module.course

    if request.method == 'POST':
        module.title = request.form.get('title', '').strip()
        module.description = request.form.get('description', '').strip()
        module.order = request.form.get('order', module.order, type=int)
        module.is_preview = request.form.get('is_preview') == 'on'

        if not module.title:
            flash('Module title is required', 'danger')
        else:
            db.session.commit()

            ActivityLog.log(
                user_id=current_user.id,
                action='module_updated',
                details=f'Updated module: {module.title}'
            )

            flash('Module updated successfully', 'success')
            return redirect(url_for('admin_content.manage_modules', course_id=course.id))

    return render_template('admin/module_form.html', course=course, module=module)


@admin_content.route('/module/<int:module_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_module(module_id):
    """Delete module"""
    module = Module.query.get_or_404(module_id)
    course_id = module.course_id

    ActivityLog.log(
        user_id=current_user.id,
        action='module_deleted',
        details=f'Deleted module: {module.title}'
    )

    db.session.delete(module)
    db.session.commit()

    flash('Module deleted successfully', 'success')
    return redirect(url_for('admin_content.manage_modules', course_id=course_id))


@admin_content.route('/module/<int:module_id>/reorder', methods=['POST'])
@login_required
@admin_required
def reorder_module(module_id):
    """Reorder module"""
    module = Module.query.get_or_404(module_id)
    direction = request.form.get('direction')

    if direction == 'up':
        prev_module = Module.query.filter_by(course_id=module.course_id).filter(
            Module.order < module.order
        ).order_by(Module.order.desc()).first()

        if prev_module:
            module.order, prev_module.order = prev_module.order, module.order
            db.session.commit()

    elif direction == 'down':
        next_module = Module.query.filter_by(course_id=module.course_id).filter(
            Module.order > module.order
        ).order_by(Module.order.asc()).first()

        if next_module:
            module.order, next_module.order = next_module.order, module.order
            db.session.commit()

    return redirect(url_for('admin_content.manage_modules', course_id=module.course_id))


# ============================================================================
# LESSON MANAGEMENT
# ============================================================================

@admin_content.route('/module/<int:module_id>/lessons')
@login_required
@admin_required
def manage_lessons(module_id):
    """Manage module lessons"""
    module = Module.query.get_or_404(module_id)
    lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()

    return render_template('admin/lessons.html',
                           module=module,
                           course=module.course,
                           lessons=lessons)


@admin_content.route('/module/<int:module_id>/lessons/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lesson(module_id):
    """Add new lesson"""
    module = Module.query.get_or_404(module_id)
    course = module.course

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        video_url = request.form.get('video_url', '').strip()
        pdf_url = request.form.get('pdf_url', '').strip()
        duration_minutes = request.form.get('duration_minutes', 0, type=int)
        order = request.form.get('order', 0, type=int)
        is_preview = request.form.get('is_preview') == 'on'
        is_published = request.form.get('is_published') == 'on'

        if not title:
            flash('Lesson title is required', 'danger')
            return render_template('admin/lesson_form.html', module=module, course=course)

        # Extract YouTube video ID
        youtube_video_id = Lesson.extract_youtube_id(video_url) if video_url else None

        # Get max order if not specified
        if order == 0:
            max_order = db.session.query(db.func.max(Lesson.order)).filter_by(module_id=module_id).scalar()
            order = (max_order or 0) + 1

        lesson = Lesson(
            module_id=module_id,
            title=title,
            description=description,
            content=content,
            video_url=video_url,
            youtube_video_id=youtube_video_id,
            pdf_url=pdf_url,
            duration_minutes=duration_minutes,
            order=order,
            is_preview=is_preview,
            is_published=is_published
        )

        db.session.add(lesson)
        db.session.commit()

        # Update module duration
        module.duration_minutes = module.total_duration_minutes
        db.session.commit()

        ActivityLog.log(
            user_id=current_user.id,
            action='lesson_created',
            details=f'Created lesson: {lesson.title} in module: {module.title}'
        )

        flash('Lesson created successfully', 'success')
        return redirect(url_for('admin_content.manage_lessons', module_id=module_id))

    return render_template('admin/lesson_form.html', module=module, course=course)


@admin_content.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lesson(lesson_id):
    """Edit lesson"""
    lesson = Lesson.query.get_or_404(lesson_id)
    module = lesson.module
    course = module.course

    if request.method == 'POST':
        lesson.title = request.form.get('title', '').strip()
        lesson.description = request.form.get('description', '').strip()
        lesson.content = request.form.get('content', '').strip()
        lesson.video_url = request.form.get('video_url', '').strip()
        lesson.pdf_url = request.form.get('pdf_url', '').strip()
        lesson.duration_minutes = request.form.get('duration_minutes', 0, type=int)
        lesson.order = request.form.get('order', lesson.order, type=int)
        lesson.is_preview = request.form.get('is_preview') == 'on'
        lesson.is_published = request.form.get('is_published') == 'on'

        # Update YouTube video ID
        lesson.youtube_video_id = Lesson.extract_youtube_id(lesson.video_url) if lesson.video_url else None

        if not lesson.title:
            flash('Lesson title is required', 'danger')
        else:
            db.session.commit()

            # Update module duration
            module.duration_minutes = module.total_duration_minutes
            db.session.commit()

            ActivityLog.log(
                user_id=current_user.id,
                action='lesson_updated',
                details=f'Updated lesson: {lesson.title}'
            )

            flash('Lesson updated successfully', 'success')
            return redirect(url_for('admin_content.manage_lessons', module_id=module.id))

    return render_template('admin/lesson_form.html', module=module, course=course, lesson=lesson)


@admin_content.route('/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lesson(lesson_id):
    """Delete lesson"""
    lesson = Lesson.query.get_or_404(lesson_id)
    module_id = lesson.module_id
    module = lesson.module

    ActivityLog.log(
        user_id=current_user.id,
        action='lesson_deleted',
        details=f'Deleted lesson: {lesson.title}'
    )

    db.session.delete(lesson)
    db.session.commit()

    # Update module duration
    module.duration_minutes = module.total_duration_minutes
    db.session.commit()

    flash('Lesson deleted successfully', 'success')
    return redirect(url_for('admin_content.manage_lessons', module_id=module_id))


@admin_content.route('/lesson/<int:lesson_id>/reorder', methods=['POST'])
@login_required
@admin_required
def reorder_lesson(lesson_id):
    """Reorder lesson"""
    lesson = Lesson.query.get_or_404(lesson_id)
    direction = request.form.get('direction')

    if direction == 'up':
        prev_lesson = Lesson.query.filter_by(module_id=lesson.module_id).filter(
            Lesson.order < lesson.order
        ).order_by(Lesson.order.desc()).first()

        if prev_lesson:
            lesson.order, prev_lesson.order = prev_lesson.order, lesson.order
            db.session.commit()

    elif direction == 'down':
        next_lesson = Lesson.query.filter_by(module_id=lesson.module_id).filter(
            Lesson.order > lesson.order
        ).order_by(Lesson.order.asc()).first()

        if next_lesson:
            lesson.order, next_lesson.order = next_lesson.order, lesson.order
            db.session.commit()

    return redirect(url_for('admin_content.manage_lessons', module_id=lesson.module_id))


@admin_content.route('/lesson/<int:lesson_id>/toggle-publish', methods=['POST'])
@login_required
@admin_required
def toggle_lesson_publish(lesson_id):
    """Toggle lesson publish status"""
    lesson = Lesson.query.get_or_404(lesson_id)
    lesson.is_published = not lesson.is_published
    db.session.commit()

    status = 'published' if lesson.is_published else 'unpublished'
    flash(f'Lesson {status} successfully', 'success')
    return redirect(url_for('admin_content.manage_lessons', module_id=lesson.module_id))


# ============================================================================
# API ENDPOINTS
# ============================================================================

@admin_content.route('/api/course/<int:course_id>/modules')
@login_required
@admin_required
def api_get_modules(course_id):
    """Get modules for a course (JSON)"""
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order).all()
    return jsonify({
        'modules': [m.to_dict() for m in modules]
    })


@admin_content.route('/api/module/<int:module_id>/lessons')
@login_required
@admin_required
def api_get_lessons(module_id):
    """Get lessons for a module (JSON)"""
    lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
    return jsonify({
        'lessons': [l.to_dict() for l in lessons]
    })
