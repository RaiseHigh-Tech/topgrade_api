# TopGrade API Documentation

This document provides comprehensive documentation for the TopGrade API endpoints.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Most endpoints require JWT token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. Add Area of Interest
**POST** `/add-area-of-interest`

Add or update the area of interest for an authenticated user.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "area_of_intrest": "Data Science"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Area of interest updated successfully",
  "area_of_intrest": "Data Science"
}
```

---

### 2. Get Categories
**GET** `/categories`

Retrieve all available categories.

**Authentication Required:** No

**Response:**
```json
{
  "success": true,
  "count": 3,
  "categories": [
    {
      "id": 1,
      "name": "Web Development",
    },
    {
      "id": 2,
      "name": "Data Science"
    }
  ]
}
```

---

### 3. Landing Page Data
**GET** `/landing`

Get landing page data with different program groups. Returns top courses, recently added programs, featured programs, regular programs, advanced programs, and continue watching (for authenticated users).

**Authentication Required:** No (but authentication affects continue_watching)

**Response:**
```json
{
  "success": true,
  "data": {
    "top_course": [
      {
        "id": 1,
        "type": "program",
        "title": "Full Stack Web Development Bootcamp",
        "subtitle": "Master MERN Stack Development",
        "description": "Complete full-stack web development course...",
        "category": {
          "id": 1,
          "name": "Web Development"
        },
        "image": "/media/program_images/image.jpg",
        "duration": "16 weeks",
        "program_rating": 4.8,
        "is_best_seller": true,
        "enrolled_students": 1250,
        "pricing": {
          "original_price": 599.00,
          "discount_percentage": 20.00,
          "discounted_price": 479.20,
          "savings": 119.80
        }
      }
    ],
    "recently_added": [...],
    "featured": [...],
    "programs": [...],
    "advanced_programs": [...],
    "continue_watching": [
      {
        "id": 1,
        "type": "program",
        "title": "Python Data Science Masterclass",
        "progress": {
          "percentage": 75.5,
          "status": "in_progress",
          "last_watched_at": "2024-01-15T10:30:00Z",
          "last_watched_topic": "Introduction to Pandas",
          "completed_topics": 8,
          "total_topics": 12
        }
      }
    ]
  },
  "counts": {
    "top_course": 5,
    "recently_added": 5,
    "featured": 5,
    "programs": 5,
    "advanced_programs": 5,
    "continue_watching": 2
  }
}
```

**Notes:**
- Each group contains maximum 5 programs (continue_watching limited to 2)
- `continue_watching` returns empty array for non-authenticated users
- `continue_watching` includes progress information for authenticated users

---

### 4. Filter Programs
**GET** `/programs/filter`

Get all programs (regular and advanced) with comprehensive filtering options.

**Authentication Required:** No

**Query Parameters:**
- `program_type` (string, optional): Filter by type ('program', 'advanced_program', 'all')
- `category_id` (int, optional): Filter by category ID
- `is_best_seller` (bool, optional): Filter best sellers
- `min_price` (float, optional): Minimum price filter
- `max_price` (float, optional): Maximum price filter
- `min_rating` (float, optional): Minimum rating filter
- `search` (string, optional): Search in title, subtitle, description
- `sort_by` (string, optional): Sort field ('most_relevant', 'recently_added', 'top_rated', 'title', 'price', 'program_rating')
- `sort_order` (string, optional): Sort order ('asc', 'desc')

**Example Request:**
```
GET /api/programs/filter?program_type=program&category_id=1&min_rating=4.0&sort_by=most_relevant
```

**Response:**
```json
{
  "success": true,
  "filters_applied": {
    "program_type": "program",
    "category_id": "1",
    "is_best_seller": null,
    "min_price": null,
    "max_price": null,
    "min_rating": 4.0,
    "search": null,
    "sort_by": "most_relevant",
    "sort_order": "asc"
  },
  "statistics": {
    "total_count": 15,
    "regular_programs_count": 12,
    "advanced_programs_count": 3
  },
  "programs": [...]
}
```

---

### 5. Get Program Details
**GET** `/program/{program_type}/{program_id}/details`

Get detailed information about a specific program including syllabus and topics.

**Authentication Required:** No (but affects video access)

**Path Parameters:**
- `program_type`: 'program' or 'advanced-program'
- `program_id`: Program ID

**Example Request:**
```
GET /api/program/program/1/details
```

**Response:**
```json
{
  "success": true,
  "program": {
    "id": 1,
    "type": "program",
    "title": "Full Stack Web Development Bootcamp",
    "subtitle": "Master MERN Stack Development",
    "category": {
      "id": 1,
      "name": "Web Development"
    },
    "description": "Complete full-stack web development course...",
    "image": "/media/program_images/image.jpg",
    "duration": "16 weeks",
    "program_rating": 4.8,
    "is_best_seller": true,
    "enrolled_students": 1250,
    "pricing": {
      "original_price": 599.00,
      "discount_percentage": 20.00,
      "discounted_price": 479.20,
      "savings": 119.80
    }
  },
  "syllabus": {
    "total_modules": 4,
    "total_topics": 15,
    "modules": [
      {
        "id": 1,
        "module_title": "Frontend Fundamentals",
        "topics_count": 4,
        "topics": [
          {
            "id": 1,
            "topic_title": "HTML5 Semantic Elements",
            "is_free_trail": true,
            "is_intro": true,
            "is_locked": false,
            "video_url": "https://example.com/video1"
          }
        ]
      }
    ]
  }
}
```

---

### 6. Add Bookmark
**POST** `/bookmark`

Add a course to user's bookmarks.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "program_type": "program",
  "program_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Course added to bookmarks successfully!",
  "bookmark": {
    "id": 1,
    "program_type": "program",
    "program_title": "Full Stack Web Development Bootcamp",
    "program_id": 1,
    "bookmarked_date": "2024-01-15T10:30:00Z"
  }
}
```

---

### 7. Remove Bookmark
**DELETE** `/bookmark`

Remove a course from user's bookmarks.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "program_type": "program",
  "program_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "'Full Stack Web Development Bootcamp' removed from bookmarks successfully!"
}
```

---

### 8. Get User Bookmarks
**GET** `/bookmarks`

Get all bookmarks for the authenticated user.

**Authentication Required:** Yes

**Response:**
```json
{
  "success": true,
  "count": 2,
  "bookmarks": [
    {
      "bookmark_id": 1,
      "program": {
        "id": 1,
        "type": "program",
        "title": "Full Stack Web Development Bootcamp",
        "subtitle": "Master MERN Stack Development",
        "description": "Complete full-stack web development course...",
        "category": {
          "id": 1,
          "name": "Web Development"
        },
        "image": "/media/program_images/image.jpg",
        "duration": "16 weeks",
        "program_rating": 4.8,
        "is_best_seller": true,
        "enrolled_students": 1250,
        "pricing": {
          "original_price": 599.00,
          "discount_percentage": 20.00,
          "discounted_price": 479.20,
          "savings": 119.80
        }
      },
      "bookmarked_date": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### 9. Purchase Course
**POST** `/purchase`

Purchase a course with dummy payment gateway.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "program_type": "program",
  "program_id": 1,
  "payment_method": "card"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Course purchased successfully!",
  "pricing": {
    "original_price": 599.00,
    "discount_percentage": 20.00,
    "discounted_price": 479.20,
    "savings": 119.80
  },
  "purchase": {
    "id": 1,
    "program_type": "program",
    "program_title": "Full Stack Web Development Bootcamp",
    "purchase_date": "2024-01-15T10:30:00Z",
    "status": "completed",
    "transaction_id": "TXN123456789"
  }
}
```

---

### 10. Get My Learnings
**GET** `/my-learnings`

Get user's purchased courses with optional status filter.

**Authentication Required:** Yes

**Query Parameters:**
- `status` (string, optional): Filter by status ('onprogress', 'completed')

**Example Request:**
```
GET /api/my-learnings?status=onprogress
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_courses": 3,
    "completed_courses": 1,
    "in_progress_courses": 2,
    "completion_rate": 33.33
  },
  "filter_applied": "onprogress",
  "learnings": [
    {
      "purchase_id": 1,
      "program": {
        "id": 1,
        "type": "program",
        "title": "Full Stack Web Development Bootcamp",
        "subtitle": "Master MERN Stack Development",
        "description": "Complete full-stack web development course...",
        "category": {
          "id": 1,
          "name": "Web Development"
        },
        "image": "/media/program_images/image.jpg",
        "duration": "16 weeks",
        "program_rating": 4.8,
        "is_best_seller": true,
        "enrolled_students": 1250,
        "pricing": {
          "original_price": 599.00,
          "discount_percentage": 20.00,
          "discounted_price": 479.20,
          "savings": 119.80
        }
      },
      "purchase_date": "2024-01-15T10:30:00Z",
      "progress": {
        "percentage": 65.5,
        "status": "onprogress",
        "completed_modules": 6,
        "total_modules": 10,
        "estimated_completion": "2-3 weeks"
      }
    }
  ]
}
```

---

### 11. Update Learning Progress
**POST** `/learning/update-progress`

Update user's progress for a specific topic/video.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "topic_type": "topic",
  "topic_id": 1,
  "watch_time_seconds": 1200,
  "total_duration_seconds": 1800
}
```

**Response:**
```json
{
  "success": true,
  "message": "Progress updated successfully!",
  "topic_progress": {
    "topic_title": "HTML5 Semantic Elements",
    "status": "in_progress",
    "completion_percentage": 66.67,
    "watch_time_seconds": 1200,
    "total_duration_seconds": 1800,
    "is_completed": false
  },
  "course_progress": {
    "completion_percentage": 25.5,
    "completed_topics": 3,
    "total_topics": 15,
    "is_completed": false
  }
}
```

---

### 12. Get Course Learning Details
**GET** `/learning/course/{purchase_id}`

Get detailed learning information for a specific purchased course with all topics and progress.

**Authentication Required:** Yes

**Path Parameters:**
- `purchase_id`: Purchase ID

**Example Request:**
```
GET /api/learning/course/1
```

**Response:**
```json
{
  "success": true,
  "purchase": {
    "id": 1,
    "program_type": "program",
    "purchase_date": "2024-01-15T10:30:00Z",
    "status": "completed"
  },
  "program": {
    "id": 1,
    "type": "program",
    "title": "Full Stack Web Development Bootcamp",
    "subtitle": "Master MERN Stack Development",
    "category": {
      "id": 1,
      "name": "Web Development"
    },
    "image": "/media/program_images/image.jpg",
    "duration": "16 weeks",
    "program_rating": 4.8,
    "is_best_seller": true
  },
  "course_progress": {
    "completion_percentage": 65.5,
    "completed_topics": 10,
    "total_topics": 15,
    "is_completed": false,
    "started_at": "2024-01-15T10:30:00Z",
    "last_activity_at": "2024-01-20T14:45:00Z"
  },
  "syllabus": {
    "total_modules": 4,
    "modules": [
      {
        "id": 1,
        "module_title": "Frontend Fundamentals",
        "topics": [
          {
            "id": 1,
            "topic_title": "HTML5 Semantic Elements",
            "video_url": "https://example.com/video1",
            "progress": {
              "status": "completed",
              "completion_percentage": 100.0,
              "watch_time_seconds": 1800,
              "total_duration_seconds": 1800,
              "last_watched_at": "2024-01-16T09:30:00Z"
            }
          }
        ]
      }
    ]
  }
}
```

---

## Data Models

### Program Object
```json
{
  "id": 1,
  "type": "program",
  "title": "Full Stack Web Development Bootcamp",
  "subtitle": "Master MERN Stack Development",
  "description": "Complete full-stack web development course...",
  "category": {
    "id": 1,
    "name": "Web Development"
  },
  "image": "/media/program_images/image.jpg",
  "duration": "16 weeks",
  "program_rating": 4.8,
  "is_best_seller": true,
  "enrolled_students": 1250,
  "pricing": {
    "original_price": 599.00,
    "discount_percentage": 20.00,
    "discounted_price": 479.20,
    "savings": 119.80
  }
}
```

### Advanced Program Object
```json
{
  "id": 1,
  "type": "advanced_program",
  "title": "AI & Machine Learning Expert Track",
  "subtitle": "Advanced Deep Learning & Neural Networks",
  "description": "Advanced course covering deep learning...",
  "category": null,
  "image": "/media/advance_program_images/image.jpg",
  "duration": "24 weeks",
  "program_rating": 4.9,
  "is_best_seller": true,
  "enrolled_students": 450,
  "pricing": {
    "original_price": 1299.00,
    "discount_percentage": 30.00,
    "discounted_price": 909.30,
    "savings": 389.70
  }
}
```

### Topic Progress Object
```json
{
  "status": "in_progress",
  "completion_percentage": 75.5,
  "watch_time_seconds": 1350,
  "total_duration_seconds": 1800,
  "last_watched_at": "2024-01-20T14:45:00Z"
}
```

---

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "success": false,
  "message": "Error description"
}
```

Common HTTP status codes:
- `400` - Bad Request (Invalid parameters, validation errors)
- `401` - Unauthorized (Missing or invalid authentication)
- `404` - Not Found (Resource not found)
- `500` - Internal Server Error

---

## Authentication Notes

- JWT tokens are required for endpoints marked as "Authentication Required: Yes"
- Tokens should be included in the Authorization header as: `Bearer <token>`
- For endpoints that don't require authentication, providing a token may unlock additional features (e.g., continue_watching in landing endpoint)
- Invalid or expired tokens will result in 401 Unauthorized responses

---

## Important Features

### Landing Page Data Structure
The landing endpoint returns 6 different sections:
1. **`top_course`** - Highest rated programs (rating ≥ 4.0), max 5 items
2. **`recently_added`** - Latest programs by ID, max 5 items
3. **`featured`** - Best seller programs, max 5 items
4. **`programs`** - Regular programs only, max 5 items
5. **`advanced_programs`** - Advanced programs only, max 5 items
6. **`continue_watching`** - Recently watched programs for authenticated users, max 2 items

### Video Access Rules
- **Regular Programs**: Intro videos (`is_intro: true`) are always accessible
- **Advanced Programs**: All videos require purchase
- **Purchased Courses**: All videos accessible with progress tracking
- **Locked Content**: No `video_url` field included in response

### Payment Gateway
- Uses dummy payment gateway with 90% success rate
- All successful purchases have `status: "completed"`
- Transaction IDs are auto-generated

### Progress Tracking
- Videos considered completed at 90% watch time
- Progress updates in real-time
- Course completion based on topic completion
- Time tracking in seconds and formatted strings

---

This API provides a complete learning platform with course browsing, purchasing, progress tracking, and personalized recommendations.