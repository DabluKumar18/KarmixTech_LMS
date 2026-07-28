"""
Course Model - Handles course data and content
"""
from datetime import datetime
from models.user import db


class Course(db.Model):
    """Course model for managing course information"""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(300))
    category = db.Column(db.String(50), nullable=False, index=True)
    level = db.Column(db.String(20), default='Beginner')
    duration_hours = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    is_free = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=True)
    thumbnail = db.Column(db.String(255))
    instructor = db.Column(db.String(100))
    language = db.Column(db.String(20), default='English')
    requirements = db.Column(db.Text)
    what_you_learn = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic',
                                  cascade='all, delete-orphan')
    modules = db.relationship('Module', backref='course', lazy='dynamic',
                              cascade='all, delete-orphan',
                              order_by='Module.order')
    progress_records = db.relationship('Progress', backref='course', lazy='dynamic',
                                        cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.title}>'

    @property
    def enrolled_students_count(self):
        """Get count of enrolled students"""
        return self.enrollments.count()

    @property
    def modules_count(self):
        """Get count of modules"""
        return self.modules.count()

    @property
    def total_lessons_count(self):
        """Get total count of all lessons across all modules"""
        total = 0
        for module in self.modules:
            total += module.lessons.count()
        return total

    @property
    def total_duration_minutes(self):
        """Get total duration of all lessons"""
        total = 0
        for module in self.modules:
            for lesson in module.lessons:
                total += lesson.duration_minutes or 0
        return total

    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @staticmethod
    def generate_slug(title):
        """Generate URL-friendly slug from title"""
        import re
        slug = title.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = re.sub(r'^-+|-+$', '', slug)
        return slug

    def to_dict(self):
        """Convert course to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'duration_hours': self.duration_hours,
            'price': self.price,
            'is_free': self.is_free,
            'instructor': self.instructor,
            'enrolled_students': self.enrolled_students_count,
            'thumbnail': self.thumbnail,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Module(db.Model):
    """Module model for course sections/lessons"""
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer, default=0)
    is_preview = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy='dynamic',
                              cascade='all, delete-orphan',
                              order_by='Lesson.order')

    def __repr__(self):
        return f'<Module {self.title}>'

    @property
    def lessons_count(self):
        """Get count of lessons in this module"""
        return self.lessons.count()

    @property
    def total_duration_minutes(self):
        """Get total duration of all lessons"""
        return sum(l.duration_minutes or 0 for l in self.lessons)

    def to_dict(self):
        """Convert module to dictionary"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'lessons_count': self.lessons_count,
            'lessons': [l.to_dict() for l in self.lessons.order_by(Lesson.order)]
        }


class Lesson(db.Model):
    """Lesson model for individual lessons within modules"""
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    youtube_video_id = db.Column(db.String(50))
    pdf_url = db.Column(db.String(500))
    duration_minutes = db.Column(db.Integer, default=0)
    order = db.Column(db.Integer, default=0)
    is_preview = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress_records = db.relationship('LessonProgress', backref='lesson', lazy='dynamic',
                                        cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Lesson {self.title}>'

    @staticmethod
    def extract_youtube_id(url):
        """Extract YouTube video ID from various URL formats"""
        if not url:
            return None

        import re

        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'^([a-zA-Z0-9_-]{11})$'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    @property
    def embedded_video_url(self):
        """Get embedded YouTube URL"""
        if self.youtube_video_id:
            return f'https://www.youtube.com/embed/{self.youtube_video_id}'
        return None

    def to_dict(self):
        """Convert lesson to dictionary"""
        return {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'video_url': self.video_url,
            'youtube_video_id': self.youtube_video_id,
            'pdf_url': self.pdf_url,
            'order': self.order,
            'is_preview': self.is_preview,
            'is_published': self.is_published
        }


class CourseReview(db.Model):
    """Course review model for student feedback"""
    __tablename__ = 'course_reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', backref=db.backref('reviews', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('reviews', lazy='dynamic'))

    def __repr__(self):
        return f'<CourseReview by {self.user_id} for course {self.course_id}>'
