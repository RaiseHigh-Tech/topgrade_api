# Profile API Documentation

## Overview
The Profile API provides comprehensive user profile management for the mobile application. It includes user information retrieval, profile updates with conditional field restrictions, and learning statistics.

**Header Required:**
```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. Get User Profile
**Endpoint:** `GET /profile`

**Description:** Retrieves comprehensive user profile data including personal information, learning statistics, and conditional update permissions.

#### Request Example
```bash
curl -X GET "https://your-domain.com/api/profile" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#### Response Format
```json
{
  "success": true,
  "data": {
    "user_info": {
      "id": 123,
      "email": "user@example.com",
      "fullname": "John Doe",
      "phone_number": "+1234567890",
      "can_update_phone": true,
      "can_update_email": false,
      "registration_type": "email"
    },
    "learning_stats": {
      "total_purchases": 3,
      "total_bookmarks": 5,
      "total_courses": 3,
      "completed_courses": 1,
      "completion_rate": 33.3,
      "recent_activity_count": 12
    }
  }
}
```

#### Field Descriptions
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | User's unique identifier |
| `email` | String | User's email address |
| `fullname` | String | User's full name |
| `phone_number` | String | User's phone number |
| `can_update_phone` | Boolean | Whether user can update phone number |
| `can_update_email` | Boolean | Whether user can update email |
| `registration_type` | String | How user registered: "email" or "phone_otp" |
| `total_purchases` | Integer | Number of program purchases |
| `total_bookmarks` | Integer | Number of bookmarked programs |
| `total_courses` | Integer | Number of enrolled courses |
| `completed_courses` | Integer | Number of completed courses |
| `completion_rate` | Float | Course completion percentage |
| `recent_activity_count` | Integer | Recent activity in last 7 days |

---

### 2. Update User Profile
**Endpoint:** `PUT /profile/update`

**Description:** Updates user profile information with field-specific restrictions based on registration method.

#### Update Rules
| Registration Type | Can Update Email | Can Update Phone | Can Update Fullname |
|-------------------|------------------|------------------|-------------------|
| **Email**         | ❌ No            | ✅ Yes           | ✅ Yes            |
| **Phone OTP**     | ✅ Yes           | ❌ No            | ✅ Yes            |

#### Request Body Schema
```json
{
  "fullname": "string (optional)",
  "email": "string (optional)", 
  "phone_number": "string (optional)"
}
```

#### Request Example
```bash
curl -X PUT "https://your-domain.com/api/profile/update" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "John Smith",
    "phone_number": "+9876543210"
  }'
```

#### Success Response
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "fullname": "John Smith",
    "email": "user@example.com",
    "phone_number": "+9876543210",
    "can_update_phone": true,
    "can_update_email": false
  }
}
```

#### Error Responses

**Phone Update Restriction (Phone OTP Users):**
```json
{
  "success": false,
  "message": "Phone number cannot be updated for accounts registered via phone OTP"
}
```

**Email Update Restriction (Email Users):**
```json
{
  "success": false,
  "message": "Email cannot be updated for accounts registered via email"
}
```

**Duplicate Email:**
```json
{
  "success": false,
  "message": "This email is already registered with another account"
}
```

**Duplicate Phone:**
```json
{
  "success": false,
  "message": "This phone number is already registered with another account"
}
```
---

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation errors, restricted updates)
- `401` - Unauthorized (invalid/expired token)
- `500` - Internal Server Error

## Testing

### Test Cases

1. **Profile Loading**
   - Test with valid token
   - Test with expired token
   - Test network error handling

2. **Profile Updates**
   - Test fullname update (always allowed)
   - Test email update (phone OTP users only)
   - Test phone update (email users only)
   - Test duplicate email/phone validation
   - Test restriction error messages

3. **UI Conditional Logic**
   - Verify edit buttons show/hide based on `can_update_*` flags
   - Test registration type-specific messaging
   - Verify profile data refresh after updates

### Sample Test Data

**Email User:**
```json
{
  "email": "john@example.com",
  "registration_type": "email",
  "can_update_email": false,
  "can_update_phone": true
}
```

**Phone OTP User:**
```json
{
  "email": "phone_1234567890_1640995200@tempuser.com",
  "registration_type": "phone_otp", 
  "can_update_email": true,
  "can_update_phone": false
}
```