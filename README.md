# Student Score Management Backend

A Django REST Framework-based backend application for managing student grades, courses, and user authentication. This system provides role-based access control for students, teachers, and administrators with comprehensive grade tracking and course management features.

## Project Overview

**Student Score Management Backend** is a comprehensive API that handles:
- **User Authentication**: Registration, login, email verification via OTP
- **Course Management**: Create, update, and manage courses
- **Student Enrollment**: Students can enroll in courses
- **Grade Management**: Teachers can assign grades and students can view their grades
- **Analytics**: Course statistics and student performance tracking
- **Image Upload**: Cloud-based image uploads using Cloudinary

## Key Features

- Role-based access control (Student, Teacher, Admin)
- JWT token-based authentication with cookie support
- Email verification through OTP
- Course statistics and analytics
- Grade filtering and sorting capabilities
- Cloud image storage integration

## Technology Stack

- **Framework**: Django 6.0.1 with Django REST Framework 3.16.1
- **Authentication**: JWT (djangorestframework-simplejwt 5.5.1)
- **Database**: SQLite (with MySQL support via mysqlclient)
- **Task Queue**: Celery 5.6.2 with Redis
- **Cloud Storage**: Cloudinary 1.44.1
- **Email**: SMTP backend
- **Python**: 3.12+

## Dependencies

- `django>=6.0.1`
- `djangorestframework>=3.16.1`
- `djangorestframework-simplejwt>=5.5.1`
- `django-cors-headers>=4.9.0`
- `gunicorn>=26.2.0`
- `dj-database-url>=2.3.0`
- `whitenoise>=6.9.0`
- `celery>=5.6.2`
- `redis>=7.1.0`
- `cloudinary>=1.44.1`
- `mysqlclient>=2.2.7`
- `python-dotenv>=1.2.1`

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/bee-jay80/student-score-management-be.git
cd student-score-management-be
```

### 2. Create a virtual environment

```bash
python -m venv venv
# On Windows
venv\\Scripts\\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
# Or using uv (modern Python package manager)
uv pip install -r requirements.txt
```

### 4. Environment configuration

Create a `.env` file in the project root with the following variables:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
EMAIL=your-email@gmail.com
EMAIL_USE_TLS=True

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### 5. Apply database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## Production deployment

Deploy on a Linux host with HTTPS terminated by a trusted reverse proxy. Configure these environment variables in the hosting provider's secret/configuration settings (do not commit production credentials or a production `.env` file):

```env
DEBUG=False
DJANGO_SECRET_KEY=<a-long-random-secret>
ALLOWED_HOSTS=api.example.com
DATABASE_URL=<database-connection-url>
FRONTEND_URL=https://your-frontend.example.com
CORS_ALLOWED_ORIGINS=https://your-frontend.example.com
CSRF_TRUSTED_ORIGINS=https://your-frontend.example.com
```

Provide the SMTP and Cloudinary variables documented in the local `.env` setup if the deployed application needs email delivery and image uploads. For a reverse proxy that sets `X-Forwarded-Proto` to `https` and strips untrusted client-supplied copies of that header, set `TRUST_PROXY_SSL_HEADER=True`; otherwise leave it unset.

Install dependencies, apply database migrations, and collect static assets as part of deployment:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

The included `Procfile` starts the application with Gunicorn. If your host does not use Procfiles, use this as its web start command:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Before exposing the service, run `python manage.py check --deploy` with the production environment variables configured. `DEBUG=False` enables HTTPS redirects and secure session, CSRF, and JWT cookies; set `SECURE_HSTS_SECONDS=0` only when you need to disable HSTS during an initial HTTPS rollout.

## API Endpoints

### Base URL

`http://localhost:8000/api/`

### Authentication Endpoints (`/api/auth/`)

#### Register User
- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Authentication**: Not required

**Request Payload**:

```json
{
  "email": "student@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

**Response**:

```json
{
  "detail": "Check your email for OTP verification"
}
```

#### Login User
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Authentication**: Not required

**Request Payload**:

```json
{
  "email": "student@example.com",
  "password": "securepassword123"
}
```

**Response**:

```json
{
  "status": "success",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "role": "student"
}
```

#### Verify OTP
- **URL**: `/api/auth/verify-otp/`
- **Method**: `POST`
- **Authentication**: Not required

**Request Payload**:

```json
{
  "otp": "123456"
}
```

**Response**:

```json
{
  "detail": "Email verified successfully"
}
```

#### Resend OTP
- **URL**: `/api/auth/resend-otp/`
- **Method**: `POST`
- **Authentication**: Not required

**Response**:

```json
{
  "detail": "OTP resent successfully"
}
```

#### Refresh Token
- **URL**: `/api/auth/refresh/`
- **Method**: `POST`
- **Authentication**: Not required

**Response**:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Logout
- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Authentication**: Required

**Response**: `204 No Content`

#### Get Current User
- **URL**: `/api/auth/me/`
- **Method**: `GET`
- **Authentication**: Required

**Response**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

#### Image Upload
- **URL**: `/api/auth/image-upload/`
- **Method**: `POST`
- **Authentication**: Required

**Request Payload**: multipart/form-data

```text
image: <file>
```

**Response**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user": "550e8400-e29b-41d4-a716-446655440001",
  "image": "https://cloudinary.url/image.jpg",
  "uploaded_at": "2026-02-04T10:30:00Z"
}
```

### Courses Endpoints (`/api/courses/`)

#### List All Active Courses
- **URL**: `/api/courses/`
- **Method**: `GET`
- **Authentication**: Required

**Response**:

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Mathematics 101",
    "duration": "4 weeks",
    "description": "Introduction to calculus",
    "created_at": "2026-02-04T10:00:00Z",
    "is_active": true
  }
]
```

#### Create Course
- **URL**: `/api/courses/create/`
- **Method**: `POST`
- **Authentication**: Required
- **Permission**: Teacher or Admin

**Request Payload**:

```json
{
  "title": "Mathematics 101",
  "duration": "4 weeks",
  "description": "Introduction to calculus"
}
```

#### Get Course Details
- **URL**: `/api/courses/<course_id>/`
- **Method**: `GET`
- **Authentication**: Required

#### Update Course
- **URL**: `/api/courses/<course_id>/`
- **Method**: `PUT`
- **Authentication**: Required
- **Permission**: Teacher or Admin

**Request Payload**:

```json
{
  "title": "Updated Title",
  "duration": "6 weeks",
  "description": "Updated description"
}
```

#### Delete/Deactivate Course
- **URL**: `/api/courses/<course_id>/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Permission**: Teacher or Admin

**Response**: `204 No Content`

### Enrollment Endpoints (`/api/courses/enrollment/`)

#### Create Enrollment
- **URL**: `/api/courses/enrollment/`
- **Method**: `POST`
- **Authentication**: Required
- **Permission**: Student or Admin

**Request Payload**:

```json
{
  "course": "550e8400-e29b-41d4-a716-446655440000",
  "month": "February",
  "status": "active"
}
```

#### Get My Enrollments
- **URL**: `/api/courses/enrollment/`
- **Method**: `GET`
- **Authentication**: Required

#### Get Enrollment Detail
- **URL**: `/api/courses/enrollment/<enrollment_id>/`
- **Method**: `GET`
- **Authentication**: Required

#### Update Enrollment
- **URL**: `/api/courses/enrollment/<enrollment_id>/`
- **Method**: `PUT`
- **Authentication**: Required

**Request Payload**:

```json
{
  "status": "completed"
}
```

#### Delete Enrollment
- **URL**: `/api/courses/enrollment/<enrollment_id>/`
- **Method**: `DELETE`
- **Authentication**: Required

**Response**: `204 No Content`

### Grades Endpoints (`/api/grades/`)

#### Create Grade
- **URL**: `/api/grades/create/`
- **Method**: `POST`
- **Authentication**: Required
- **Permission**: Teacher or Admin

**Request Payload**:

```json
{
  "enrollment": "550e8400-e29b-41d4-a716-446655440001",
  "score": 95,
  "remark": "Excellent performance"
}
```

#### Get All Grades (Teacher)
- **URL**: `/api/grades/list/`
- **Method**: `GET`
- **Authentication**: Required
- **Permission**: Teacher or Admin

Query parameters support filtering by `enrollment_id`, `student_id`, `student_name`, `course_id`, `course_name`, and `student_email`.

#### Get Teacher's Grades
- **URL**: `/api/grades/teacher-list/`
- **Method**: `GET`
- **Authentication**: Required
- **Permission**: Teacher or Admin

#### Get Grade Detail
- **URL**: `/api/grades/<grade_id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Permission**: Teacher or Admin

#### Update Grade
- **URL**: `/api/grades/<grade_id>/`
- **Method**: `PUT`
- **Authentication**: Required
- **Permission**: Teacher or Admin

**Request Payload**:

```json
{
  "score": 92,
  "remark": "Good performance"
}
```

#### Delete Grade
- **URL**: `/api/grades/<grade_id>/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Permission**: Teacher or Admin

**Response**: `204 No Content`

#### Course Statistics (Teacher)
- **URL**: `/api/grades/course-stats/`
- **Method**: `GET`
- **Authentication**: Required
- **Permission**: Teacher or Admin

Required query parameter: `course_id`

#### Student Course Statistics
- **URL**: `/api/grades/student-course-stats/`
- **Method**: `GET`
- **Authentication**: Required
- **Permission**: Student

Required query parameter: `course_id`

#### Student Grades
- **URL**: `/api/grades/student-grades/`
- **Method**: `GET`
- **Authentication**: Required
- **Permission**: Student

Optional query parameters include `min_score`, `max_score`, `graded_after`, `graded_before`, `course_name`, and `enrollment_month`.

#### Student Grade Detail
- **URL**: `/api/grades/student-grades/<grade_id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Permission**: Student

## Authentication

### JWT Authentication
This API uses JWT for authentication. Tokens are typically stored in HTTP-only cookies for security.

- **Access Token**: 15 minutes
- **Refresh Token**: 7 days
- Tokens rotate on refresh and old tokens are blacklisted

**Authentication header** (if not using cookies):

```http
Authorization: Bearer <access_token>
```

### User Roles

| Role | Permissions |
|------|-------------|
| **Student** | View own grades, courses, enrollments; upload images |
| **Teacher** | Create/update courses; assign grades; view course statistics |
| **Admin** | Full access; manage users and approvals |

## Usage Examples

### Register and Login as Student

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "student"
  }'

curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"otp": "123456"}'

curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!"
  }' \
  -c cookies.txt
```

### Enroll in a Course (as Student)

```bash
curl http://localhost:8000/api/courses/ \
  -b cookies.txt

curl -X POST http://localhost:8000/api/courses/enrollment/ \
  -H "Content-Type: application/json" \
  -d '{
    "course": "550e8400-e29b-41d4-a716-446655440000",
    "month": "February",
    "status": "active"
  }' \
  -b cookies.txt
```

### Assign Grade (as Teacher)

```bash
curl -X POST http://localhost:8000/api/grades/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment": "550e8400-e29b-41d4-a716-446655440001",
    "score": 92,
    "remark": "Great work!"
  }' \
  -b cookies.txt
```

### View Course Statistics (as Teacher)

```bash
curl "http://localhost:8000/api/grades/course-stats/?course_id=550e8400-e29b-41d4-a716-446655440000" \
  -b cookies.txt
```

## Environment Variables

| Variable | Description | Notes |
|----------|-------------|-------|
| `DJANGO_SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `False` in production |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `SMTP_SERVER` | SMTP server | Required for email sends |
| `SMTP_PORT` | SMTP port | `587` for TLS |
| `MAIL_USERNAME` | Email username | Required for SMTP |
| `MAIL_PASSWORD` | Email password | Required for SMTP |
| `FRONTEND_URL` | Frontend URL | `http://localhost:5173` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | Required for uploads |
| `CLOUDINARY_API_KEY` | Cloudinary API key | Required for uploads |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | Required for uploads |
| `REDIS_URL` | Redis connection URL | Required for Celery |

## Running with Docker

```bash
# Build image
docker build -t student-score-management-be .

# Run container
docker run -p 8000:8000 --env-file .env student-score-management-be
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m "Add amazing feature"`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a pull request

## License

This project is open source and available under the MIT License.

## Support

For support, email [your-email@example.com] or open an issue in the repository.

## Project Structure

```text
student-score-management-be/
├── accounts/           # User authentication and management
├── courses/            # Course management
├── grades/             # Grade management and analytics
├── students/           # Student-specific functionality
├── teachers/           # Teacher-specific functionality
├── notifications/      # Notification services
├── forgot_password/    # Password reset functionality
├── config/             # Django configuration
├── templates/          # HTML templates
├── manage.py           # Django management script
├── main.py             # Entry point
└── requirements.txt    # Python dependencies
```

**Last Updated**: February 4, 2026
**Version**: 0.1.0
