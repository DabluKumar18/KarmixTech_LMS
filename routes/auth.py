"""
Authentication Routes - Handles login, register, logout
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import re

from models.user import User, db
from models.notification import Notification

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        # Validation
        errors = []

        if not email:
            errors.append('Email is required')
        else:
            try:
                validate_email(email)
            except EmailNotValidError:
                errors.append('Invalid email format')

        if not password:
            errors.append('Password is required')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters')
        elif not re.search(r'[A-Z]', password):
            errors.append('Password must contain uppercase letter')
        elif not re.search(r'[a-z]', password):
            errors.append('Password must contain lowercase letter')
        elif not re.search(r'[0-9]', password):
            errors.append('Password must contain a number')

        if password != confirm_password:
            errors.append('Passwords do not match')

        if not first_name:
            errors.append('First name is required')
        if not last_name:
            errors.append('Last name is required')

        # Check existing email
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html',
                                   email=email, first_name=first_name,
                                   last_name=last_name)

        # Create user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role='student',
            is_active=True,
            email_verified=True
        )

        db.session.add(user)
        db.session.commit()

        # Create welcome notification
        Notification.create(
            user_id=user.id,
            title='Welcome to KarmixTech LMS!',
            message='Your account has been created successfully. Start exploring courses!',
            notification_type='success'
        )

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return render_template('auth/login.html')

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Login user
        login_user(user, remember=remember)

        # Redirect to intended page or dashboard
        next_page = request.args.get('next')

        if user.is_admin:
            return redirect(next_page or url_for('admin.dashboard'))
        return redirect(next_page or url_for('student.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('auth/admin_login.html')

        user = User.query.filter_by(email=email, role='admin').first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid admin credentials', 'danger')
            return render_template('auth/admin_login.html')

        if not user.is_active:
            flash('Admin account is deactivated', 'danger')
            return render_template('auth/admin_login.html')

        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user)
        return redirect(url_for('admin.dashboard'))

    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()

        # Always show success to prevent email enumeration
        flash('If that email exists in our system, you will receive reset instructions.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')
