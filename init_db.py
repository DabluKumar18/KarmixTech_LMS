"""
Database initialization script
Run this script to seed the database with initial data
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import app, db
from models.user import User
from models.course import Course
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()

        # Create admin user
        admin = User.query.filter_by(email='admin@karmixtech.com').first()
        if not admin:
            print("Creating admin user...")
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
            print("Admin user created: admin@karmixtech.com / Admin@123")
        else:
            print("Admin user already exists")

        # Create sample courses
        if Course.query.count() == 0:
            print("Creating sample courses...")
            sample_courses = [
                {
                    'title': 'Python Programming Fundamentals',
                    'slug': 'python-programming-fundamentals',
                    'description': 'Learn Python from scratch. Cover variables, data types, control structures, functions, and OOP concepts.',
                    'short_description': 'Master Python basics and build a strong programming foundation',
                    'category': 'Programming',
                    'level': 'Beginner',
                    'duration_hours': 40,
                    'price': 0,
                    'is_free': True,
                    'instructor': 'Dr. Sarah Johnson',
                    'thumbnail': 'https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg?auto=compress&cs=tinysrgb&w=500',
                    'created_by': admin.id
                },
                {
                    'title': 'Web Development with HTML, CSS & JavaScript',
                    'slug': 'web-development-html-css-javascript',
                    'description': 'Master modern web development. Learn to build responsive, interactive websites using the core technologies of the web.',
                    'short_description': 'Build modern, responsive websites from scratch',
                    'category': 'Web Development',
                    'level': 'Beginner',
                    'duration_hours': 50,
                    'price': 0,
                    'is_free': True,
                    'instructor': 'Prof. Michael Chen',
                    'thumbnail': 'https://images.pexels.com/photos/11035422/pexels-photo-11035422.jpeg?auto=compress&cs=tinysrgb&w=500',
                    'created_by': admin.id
                },
                {
                    'title': 'Data Science with Python',
                    'slug': 'data-science-python',
                    'description': 'Dive into data science. Learn data manipulation, visualization, statistical analysis, and machine learning basics.',
                    'short_description': 'Analyze data and build predictive models',
                    'category': 'Data Science',
                    'level': 'Intermediate',
                    'duration_hours': 60,
                    'price': 0,
                    'is_free': True,
                    'instructor': 'Dr. Emily Williams',
                    'thumbnail': 'https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=500',
                    'created_by': admin.id
                }
            ]

            for course_data in sample_courses:
                course = Course(**course_data)
                db.session.add(course)

            db.session.commit()
            print(f"Created {len(sample_courses)} sample courses")
        else:
            print("Courses already exist")

        print("\nDatabase initialization complete!")
        print("=" * 50)
        print("Admin Login: admin@karmixtech.com")
        print("Admin Password: Admin@123")
        print("=" * 50)

if __name__ == '__main__':
    init_database()
