# TopGrade API Documentation

## Overview
This document covers all API endpoints available in the TopGrade learning platform. All endpoints are prefixed with `/api/`.

## Authentication
Most endpoints require authentication using Bearer token in the Authorization header:
```
Authorization: Bearer <your_token>
```

---

## 🔐 Authentication Endpoints

### 1. Add Area of Interest
**POST** `/api/add-area-of-interest`
- **Auth Required**: Yes
- **Purpose**: Update user's area of interest
- **Request Body**:
  ```json
  {
    "area_of_intrest": "Data Science"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Area of interest updated successfully",
    "area_of_intrest": "Data Science"
  }
  ```

---

## 📚 Program & Course Endpoints

### 2. Get Categories
**GET** `/api/categories`
- **Auth Required**: No
- **Purpose**: Get list of all course categories
- **Response**:
  ```json
  {
    "success": true,
    "count": 5,
    "categories": [
      {
        "id": 1,
        "name": "Programming",
        "description": "Programming courses",
        "icon": "code-icon",
        "created_at": "2023-12-01T10:30:00Z",
        "updated_at": "2023-12-01T10:30:00Z"
      }
    ]
  }
  ```

### 3. Filter Programs
**GET** `/api/programs/filter`
- **Auth Required**: No
- **Purpose**: Get all programs with comprehensive filtering
- **Query Parameters**:
  - `program_type` (optional): 'program', 'advanced_program', or leave empty for all
  - `category_id` (optional): Filter by category ID
  - `is_best_seller` (optional): true/false
  - `min_price` (optional): Minimum price
  - `max_price` (optional): Maximum price
  - `min_rating` (optional): Minimum rating (0-5)
  - `search` (optional): Search in title/description
  - `sort_by` (optional): 'most_relevant', 'recently_added', 'top_rated', 'title', 'price', 'program_rating', 'available_slots', 'discounted_price'
  - `sort_order` (optional): 'asc' or 'desc'

- **Example**: `/api/programs/filter?program_type=program&category_id=1&min_price=1000&sort_by=price`

- **Response**:
  ```json
  {
    "success": true,
    "filters_applied": {
      "program_type": "program",
      "category_id": "1",
      "min_price": "1000",
      "sort_by": "price",
      "sort_order": "asc"
    },
    "statistics": {
      "total_count": 15,
      "regular_programs_count": 8,
      "advanced_programs_count": 7
    },
    "programs": [
      {
        "id": 1,
        "type": "program",
        "title": "Python Programming",
        "subtitle": "Learn Python from scratch",
        "description": "Complete Python course...",
        "category": {
          "id": 1,
          "name": "Programming",
          "icon": "code-icon"
        },
        "image": "https://example.com/image.jpg",
        "batch_starts": "January 2024",
        "available_slots": 50,
        "duration": "3 months",
        "program_rating": 4.5,
        "job_openings": "10,000+",
        "global_market_size": "$50B",
        "avg_annual_salary": "$80,000",
        "is_best_seller": true,
        "enrolled_students": 847,
        "price": 5000.00,
        "discount_percentage": 20.00,
        "discounted_price": 4000.00
      }
    ]
  }
  ```

### 4. Get Program Details
**GET** `/api/program/{program_type}/{program_id}/details`
- **Auth Required**: Optional (affects video access)
- **Purpose**: Get detailed information about a specific program
- **Path Parameters**:
  - `program_type`: 'program' or 'advanced-program'
  - `program_id`: Program ID
- **Example**: `/api/program/program/123/details`

- **Response**:
  ```json
  {
    "success": true,
    "program": {
      "id": 123,
      "type": "program",
      "title": "Python Programming",
      "subtitle": "Learn Python from scratch",
      "description": "Complete Python course...",
      "category": {
        "id": 1,
        "name": "Programming",
        "description": "Programming courses",
        "icon": "code-icon"
      },
      "image": "https://example.com/image.jpg",
      "batch_starts": "January 2024",
      "available_slots": 50,
      "duration": "3 months",
      "program_rating": 4.5,
      "job_openings": "10,000+",
      "global_market_size": "$50B",
      "avg_annual_salary": "$80,000",
      "is_best_seller": true,
      "enrolled_students": 847,
      "pricing": {
        "original_price": 5000.00,
        "discount_percentage": 20.00,
        "discounted_price": 4000.00,
        "savings": 1000.00
      },
      "syllabus": {
        "total_modules": 5,
        "total_topics": 25,
        "modules": [
          {
            "id": 1,
            "module_title": "Introduction to Python",
            "topics_count": 5,
            "topics": [
              {
                "id": 101,
                "topic_title": "Variables and Data Types",
                "is_free_trail": true,
                "is_intro": true,
                "is_locked": false,
                "video_url": "https://youtube.com/watch?v=abc123"
              },
              {
                "id": 102,
                "topic_title": "Advanced Concepts",
                "is_free_trail": false,
                "is_intro": false,
                "is_locked": true
                // Note: No video_url for locked content
              }
            ]
          }
        ]
      }
    }
  }
  ```

**Important Notes for Video Access**:
- **Intro videos** (`is_intro: true`): Always accessible, even without purchase
- **Regular videos**: Locked until user purchases the course
- **Advanced programs**: All videos locked until purchase (no intro exception)
- **Locked videos**: No `video_url` field in response
- **Purchased courses**: All videos accessible with `video_url` field

---

## 🛒 Purchase & Bookmark Endpoints

### 5. Purchase Course
**POST** `/api/purchase`
- **Auth Required**: Yes
- **Purpose**: Purchase a program or advanced program
- **Request Body**:
  ```json
  {
    "program_type": "program",
    "program_id": 123,
    "payment_method": "card"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Course purchased successfully!",
    "purchase": {
      "id": 456,
      "program_type": "program",
      "program_title": "Python Programming",
      "original_price": 5000.00,
      "discount_percentage": 20.00,
      "final_price": 4000.00,
      "savings": 1000.00,
      "purchase_date": "2023-12-01T10:30:00Z",
      "status": "completed",
      "transaction_id": "ABC123DEF456"
    }
  }
  ```

### 6. Add to Bookmark
**POST** `/api/bookmark`
- **Auth Required**: Yes
- **Purpose**: Add a course to user's bookmarks
- **Request Body**:
  ```json
  {
    "program_type": "program",
    "program_id": 123
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Course added to bookmarks successfully!",
    "bookmark": {
      "id": 789,
      "program_type": "program",
      "program_title": "Python Programming",
      "program_id": 123,
      "bookmarked_date": "2023-12-01T10:30:00Z"
    }
  }
  ```

### 7. Remove from Bookmark
**DELETE** `/api/bookmark`
- **Auth Required**: Yes
- **Purpose**: Remove a course from user's bookmarks
- **Request Body**: Same as add bookmark
- **Response**:
  ```json
  {
    "success": true,
    "message": "Python Programming removed from bookmarks successfully!"
  }
  ```

### 8. Get User Bookmarks
**GET** `/api/bookmarks`
- **Auth Required**: Yes
- **Purpose**: Get all bookmarked courses for the user
- **Response**:
  ```json
  {
    "success": true,
    "count": 3,
    "bookmarks": [
      {
        "bookmark_id": 789,
        "program_type": "program",
        "program": {
          "id": 123,
          "title": "Python Programming",
          "subtitle": "Learn Python from scratch",
          "category": {
            "id": 1,
            "name": "Programming",
            "icon": "code-icon"
          },
          "image": "https://example.com/image.jpg",
          "price": 5000.00,
          "discount_percentage": 20.00,
          "discounted_price": 4000.00,
          "program_rating": 4.5,
          "is_best_seller": true
        },
        "bookmarked_date": "2023-12-01T10:30:00Z"
      }
    ]
  }
  ```

---

## 📖 Learning Progress Endpoints

### 9. Get My Learnings
**GET** `/api/my-learnings`
- **Auth Required**: Yes
- **Purpose**: Get user's purchased courses with progress
- **Query Parameters**:
  - `status` (optional): 'onprogress', 'completed', or leave empty for all

- **Example**: `/api/my-learnings?status=onprogress`

- **Response**:
  ```json
  {
    "success": true,
    "statistics": {
      "total_courses": 5,
      "completed_courses": 2,
      "in_progress_courses": 3,
      "completion_rate": 40.0,
      "total_watch_time": "15h 45m",
      "total_topics_completed": 45
    },
    "filter_applied": "onprogress",
    "learnings": [
      {
        "purchase_id": 456,
        "program_type": "program",
        "program": {
          "id": 123,
          "title": "Python Programming",
          "category": {
            "id": 1,
            "name": "Programming",
            "icon": "code-icon"
          },
          "price": 5000.00,
          "discounted_price": 4000.00
        },
        "purchase_date": "2023-11-15T10:30:00Z",
        "progress": {
          "percentage": 65.5,
          "status": "onprogress",
          "completed_topics": 13,
          "total_topics": 20,
          "in_progress_topics": 3,
          "total_watch_time": "5h 30m",
          "total_watch_time_seconds": 19800,
          "started_at": "2023-11-15T10:30:00Z",
          "last_activity_at": "2023-12-01T14:20:00Z",
          "estimated_completion": "8 hours remaining"
        },
        "recent_topics": [
          {
            "topic_title": "Advanced Functions",
            "status": "in_progress",
            "completion_percentage": 75.0,
            "watch_time_seconds": 1350,
            "last_watched_at": "2023-12-01T14:20:00Z"
          }
        ]
      }
    ]
  }
  ```

### 10. Update Learning Progress
**POST** `/api/learning/update-progress`
- **Auth Required**: Yes
- **Purpose**: Update user's progress for a specific video/topic
- **Request Body**:
  ```json
  {
    "topic_id": 101,
    "topic_type": "topic",
    "watch_time_seconds": 1800,
    "total_duration_seconds": 2400
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Progress updated successfully!",
    "topic_progress": {
      "topic_title": "Introduction to Python",
      "status": "in_progress",
      "completion_percentage": 75.0,
      "watch_time_seconds": 1800,
      "total_duration_seconds": 2400,
      "is_completed": false
    },
    "course_progress": {
      "completion_percentage": 45.5,
      "completed_topics": 5,
      "total_topics": 11,
      "is_completed": false
    }
  }
  ```

### 11. Get Course Learning Details
**GET** `/api/learning/course/{purchase_id}`
- **Auth Required**: Yes
- **Purpose**: Get detailed learning information for a purchased course
- **Path Parameters**:
  - `purchase_id`: Purchase ID from my-learnings response

- **Example**: `/api/learning/course/456`

- **Response**:
  ```json
  {
    "success": true,
    "course": {
      "purchase_id": 456,
      "program_type": "program",
      "program_title": "Python Programming",
      "program_subtitle": "Learn Python from scratch",
      "program_description": "Complete Python course...",
      "program_image": "https://example.com/image.jpg",
      "purchase_date": "2023-11-15T10:30:00Z",
      "progress": {
        "completion_percentage": 65.5,
        "completed_topics": 13,
        "total_topics": 20,
        "in_progress_topics": 3,
        "total_watch_time": "5h 30m",
        "total_watch_time_seconds": 19800,
        "is_completed": false,
        "started_at": "2023-11-15T10:30:00Z",
        "last_activity_at": "2023-12-01T14:20:00Z"
      },
      "syllabus": [
        {
          "id": 1,
          "module_title": "Introduction",
          "topics_count": 5,
          "completed_topics": 3,
          "topics": [
            {
              "id": 101,
              "topic_title": "Variables and Data Types",
              "topic_type": "topic",
              "is_free_trail": true,
              "is_intro": true,
              "is_locked": false,
              "video_url": "https://youtube.com/watch?v=abc123",
              "progress": {
                "status": "completed",
                "completion_percentage": 100.0,
                "watch_time": "00:28:45",
                "watch_time_seconds": 1725,
                "total_duration": "30:00",
                "total_duration_seconds": 1800,
                "completed_at": "2023-11-20T15:30:00Z",
                "last_watched_at": "2023-11-20T15:30:00Z"
              }
            }
          ]
        }
      ]
    }
  }
  ```

---

## 🔄 Progress Status Types

### Topic Progress Status:
- **`not_started`**: Topic hasn't been watched yet
- **`in_progress`**: Topic is partially watched (< 90%)
- **`completed`**: Topic is fully watched (≥ 90%)

### Course Progress Status:
- **`onprogress`**: Course has started but not completed
- **`completed`**: All topics in the course are completed

---

## ⚠️ Common Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Invalid program_type. Must be 'program' or 'advanced_program'"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Authentication required"
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Program not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Error fetching programs: Database connection failed"
}
```

---

## 📝 Important Notes

### Video Access Rules:
1. **Regular Programs**:
   - Intro videos (`is_intro: true`) are always accessible
   - Other videos require purchase
   - Locked videos don't include `video_url` in response

2. **Advanced Programs**:
   - All videos require purchase
   - No free intro videos

3. **Purchased Courses**:
   - All videos accessible with `video_url`
   - Progress tracking available
   - Can update watch time

### Payment Gateway:
- Currently using dummy payment gateway (90% success rate)
- All successful purchases have `status: "completed"`
- Transaction IDs are auto-generated

### Filtering & Sorting:
- All filter parameters are optional
- Combine multiple filters for precise results
- Search works across title, subtitle, and description

#### Available Sorting Options:
- **`most_relevant`** (default): Best sellers first, then by highest rating, then by most enrolled students
- **`recently_added`**: Newest courses first (based on course ID)
- **`top_rated`**: Highest rated courses first, with enrollment count as tiebreaker
- **`title`**: Alphabetical order by course name
- **`price`**: By course price (original price)
- **`discounted_price`**: By final price after discount
- **`program_rating`**: By user rating (0-5 stars)
- **`available_slots`**: By number of available seats
- **`sort_order`**: Use 'asc' for ascending or 'desc' for descending (applies to price, rating, etc.)

### Progress Tracking:
- Videos considered completed at 90% watch time
- Progress updates in real-time
- Course completion based on topic completion
- Time tracking in seconds and formatted strings

---

## 🚀 Quick Start Guide

1. **Browse Courses**: Start with `/api/programs/filter` to get all available courses
2. **View Details**: Use `/api/program/{type}/{id}/details` to see course content
3. **Purchase**: Use `/api/purchase` to buy a course
4. **Learn**: Access `/api/learning/course/{purchase_id}` to start learning
5. **Track Progress**: Update progress with `/api/learning/update-progress`
6. **Monitor**: Check `/api/my-learnings` for overall progress

This API provides a complete learning platform with course browsing, purchasing, and progress tracking capabilities.