"""
Courses API - REST endpoints for courses
"""
from flask import Blueprint, jsonify, request
from models.user import db
from models.course import Course, Module, Lesson
from services.course_service import CourseService

courses_api = Blueprint('courses_api', __name__)


@courses_api.route('/', methods=['GET'])
def get_courses():
    """Get all courses with optional filters"""
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    level = request.args.get('level', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Course.query.filter_by(is_published=True)

    if search:
        query = query.filter(
            db.or_(
                Course.title.ilike(f'%{search}%'),
                Course.description.ilike(f'%{search}%')
            )
        )

    if category:
        query = query.filter_by(category=category)

    if level:
        query = query.filter_by(level=level)

    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'courses': [course.to_dict() for course in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@courses_api.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get course details"""
    course = CourseService.get_by_id(course_id)

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    course_data = course.to_dict()
    course_data['modules'] = []

    for module in course.modules.order_by(Module.order):
        module_data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'order': module.order,
            'lessons': []
        }

        for lesson in module.lessons.order_by(Lesson.order):
            module_data['lessons'].append({
                'id': lesson.id,
                'title': lesson.title,
                'duration_minutes': lesson.duration_minutes,
                'is_preview': lesson.is_preview
            })

        course_data['modules'].append(module_data)

    return jsonify(course_data)


@courses_api.route('/<int:course_id>/stats', methods=['GET'])
def get_course_stats(course_id):
    """Get course enrollment statistics"""
    from services.enrollment_service import EnrollmentService

    course = Course.query.get(course_id)

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    stats = EnrollmentService.get_enrollment_stats(course_id)

    return jsonify({
        'course_id': course_id,
        'course_title': course.title,
        **stats
    })


@courses_api.route('/categories', methods=['GET'])
def get_categories():
    """Get all course categories"""
    categories = CourseService.get_categories()
    return jsonify({'categories': categories})


@courses_api.route('/levels', methods=['GET'])
def get_levels():
    """Get all course levels"""
    levels = CourseService.get_levels()
    return jsonify({'levels': levels})


@courses_api.route('/popular', methods=['GET'])
def get_popular_courses():
    """Get most popular courses"""
    from services.analytics import AnalyticsService

    limit = request.args.get('limit', 5, type=int)
    courses = AnalyticsService.get_popular_courses(limit)

    return jsonify({
        'courses': [course.to_dict() for course in courses]
    })


@courses_api.route('/by-slug/<slug>', methods=['GET'])
def get_course_by_slug(slug):
    """Get course by slug"""
    course = CourseService.get_by_slug(slug)

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    return jsonify(course.to_dict())
