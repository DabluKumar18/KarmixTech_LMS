# KarmixTech LMS

![KarmixTech LMS Banner](https://images.pexels.com/photos/5905485/pexels-photo-5905485.jpeg?auto=compress&cs=tinysrgb&w=1200)

A comprehensive, industry-level **Learning Management System** built with Python Flask, featuring modern responsive design, secure authentication, REST APIs, and complete admin panel.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation Guide](#installation-guide)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Overview

KarmixTech LMS is a professional-grade learning management platform designed for educational institutions, corporations, and training providers. It provides a complete solution for course delivery, student management, progress tracking, and analytics.

### Key Highlights

- Modern, responsive UI/UX design
- Secure authentication with password hashing
- Role-based access control (Student/Admin)
- RESTful API architecture
- Real-time progress tracking
- Dashboard analytics
- Comprehensive course management

## Features

### Student Features
- User registration and authentication
- Personal dashboard with learning statistics
- Browse and search courses
- Course enrollment
- **Watch embedded YouTube videos**
- **Download PDF lesson notes**
- Progress tracking with **auto-updating percentage**
- **Next/Previous lesson navigation**
- **Mark lessons as completed**
- Certificate generation upon 100% completion
- Profile management
- Change password functionality
- Notification center

### Admin Features
- Admin dashboard with analytics
- Course management (CRUD operations)
- **Module management (add, edit, delete, reorder)**
- **Lesson management with:**
  - Title and description
  - YouTube video URL (auto-extracts video ID)
  - PDF notes URL
  - Duration tracking
  - Order/reordering
  - Preview mode
  - Publish/unpublish
- Student management
- Enrollment tracking
- User activity monitoring
- Statistics and reports
- Category management

### Technical Features
- Clean code architecture (MVC pattern)
- RESTful API endpoints
- Form validation (client & server)
- Error handling pages (404, 403, 500)
- Pagination for data tables
- Search functionality
- Session management
- SQL injection protection
- CSRF protection ready

## Technology Stack

| Category | Technology |
|----------|------------|
| Backend | Python 3.11+, Flask |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |
| Authentication | Flask-Login |
| Frontend | HTML5, CSS3, JavaScript |
| Styling | Custom CSS, CSS Variables |
| Icons | Font Awesome 6 |
| Fonts | Google Fonts (Inter) |
| HTTP Client | Fetch API |

## Project Structure

```
KarmixTech_LMS/
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   ├── js/
│   │   └── main.js        # JavaScript functionality
│   └── images/            # Static images
│
├── templates/
│   ├── base.html          # Base template
│   ├── dashboard.html     # Dashboard layout
│   ├── index.html         # Landing page
│   ├── about.html         # About page
│   ├── contact.html       # Contact page
│   ├── auth/
│   │   ├── login.html     # Student login
│   │   ├── register.html  # Student registration
│   │   └── admin_login.html # Admin login
│   ├── student/
│   │   ├── dashboard.html
│   │   ├── courses.html
│   │   ├── course_detail.html
│   │   ├── my_courses.html
│   │   ├── profile.html
│   │   ├── learn.html
│   │   ├── notifications.html
│   │   └── change_password.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── courses.html
│   │   ├── course_form.html
│   │   ├── students.html
│   │   ├── student_detail.html
│   │   └── statistics.html
│   └── errors/
│       ├── 404.html
│       ├── 403.html
│       └── 500.html
│
├── models/
│   ├── __init__.py
│   ├── user.py             # User model
│   ├── course.py           # Course model
│   ├── enrollment.py       # Enrollment model
│   ├── progress.py         # Progress model
│   └── notification.py     # Notification model
│
├── routes/
│   ├── auth.py             # Authentication routes
│   ├── student.py          # Student routes
│   └── admin.py             # Admin routes
│
├── api/
│   ├── __init__.py
│   ├── courses.py          # Course API endpoints
│   ├── users.py            # User API endpoints
│   ├── enrollments.py      # Enrollment API endpoints
│   └── progress.py         # Progress API endpoints
│
└── services/
    ├── analytics.py        # Analytics service
    ├── course_service.py   # Course operations
    └── enrollment_service.py # Enrollment operations
```

## Installation Guide

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- PostgreSQL database (or Supabase account)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/karmixtech-lms.git
cd karmixtech-lms
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
SUPABASE_DB_URL=your-postgresql-connection-string
FLASK_ENV=development
```

### Step 5: Initialize Database

```bash
python app.py
```

The application will automatically create tables and seed initial data.

### Step 6: Run the Application

```bash
python app.py
```

Open your browser and navigate to: `http://localhost:5000`

## Database Setup

### Database Schema

```sql
TABLE users (
    id                  SERIAL PRIMARY KEY,
    email               VARCHAR(120) UNIQUE NOT NULL,
    password_hash       VARCHAR(256) NOT NULL,
    first_name          VARCHAR(50) NOT NULL,
    last_name           VARCHAR(50) NOT NULL,
    role                VARCHAR(20) DEFAULT 'student',
    is_active           BOOLEAN DEFAULT TRUE,
    email_verified      BOOLEAN DEFAULT FALSE,
    profile_image       VARCHAR(255),
    phone               VARCHAR(20),
    bio                 TEXT,
    city                VARCHAR(100),
    country             VARCHAR(100),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login          TIMESTAMP
);

TABLE courses (
    id                  SERIAL PRIMARY KEY,
    title               VARCHAR(200) NOT NULL,
    slug                VARCHAR(250) UNIQUE NOT NULL,
    description         TEXT NOT NULL,
    category            VARCHAR(50) NOT NULL,
    level               VARCHAR(20) DEFAULT 'Beginner',
    duration_hours      INTEGER DEFAULT 0,
    price               FLOAT DEFAULT 0,
    is_free             BOOLEAN DEFAULT TRUE,
    is_published        BOOLEAN DEFAULT TRUE,
    thumbnail           VARCHAR(255),
    instructor          VARCHAR(100),
    language            VARCHAR(20) DEFAULT 'English',
    created_by          INTEGER REFERENCES users(id),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

TABLE enrollments (
    id                  SERIAL PRIMARY KEY,
    user_id              INTEGER REFERENCES users(id) NOT NULL,
    course_id            INTEGER REFERENCES courses(id) NOT NULL,
    enrolled_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMP,
    is_completed        BOOLEAN DEFAULT FALSE,
    progress_percentage FLOAT DEFAULT 0,
    last_accessed       TIMESTAMP,
    UNIQUE(user_id, course_id)
);

TABLE progress (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER REFERENCES users(id) NOT NULL,
    course_id           INTEGER REFERENCES courses(id) NOT NULL,
    lesson_id           INTEGER REFERENCES lessons(id),
    is_completed        BOOLEAN DEFAULT FALSE,
    time_spent_minutes  INTEGER DEFAULT 0,
    completed_at        TIMESTAMP,
    UNIQUE(user_id, lesson_id)
);

TABLE notifications (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER REFERENCES users(id) NOT NULL,
    title               VARCHAR(200) NOT NULL,
    message             TEXT NOT NULL,
    notification_type   VARCHAR(50) DEFAULT 'info',
    link                VARCHAR(255),
    is_read             BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration

### Application Config

The application uses environment-based configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | 'karmixtech-lms-secret-key-2024' |
| `SUPABASE_DB_URL` | PostgreSQL connection string | Required |
| `FLASK_ENV` | Environment mode | 'development' |
| `ITEMS_PER_PAGE` | Pagination limit | 10 |

### Security Settings

- Session cookie HTTPOnly: Enabled
- Session lifetime: 24 hours
- Password hashing: werkzeug.security (pbkdf2:sha256)

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### POST /api/users/register
Register a new user.

**Request Body:**
```json
{
    "email": "student@example.com",
    "password": "Password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "message": "Registration successful",
    "user": { ... }
}
```

#### POST /api/users/login
Login user.

**Request Body:**
```json
{
    "email": "student@example.com",
    "password": "Password123"
}
```

### Course Endpoints

#### GET /api/courses
Get all courses with filters.

**Query Parameters:**
- `search` - Search term
- `category` - Filter by category
- `level` - Filter by level
- `page` - Page number
- `per_page` - Items per page

**Response:**
```json
{
    "courses": [...],
    "total": 100,
    "pages": 10,
    "current_page": 1
}
```

#### GET /api/courses/:id
Get course details.

### Enrollment Endpoints

#### POST /api/enrollments
Enroll in a course.

**Request Body:**
```json
{
    "course_id": 1
}
```

#### GET /api/enrollments
Get user's enrollments.

### Progress Endpoints

#### GET /api/progress/:course_id
Get course progress.

#### POST /api/progress/:course_id/lesson/:lesson_id
Mark lesson as completed.

## Screenshots

### Landing Page
![Landing Page](https://via.placeholder.com/800x400?text=Landing+Page)

### Student Dashboard
![Student Dashboard](https://via.placeholder.com/800x400?text=Student+Dashboard)

### Course Detail
![Course Detail](https://via.placeholder.com/800x400?text=Course+Detail)

### Admin Dashboard
![Admin Dashboard](https://via.placeholder.com/800x400?text=Admin+Dashboard)

### Course Management
![Course Management](https://via.placeholder.com/800x400?text=Course+Management)

## Default Credentials

### Admin Account
- Email: `admin@karmixtech.com`
- Password: `Admin@123`

## Future Enhancements

- Video hosting integration
- Discussion forums
- Live sessions with WebRTC
- Payment gateway (Stripe)
- Email notifications
- Two-factor authentication
- Mobile app (React Native)
- AI-powered course recommendations
- Multi-language support
- Badges and gamification
- Social login (Google, GitHub)
- Course ratings and reviews
- Instructor dashboard
- Certificate verification system

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask Documentation
- SQLAlchemy ORM
- Font Awesome Icons
- Google Fonts (Inter)
- Pexels for stock images

---

**Developed by KarmixTech Team**

*This project is suitable for portfolio presentation and internship submission.*
