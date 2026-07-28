"""
Progress API - REST endpoints for progress tracking
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime

from models.user import db
from models.course import Course, Lesson
from models.enrollment import Enrollment
from models.progress import Progress
from services.enrollment_service import EnrollmentService

progress_api = Blueprint('progress_api', __name__)


@progress_api.route('/<int:course_id>', methods=['GET'])
@login_required
def get_course_progress(course_id):
    """Get user's progress for a course"""
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 404

    progress_records = Progress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).all()

    return jsonify({
        'course_id': course_id,
        'enrollment': enrollment.to_dict(),
        'progress': [p.to_dict() for p in progress_records],
        'overall_progress': enrollment.progress_percentage,
        'is_completed': enrollment.is_completed
    })


@progress_api.route('/<int:course_id>/lesson/<int:lesson_id>', methods=['POST'])
@login_required
def mark_lesson_completed(course_id, lesson_id):
    """Mark a lesson as completed"""
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 404

    # Check lesson exists in course
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404

    # Get or create progress record
    progress = Progress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()

    if not progress:
        progress = Progress(
            user_id=current_user.id,
            course_id=course_id,
            lesson_id=lesson_id
        )
        db.session.add(progress)

    progress.is_completed = True
    progress.completed_at = datetime.utcnow()

    db.session.commit()

    # Calculate course progress
    course = Course.query.get(course_id)
    total_lessons = sum(m.lessons.count() for m in course.modules.all())

    completed_lessons = Progress.query.filter(
        Progress.user_id == current_user.id,
        Progress.course_id == course_id,
        Progress.is_completed == True
    ).count()

    if total_lessons > 0:
        new_percentage = (completed_lessons / total_lessons) * 100
        enrollment.update_progress(new_percentage)

    return jsonify({
        'message': 'Lesson marked as completed',
        'lesson_id': lesson_id,
        'course_progress': enrollment.progress_percentage,
        'is_course_completed': enrollment.is_completed
    })


@progress_api.route('/<int:course_id>/time', methods=['POST'])
@login_required
def update_time_spent(course_id):
    """Update time spent on course"""
    data = request.get_json()

    if not data or 'minutes' not in data:
        return jsonify({'error': 'Minutes required'}), 400

    minutes = data['minutes']

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 404

    lesson_id = data.get('lesson_id')

    if lesson_id:
        progress = Progress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()

        if progress:
            progress.update_time_spent(minutes)

    enrollment.last_accessed = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Time updated successfully'})


@progress_api.route('/<int:course_id>/video-position/<int:lesson_id>', methods=['POST'])
@login_required
def update_video_position(course_id, lesson_id):
    """Update video position for a lesson"""
    data = request.get_json()

    if not data or 'position' not in data:
        return jsonify({'error': 'Position required'}), 400

    position = data['position']

    progress = Progress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()

    if not progress:
        return jsonify({'error': 'Progress not found'}), 404

    progress.last_position = position
    db.session.commit()

    return jsonify({
        'message': 'Position updated',
        'position': position
    })


@progress_api.route('/overall', methods=['GET'])
@login_required
def get_overall_progress():
    """Get overall learning progress"""
    total_enrolled = current_user.enrollments.count()
    completed = current_user.enrollments.filter_by(is_completed=True).count()
    in_progress = total_enrolled - completed

    total_time = sum(
        p.time_spent_minutes for p in current_user.progress_records.all()
    )

    return jsonify({
        'total_enrolled': total_enrolled,
        'completed': completed,
        'in_progress': in_progress,
        'total_time_minutes': total_time,
        'average_progress': current_user.get_total_progress()
    })
