"""
Enrollments API - REST endpoints for enrollments
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from models.user import db
from models.course import Course
from models.enrollment import Enrollment
from models.notification import Notification
from services.enrollment_service import EnrollmentService

enrollments_api = Blueprint('enrollments_api', __name__)


@enrollments_api.route('/', methods=['GET'])
@login_required
def get_enrollments():
    """Get current user's enrollments"""
    enrollments = EnrollmentService.get_user_enrollments(current_user.id)

    return jsonify({
        'enrollments': [e.to_dict() for e in enrollments],
        'total': len(enrollments)
    })


@enrollments_api.route('/', methods=['POST'])
@login_required
def create_enrollment():
    """Enroll in a course"""
    data = request.get_json()

    if not data or 'course_id' not in data:
        return jsonify({'error': 'Course ID is required'}), 400

    course_id = data['course_id']

    # Check course exists
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    enrollment, error = EnrollmentService.enroll(current_user.id, course_id)

    if error:
        return jsonify({'error': error}), 400

    return jsonify({
        'message': 'Enrollment successful',
        'enrollment': enrollment.to_dict()
    }), 201


@enrollments_api.route('/<int:enrollment_id>', methods=['GET'])
@login_required
def get_enrollment(enrollment_id):
    """Get enrollment details"""
    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    if enrollment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(enrollment.to_dict())


@enrollments_api.route('/<int:enrollment_id>', methods=['DELETE'])
@login_required
def delete_enrollment(enrollment_id):
    """Unenroll from a course"""
    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    if enrollment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    course_id = enrollment.course_id
    db.session.delete(enrollment)
    db.session.commit()

    # Create notification
    course = Course.query.get(course_id)
    Notification.create(
        user_id=current_user.id,
        title='Course Unenrolled',
        message=f'You have been unenrolled from {course.title}',
        notification_type='info'
    )

    return jsonify({'message': 'Unenrolled successfully'})


@enrollments_api.route('/check/<int:course_id>', methods=['GET'])
@login_required
def check_enrollment(course_id):
    """Check if enrolled in a course"""
    is_enrolled = EnrollmentService.is_enrolled(current_user.id, course_id)

    return jsonify({
        'is_enrolled': is_enrolled,
        'course_id': course_id
    })


@enrollments_api.route('/student/<int:user_id>', methods=['GET'])
@login_required
def get_student_enrollments(user_id):
    """Get all enrollments for a student (admin only)"""
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    enrollments = EnrollmentService.get_user_enrollments(user_id)

    return jsonify({
        'enrollments': [e.to_dict() for e in enrollments],
        'total': len(enrollments)
    })


@enrollments_api.route('/course/<int:course_id>', methods=['GET'])
@login_required
def get_course_enrollments_api(course_id):
    """Get all enrollments for a course (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    enrollments = EnrollmentService.get_course_enrollments(course_id)

    return jsonify({
        'enrollments': [e.to_dict() for e in enrollments],
        'total': len(enrollments)
    })
