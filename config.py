"""
Configuration settings for KarmixTech LMS
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'karmixtech-lms-secret-key-2024')

    # MySQL Connection
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456789@localhost/lms_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 5,
    'pool_recycle': 300,
    }

    # Session settings
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # Pagination
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
