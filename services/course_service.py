"""
Course Service - Handles course-related operations
"""
from models.user import db
from models.course import Course, Module, Lesson
from datetime import datetime


class CourseService:
    """Service for course operations"""

    @staticmethod
    def get_all_published(search=None, category=None, level=None):
        """Get all published courses with optional filters"""
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

        return query.order_by(Course.created_at.desc())

    @staticmethod
    def get_by_id(course_id):
        """Get course by ID"""
        return Course.query.get(course_id)

    @staticmethod
    def get_by_slug(slug):
        """Get course by slug"""
        return Course.query.filter_by(slug=slug).first()

    @staticmethod
    def create(title, description, created_by, **kwargs):
        """Create a new course"""
        slug = Course.generate_slug(title)

        # Ensure unique slug
        existing = Course.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        course = Course(
            title=title,
            slug=slug,
            description=description,
            short_description=kwargs.get('short_description', description[:200]),
            category=kwargs.get('category', 'General'),
            level=kwargs.get('level', 'Beginner'),
            duration_hours=kwargs.get('duration_hours', 0),
            price=kwargs.get('price', 0),
            is_free=kwargs.get('is_free', True),
            thumbnail=kwargs.get('thumbnail'),
            instructor=kwargs.get('instructor'),
            language=kwargs.get('language', 'English'),
            requirements=kwargs.get('requirements'),
            what_you_learn=kwargs.get('what_you_learn'),
            created_by=created_by
        )

        db.session.add(course)
        db.session.commit()
        return course

    @staticmethod
    def update(course_id, **kwargs):
        """Update course details"""
        course = Course.query.get(course_id)
        if not course:
            return None

        for key, value in kwargs.items():
            if hasattr(course, key) and key not in ['id', 'created_by', 'created_at']:
                setattr(course, key, value)

        if 'title' in kwargs:
            course.slug = Course.generate_slug(kwargs['title'])

        db.session.commit()
        return course

    @staticmethod
    def delete(course_id):
        """Delete a course"""
        course = Course.query.get(course_id)
        if course:
            db.session.delete(course)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_categories():
        """Get all unique categories"""
        return [row[0] for row in db.session.query(
            Course.category
        ).distinct().all()]

    @staticmethod
    def get_levels():
        """Get all unique levels"""
        return ['Beginner', 'Intermediate', 'Advanced']
