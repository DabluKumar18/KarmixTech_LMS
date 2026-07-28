"""
KarmixTech LMS - Main Application Entry Point
A comprehensive Learning Management System built with Flask
"""
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

from config import config
from models.user import User, db
from models.course import Course
from models.enrollment import Enrollment
from models.progress import Progress
from models.notification import Notification
from services.analytics import AnalyticsService
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService

# Initialize Flask app
app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'warning'

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Template filters
@app.template_filter('date_format')
def date_format(value, format='%b %d, %Y'):
    if value:
        return value.strftime(format)
    return ''


@app.template_filter('time_ago')
def time_ago(value):
    if not value:
        return ''
    now = datetime.utcnow()
    diff = now - value
    if diff.days > 365:
        return f"{diff.days // 365} year(s) ago"
    elif diff.days > 30:
        return f"{diff.days // 30} month(s) ago"
    elif diff.days > 0:
        return f"{diff.days} day(s) ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hour(s) ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minute(s) ago"
    return "Just now"


# Context processor
@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'app_name': 'KarmixTech LMS'
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')


# ============================================================================
# STUDENT ROUTES
# ============================================================================

from routes.student import student_bp
app.register_blueprint(student_bp, url_prefix='/student')


# ============================================================================
# ADMIN ROUTES
# ============================================================================

from routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')
from routes.admin_content import admin_content
app.register_blueprint(admin_content, url_prefix='/admin')


# ============================================================================
# API ROUTES
# ============================================================================

from api.courses import courses_api
from api.users import users_api
from api.enrollments import enrollments_api
from api.progress import progress_api

app.register_blueprint(courses_api, url_prefix='/api/courses')
app.register_blueprint(users_api, url_prefix='/api/users')
app.register_blueprint(enrollments_api, url_prefix='/api/enrollments')
app.register_blueprint(progress_api, url_prefix='/api/progress')


# ============================================================================
# INITIALIZE DATABASE
# ============================================================================

def create_admin_user():
    """Create default admin user if not exists"""
    admin = User.query.filter_by(email='admin@karmixtech.com').first()
    if not admin:
        admin = User(
            email='admin@karmixtech.com',
            password_hash=generate_password_hash('Admin@123'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            email_verified=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin@karmixtech.com / Admin@123")


def create_sample_courses():
    """Create sample courses if none exist"""
    if Course.query.count() == 0:
        admin = User.query.filter_by(role='admin').first()
        if admin:
            sample_courses = [
                {
                    'title': 'Python Programming Fundamentals',
                    'description': 'Learn Python from scratch. Cover variables, data types, control structures, functions, and OOP concepts. Perfect for beginners.',
                    'category': 'Programming',
                    'level': 'Beginner',
                    'duration_hours': 40,
                    'price': 0,
                    'instructor': 'Dr. Sarah Johnson',
                    'thumbnail': 'https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg?auto=compress&cs=tinysrgb&w=500'
                },
                {
                    'title': 'Web Development with HTML, CSS & JavaScript',
                    'description': 'Master modern web development. Learn to build responsive, interactive websites using the core technologies of the web.',
                    'category': 'Web Development',
                    'level': 'Beginner',
                    'duration_hours': 50,
                    'price': 0,
                    'instructor': 'Prof. Michael Chen',
                    'thumbnail': 'https://images.pexels.com/photos/11035422/pexels-photo-11035422.jpeg?auto=compress&cs=tinysrgb&w=500'
                },
                {
                    'title': 'Data Science with Python',
                    'description': 'Dive into data science. Learn data manipulation, visualization, statistical analysis, and machine learning basics.',
                    'category': 'Data Science',
                    'level': 'Intermediate',
                    'duration_hours': 60,
                    'price': 0,
                    'instructor': 'Dr. Emily Williams',
                    'thumbnail': 'https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=500'
                },
                {
                    'title': 'React.js Complete Guide',
                    'description': 'Build modern web applications with React. Learn components, hooks, state management, and build real projects.',
                    'category': 'Web Development',
                    'level': 'Intermediate',
                    'duration_hours': 45,
                    'price': 0,
                    'instructor': 'James Anderson',
                    'thumbnail': 'https://images.pexels.com/photos/4169359/pexels-photo-4169359.jpeg?auto=compress&cs=tinysrgb&w=500'
                },
                {
                    'title': 'Database Design & SQL Mastery',
                    'description': 'Master database design principles and SQL. Learn to create efficient databases, write complex queries, and optimize performance.',
                    'category': 'Database',
                    'level': 'Intermediate',
                    'duration_hours': 35,
                    'price': 0,
                    'instructor': 'Dr. Robert Miller',
                    'thumbnail': 'https://images.pexels.com/photos/577585/pexels-photo-577585.jpeg?auto=compress&cs=tinysrgb&w=500'
                },
                {
                    'title': 'Cloud Computing with AWS',
                    'description': 'Learn cloud fundamentals with AWS. Cover EC2, S3, Lambda, and deploy scalable applications in the cloud.',
                    'category': 'Cloud Computing',
                    'level': 'Advanced',
                    'duration_hours': 55,
                    'price': 0,
                    'instructor': 'Alex Thompson',
                    'thumbnail': 'https://images.pexels.com/photos/1148820/pexels-photo-1148820.jpeg?auto=compress&cs=tinysrgb&w=500'
                }
            ]

            for course_data in sample_courses:
                course = Course(created_by=admin.id, **course_data)
                db.session.add(course)

            db.session.commit()
            print(f"Created {len(sample_courses)} sample courses")


with app.app_context():
    try:
        db.create_all()
        create_admin_user()
        create_sample_courses()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
