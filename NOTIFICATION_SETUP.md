# Student Field Update Notification System - Setup Guide

## Overview
The notification system handles all communications when students request to update their fields/course roles. It includes:
- **In-app notifications** (stored in database)
- **Email notifications** (sent to students, admins, and teachers)
- **Separate views** for students, admins, and teachers to retrieve and manage their notifications

## Files Created/Modified

### New Files
1. **notifications/models/student_field_update_notification.py** - Model to store in-app notifications
2. **notifications/serializers/student_field_update_notification.py** - Serializer for the notification model
3. **notifications/services/student_field_update_notifier.py** - Service functions to create notifications
4. **notifications/views/student_field_update_notification.py** - API views for retrieving notifications
5. **notifications/views/notify_admin_teacher_student_update.py** - Centralized email notification handler

### Modified Files
1. **students/views.py** - Integrated notification system into request creation and approval/rejection flows
2. **students/urls.py** - Added field update request endpoints
3. **notifications/models/__init__.py** - Added new model to imports
4. **notifications/serializers/__init__.py** - Added new serializer to imports
5. **notifications/urls.py** - Added notification API endpoints

## Database Migration

Before using the system, run these commands:

```bash
# Create migration file
python manage.py makemigrations notifications

# Apply migration
python manage.py migrate
```

## API Endpoints

### 1. Student Field Update Request Creation
**Endpoint:** `PUT /students/<student_id>/`
**Authentication:** Required
**Permission:** Student (own profile) or Admin/Teacher

**Request Body:**
```json
{
  "requested_role_id": "<course-role-uuid>",
  "message": "Optional reason for requesting this role"
}
```

**Response:** 201 Created
```json
{
  "id": "<request-id>",
  "student": "<student-data>",
  "requested_role": "<role-id>",
  "message": "...",
  "status": "pending",
  "created_at": "2026-02-06T..."
}
```

**Behavior:**
- Creates a `StudentFieldUpdateRequest` with status `pending`
- Creates in-app notifications for all admins and teachers
- Sends emails to all admins and teachers

---

### 2. List Student Field Update Requests
**Endpoint:** `GET /students/field-requests/`
**Authentication:** Required
**Permission:** Admin or Teacher only

**Response:** 200 OK
```json
[
  {
    "id": "<request-id>",
    "student": {
      "id": "...",
      "user": "..."
    },
    "requested_role": "...",
    "status": "pending",
    "created_at": "..."
  },
  ...
]
```

---

### 3. Approve/Reject Field Update Request
**Endpoint:** `POST /students/field-requests/<request_id>/action/`
**Authentication:** Required
**Permission:** Admin or Teacher only

**Request Body:**
```json
{
  "action": "approve",
  "message": "Approved! Welcome to the new role."
}
```
or
```json
{
  "action": "reject",
  "message": "Does not meet the current requirements."
}
```

**Response:** 200 OK (same as request detail)

**Behavior:**
- If `action == "approve"`: Adds the course role to the student's profile
- Creates in-app notification for the student
- Sends approval/rejection email to the student

---

### 4. Student Field Update Notifications
**Endpoint:** `GET /notifications/student/field-update-notifications/`
**Authentication:** Required
**Permission:** Student only

**Response:** 200 OK
```json
[
  {
    "id": "<notification-id>",
    "student_user": {
      "id": "...",
      "first_name": "...",
      "last_name": "...",
      "email": "..."
    },
    "reviewer_user": {
      "id": "...",
      "first_name": "...",
      "last_name": "...",
      "email": "..."
    },
    "field_update_request": {
      "id": "...",
      "requested_role": "...",
      "status": "approved",
      "created_at": "..."
    },
    "notification_type": "field_update_approved",
    "message": "Optional reviewer message",
    "is_read": false,
    "created_at": "..."
  },
  ...
]
```

**Notification Types for Students:**
- `field_update_approved` - Request was approved
- `field_update_rejected` - Request was rejected

---

### 5. Admin/Teacher Field Update Request Notifications
**Endpoint:** `GET /notifications/admin-teacher/field-update-notifications/`
**Authentication:** Required
**Permission:** Admin or Teacher only

**Response:** 200 OK (same structure as student notifications)

**Notification Types for Admins/Teachers:**
- `field_update_request` - New request from a student to review

---

### 6. Get Notification Detail
**Endpoint:** `GET /notifications/field-update-notifications/<notification_id>/`
**Authentication:** Required
**Permission:** Student or reviewer of the notification

**Response:** 200 OK (single notification object)

---

### 7. Mark Notification as Read
**Endpoint:** `POST /notifications/student/field-update-notifications/` (with notification ID)
**Authentication:** Required
**Permission:** Student only

**Request Body:**
```json
{
  "notification_id": "<notification-id>"
}
```

**Response:** 200 OK (updated notification object)

---

## Notification Flow Diagram

```
Student requests to add CourseRole
    ↓
StudentFieldUpdateRequest created (status: pending)
    ↓
For each Admin/Teacher:
    ├─ StudentFieldUpdateNotification created (type: field_update_request)
    └─ Email sent to reviewer
    ↓
Admin/Teacher reviews and approves/rejects
    ├─ If APPROVE:
    │   ├─ CourseRole added to student.fields
    │   ├─ Request status → approved
    │   ├─ StudentFieldUpdateNotification created (type: field_update_approved)
    │   └─ Email sent to student: "✅ Your request was approved"
    │
    └─ If REJECT:
        ├─ Request status → rejected
        ├─ StudentFieldUpdateNotification created (type: field_update_rejected)
        └─ Email sent to student: "❌ Your request was rejected"
```

## Email Templates

### Email to Admins/Teachers (New Request)
```
Subject: 🎓 New Field Update Request from <student-email>

Hello Admin/Teacher,

A student has requested to add a new field/course role to their profile.

Student Details:
- Name: <first_name> <last_name>
- Email: <email>
- Student ID: <matric_no>

Request Details:
- Requested Role: <role_name>
- Message: <message>
- Requested on: <created_at>

Review and approve/reject here: <frontend_url>/admin/field-requests/<request_id>

Best regards,
Student Grade Management Dashboard
```

### Email to Student (Approval)
```
Subject: ✅ Your Field Update Request Has Been Approved!

Hello <first_name>,

Great news! Your request to add '<role_name>' has been approved.

Approved by: <reviewer_first_name> <reviewer_last_name>

<reviewer_message (if any)>

Your profile has been updated and you can now access this field/role.

View your updated profile: <frontend_url>/student/dashboard

Best regards,
Student Grade Management Dashboard
```

### Email to Student (Rejection)
```
Subject: ❌ Your Field Update Request Has Been Rejected

Hello <first_name>,

Unfortunately, your request to add '<role_name>' has been rejected.

Rejected by: <reviewer_first_name> <reviewer_last_name>

Reason: <reviewer_message (if any)>

You can submit a new request or contact your administrator for assistance.

View your request details: <frontend_url>/student/field-requests/<request_id>

Best regards,
Student Grade Management Dashboard
```

## Configuration

### Email Settings (.env)
Ensure your email configuration in `config/settings.py` is properly set:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
EMAIL_USE_TLS=True
MAIL_FROM=your-email@gmail.com
```

### Frontend URL
Set the `FRONTEND_URL` in your `.env` file for email links:

```
FRONTEND_URL=http://localhost:5173
```

## Optional Enhancements

### 1. Use Celery for Async Email
Replace `send_mail` with Celery tasks for non-blocking email delivery:

```python
from celery import shared_task

@shared_task
def send_field_update_email(recipient_email, subject, body):
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient_email])
```

### 2. Add Pagination to Notification Lists
```python
from rest_framework.pagination import PageNumberPagination

class NotificationPagination(PageNumberPagination):
    page_size = 10
```

### 3. Add Filtering by Notification Type
```python
# In views
notification_type = request.query_params.get('type')
if notification_type:
    notifications = notifications.filter(notification_type=notification_type)
```

### 4. Add Unread Count Endpoint
```python
class FieldUpdateNotificationUnreadCountView(APIView):
    def get(self, request):
        count = StudentFieldUpdateNotification.objects.filter(
            student_user=request.user, is_read=False
        ).count()
        return Response({"unread_count": count})
```

## Testing the System

### 1. Student requests a field update
```bash
curl -X PUT http://localhost:8000/students/<student_id>/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "requested_role_id": "<course-role-id>",
    "message": "I want to study this field"
  }'
```

### 2. Admin lists pending requests
```bash
curl -X GET http://localhost:8000/students/field-requests/ \
  -H "Authorization: Bearer <admin-token>"
```

### 3. Admin approves the request
```bash
curl -X POST http://localhost:8000/students/field-requests/<request_id>/action/ \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "message": "Welcome to the program!"
  }'
```

### 4. Student checks their notifications
```bash
curl -X GET http://localhost:8000/notifications/student/field-update-notifications/ \
  -H "Authorization: Bearer <student-token>"
```

## Troubleshooting

### Emails not being sent
1. Check `config/settings.py` EMAIL settings
2. Check application logs for email errors
3. Test email manually:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
   ```

### Notifications not appearing
1. Ensure migrations were run: `python manage.py migrate`
2. Check that `StudentFieldUpdateNotification` model is imported in admin
3. Verify the notification view is called in the correct flow

### Permission errors
1. Verify user `role` field is set correctly (`student`, `teacher`, `admin`)
2. Check that JWT authentication is working
3. Ensure request includes proper `Authorization` header
