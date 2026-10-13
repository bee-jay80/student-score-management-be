#!/bin/bash
# Test script for Student Field Update Notification System
# Usage: Update TOKEN, STUDENT_ID, COURSE_ROLE_ID, REQUEST_ID, NOTIFICATION_ID below

# Configuration
BASE_URL="http://localhost:8000"
STUDENT_TOKEN="<your-student-token>"
ADMIN_TOKEN="<your-admin-token>"
STUDENT_ID="<student-uuid>"
COURSE_ROLE_ID="<course-role-uuid>"
REQUEST_ID="<request-uuid>"
NOTIFICATION_ID="<notification-uuid>"

echo "=========================================="
echo "Student Field Update Notification Tests"
echo "=========================================="

# Test 1: Create field update request
echo -e "\n1️⃣  Creating field update request..."
curl -X PUT "$BASE_URL/students/$STUDENT_ID/" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requested_role_id": "'$COURSE_ROLE_ID'",
    "message": "I want to study this field"
  }' \
  | python -m json.tool

# Test 2: Admin lists pending requests
echo -e "\n\n2️⃣  Admin listing field update requests..."
curl -X GET "$BASE_URL/students/field-requests/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | python -m json.tool

# Test 3: Admin checks their notifications
echo -e "\n\n3️⃣  Admin checking field update request notifications..."
curl -X GET "$BASE_URL/notifications/admin-teacher/field-update-notifications/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | python -m json.tool

# Test 4: Admin approves the request
echo -e "\n\n4️⃣  Admin approving field update request..."
curl -X POST "$BASE_URL/students/field-requests/$REQUEST_ID/action/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "message": "Welcome to the program!"
  }' \
  | python -m json.tool

# Test 5: Student checks their notifications
echo -e "\n\n5️⃣  Student checking their field update notifications..."
curl -X GET "$BASE_URL/notifications/student/field-update-notifications/" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  | python -m json.tool

# Test 6: Get single notification detail
echo -e "\n\n6️⃣  Getting notification detail..."
curl -X GET "$BASE_URL/notifications/field-update-notifications/$NOTIFICATION_ID/" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  | python -m json.tool

# Test 7: Reject a request (alternative to Test 4)
echo -e "\n\n7️⃣  Admin rejecting field update request (alternative test)..."
curl -X POST "$BASE_URL/students/field-requests/$REQUEST_ID/action/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject",
    "message": "Does not meet current program requirements"
  }' \
  | python -m json.tool

echo -e "\n\n=========================================="
echo "✅ Tests Complete!"
echo "=========================================="
