"""
Routes package initialization
"""
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp

__all__ = ['auth_bp', 'student_bp', 'admin_bp']
