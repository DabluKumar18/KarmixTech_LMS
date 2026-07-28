"""
Users API - REST endpoints for user operations
"""
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
import re

from models.user import db, User
from models.notification import Notification

users_api = Blueprint('users_api', __name__)


@users_api.route('/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()

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

    if not first_name:
        errors.append('First name is required')
    if not last_name:
        errors.append('Last name is required')

    # Check existing email
    if User.query.filter_by(email=email).first():
        errors.append('Email already registered')

    if errors:
        return jsonify({'errors': errors}), 400

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
        message='Your account has been created successfully.',
        notification_type='success'
    )

    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201


@users_api.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.session.commit()

    login_user(user, remember=remember)

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })


@users_api.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'})


@users_api.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile"""
    return jsonify(current_user.to_dict())


@users_api.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'first_name' in data:
        current_user.first_name = data['first_name'].strip()
    if 'last_name' in data:
        current_user.last_name = data['last_name'].strip()
    if 'phone' in data:
        current_user.phone = data['phone'].strip()
    if 'bio' in data:
        current_user.bio = data['bio'].strip()
    if 'city' in data:
        current_user.city = data['city'].strip()
    if 'country' in data:
        current_user.country = data['country'].strip()

    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    })


@users_api.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    errors = []

    if not check_password_hash(current_user.password_hash, current_password):
        errors.append('Current password is incorrect')

    if not new_password or len(new_password) < 8:
        errors.append('New password must be at least 8 characters')

    if errors:
        return jsonify({'errors': errors}), 400

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'})


@users_api.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID (public info only)"""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })
