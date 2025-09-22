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

Get landing page data with different program groups. Returns top courses, recently added programs, featured programs, regular programs, advanced programs, and continue watching.

**Authentication Required:** Yes

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
        "is_bookmarked": true,
        "enrolled_students": 1250,
        "pricing": {
          "original_price": 599.00,
          "discount_percentage": 20.00,
          "discounted_price": 479.20,
          "savings": 119.80
        }
      }
    ],
    "recently_added": [
      {
        "id": 3,
        "type": "program",
        "title": "React Native Mobile Development",
        "subtitle": "Build iOS & Android Apps",
        "description": "Learn to build cross-platform mobile applications using React Native...",
        "category": {
          "id": 3,
          "name": "Mobile Development"
        },
        "image": "/media/program_images/react_native.jpg",
        "duration": "10 weeks",
        "program_rating": 4.6,
        "is_best_seller": false,
        "is_bookmarked": false,
        "enrolled_students": 892,
        "pricing": {
          "original_price": 449.00,
          "discount_percentage": 10.00,
          "discounted_price": 404.10,
          "savings": 44.90
        }
      },
      {
        "id": 4,
        "type": "advanced_program",
        "title": "Blockchain & Web3 Development",
        "subtitle": "Smart Contracts & DeFi Applications",
        "description": "Advanced blockchain development covering Ethereum, Solidity...",
        "category": null,
        "image": "/media/advance_program_images/blockchain.jpg",
        "duration": "18 weeks",
        "program_rating": 4.7,
        "is_best_seller": false,
        "is_bookmarked": true,
        "enrolled_students": 234,
        "pricing": {
          "original_price": 899.00,
          "discount_percentage": 15.00,
          "discounted_price": 764.15,
          "savings": 134.85
        }
      }
    ],
    "featured": [
      {
        "id": 2,
        "type": "program",
        "title": "Python Data Science Masterclass",
        "subtitle": "From Beginner to Data Scientist",
        "description": "Comprehensive data science course covering Python, NumPy, Pandas...",
        "category": {
          "id": 2,
          "name": "Data Science"
        },
        "image": "/media/program_images/python_ds.jpg",
        "duration": "12 weeks",
        "program_rating": 4.7,
        "is_best_seller": true,
        "is_bookmarked": true,
        "enrolled_students": 1567,
        "pricing": {
          "original_price": 499.00,
          "discount_percentage": 15.00,
          "discounted_price": 424.15,
          "savings": 74.85
        }
      },
      {
        "id": 5,
        "type": "advanced_program",
        "title": "AI & Machine Learning Expert Track",
        "subtitle": "Advanced Deep Learning & Neural Networks",
        "description": "Advanced course covering deep learning, neural networks, computer vision...",
        "category": null,
        "image": "/media/advance_program_images/ai_ml.jpg",
        "duration": "24 weeks",
        "program_rating": 4.9,
        "is_best_seller": true,
        "is_bookmarked": false,
        "enrolled_students": 678,
        "pricing": {
          "original_price": 1299.00,
          "discount_percentage": 30.00,
          "discounted_price": 909.30,
          "savings": 389.70
        }
      }
    ],
    "programs": [
      {
        "id": 1,
        "type": "program",
        "title": "Full Stack Web Development Bootcamp",
        "subtitle": "Master MERN Stack Development",
        "description": "Complete full-stack web development course covering HTML, CSS, JavaScript, React...",
        "category": {
          "id": 1,
          "name": "Web Development"
        },
        "image": "/media/program_images/fullstack.jpg",
        "duration": "16 weeks",
        "program_rating": 4.8,
        "is_best_seller": true,
        "is_bookmarked": true,
        "enrolled_students": 1250,
        "pricing": {
          "original_price": 599.00,
          "discount_percentage": 20.00,
          "discounted_price": 479.20,
          "savings": 119.80
        }
      },
      {
        "id": 6,
        "type": "program",
        "title": "DevOps Engineering Complete Course",
        "subtitle": "Master CI/CD and Cloud Technologies",
        "description": "Complete DevOps course covering Git, Docker, Kubernetes, Jenkins, AWS...",
        "category": {
          "id": 4,
          "name": "DevOps"
        },
        "image": "/media/program_images/devops.jpg",
        "duration": "14 weeks",
        "program_rating": 4.9,
        "is_best_seller": true,
        "is_bookmarked": false,
        "enrolled_students": 934,
        "pricing": {
          "original_price": 699.00,
          "discount_percentage": 25.00,
          "discounted_price": 524.25,
          "savings": 174.75
        }
      }
    ],
    "advanced_programs": [
      {
        "id": 7,
        "type": "advanced_program",
        "title": "Enterprise Architecture & System Design",
        "subtitle": "Scalable Systems for Senior Engineers",
        "description": "Advanced system design course for senior engineers. Learn to design scalable...",
        "category": null,
        "image": "/media/advance_program_images/architecture.jpg",
        "duration": "20 weeks",
        "program_rating": 4.8,
        "is_best_seller": true,
        "is_bookmarked": true,
        "enrolled_students": 456,
        "pricing": {
          "original_price": 999.00,
          "discount_percentage": 20.00,
          "discounted_price": 799.20,
          "savings": 199.80
        }
      },
      {
        "id": 8,
        "type": "advanced_program",
        "title": "Cloud Security & DevSecOps",
        "subtitle": "Advanced Security for Cloud Environments",
        "description": "Master cloud security, DevSecOps practices, and advanced cybersecurity...",
        "category": null,
        "image": "/media/advance_program_images/cloud_security.jpg",
        "duration": "16 weeks",
        "program_rating": 4.6,
        "is_best_seller": false,
        "is_bookmarked": false,
        "enrolled_students": 289,
        "pricing": {
          "original_price": 799.00,
          "discount_percentage": 18.00,
          "discounted_price": 655.18,
          "savings": 143.82
        }
      }
    ],
    "continue_watching": [
      {
        "id": 1,
        "type": "program",
        "title": "Python Data Science Masterclass",
        "is_bookmarked": false,
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
- All programs include `is_bookmarked` status for authenticated user
- `continue_watching` shows recently watched programs with progress information

---

### 4. Filter Programs
**GET** `/programs/filter`

Get all programs (regular and advanced) with comprehensive filtering options.

**Authentication Required:** Yes

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
  "programs": [
    {
      "id": 1,
      "type": "program",
      "title": "Full Stack Web Development Bootcamp",
      "subtitle": "Master MERN Stack Development",
      "description": "Complete full-stack web development course covering HTML, CSS, JavaScript, React, Node.js, Express, and MongoDB.",
      "category": {
        "id": 1,
        "name": "Web Development"
      },
      "image": "/media/program_images/fullstack.jpg",
      "duration": "16 weeks",
      "program_rating": 4.8,
      "is_best_seller": true,
      "is_bookmarked": false,
      "enrolled_students": 1250,
      "pricing": {
        "original_price": 599.00,
        "discount_percentage": 20.00,
        "discounted_price": 479.20,
        "savings": 119.80
      }
    },
    {
      "id": 2,
      "type": "program",
      "title": "Python Data Science Masterclass",
      "subtitle": "From Beginner to Data Scientist",
      "description": "Comprehensive data science course covering Python, NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn, and machine learning algorithms.",
      "category": {
        "id": 2,
        "name": "Data Science"
      },
      "image": "/media/program_images/python_ds.jpg",
      "duration": "12 weeks",
      "program_rating": 4.7,
      "is_best_seller": true,
      "is_bookmarked": true,
      "enrolled_students": 1567,
      "pricing": {
        "original_price": 499.00,
        "discount_percentage": 15.00,
        "discounted_price": 424.15,
        "savings": 74.85
      }
    }
  ]
}
```

---

### 5. Get Program Details
**GET** `/program/{program_type}/{program_id}/details`

Get detailed information about a specific program including syllabus and topics.

**Authentication Required:** Yes

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
    "is_bookmarked": true,
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
            "video_url": "/media/program/Master_MERN_Stack_Development/intro.mp4",
            "video_duration": "15:32"
          },
          {
            "id": 2,
            "topic_title": "CSS3 Flexbox and Grid",
            "video_url": "/media/program/Master_MERN_Stack_Development/css_flexbox.mp4",
            "video_duration": "22:45"
          },
          {
            "id": 3,
            "topic_title": "JavaScript ES6+ Features",
            "video_url": "",
            "video_duration": null
          },
          {
            "id": 4,
            "topic_title": "DOM Manipulation",
            "video_url": "",
            "video_duration": null
          }
        ]
      },
      {
        "id": 2,
        "module_title": "React Development",
        "topics_count": 4,
        "topics": [
          {
            "id": 5,
            "topic_title": "React Components & JSX",
            "video_url": "",
            "video_duration": null
          },
          {
            "id": 6,
            "topic_title": "State Management with Hooks",
            "video_url": "",
            "video_duration": null
          },
          {
            "id": 7,
            "topic_title": "React Router & Navigation",
            "video_url": "",
            "video_duration": null
          },
          {
            "id": 8,
            "topic_title": "Context API & Redux",
            "video_url": "",
            "video_duration": null
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
    },
    {
      "bookmark_id": 2,
      "program": {
        "id": 3,
        "type": "advanced_program",
        "title": "AI & Machine Learning Expert Track",
        "subtitle": "Advanced Deep Learning & Neural Networks",
        "description": "Advanced course covering deep learning, neural networks, computer vision, NLP, and AI deployment.",
        "category": null,
        "image": "/media/advance_program_images/ai_ml.jpg",
        "duration": "24 weeks",
        "program_rating": 4.9,
        "is_best_seller": true,
        "enrolled_students": 678,
        "pricing": {
          "original_price": 1299.00,
          "discount_percentage": 30.00,
          "discounted_price": 909.30,
          "savings": 389.70
        }
      },
      "bookmarked_date": "2024-01-12T08:15:00Z"
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
        "is_bookmarked": true,
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
        "completed_modules": 2,
        "total_modules": 4
      }
    },
    {
      "purchase_id": 2,
      "program": {
        "id": 2,
        "type": "program",
        "title": "Python Data Science Masterclass",
        "subtitle": "From Beginner to Data Scientist",
        "description": "Comprehensive data science course covering Python, NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn, and machine learning algorithms.",
        "category": {
          "id": 2,
          "name": "Data Science"
        },
        "image": "/media/program_images/python_ds.jpg",
        "duration": "12 weeks",
        "program_rating": 4.7,
        "is_best_seller": true,
        "is_bookmarked": true,
        "enrolled_students": 1567,
        "pricing": {
          "original_price": 499.00,
          "discount_percentage": 15.00,
          "discounted_price": 424.15,
          "savings": 74.85
        }
      },
      "purchase_date": "2024-01-10T14:22:00Z",
      "progress": {
        "percentage": 100.0,
        "status": "completed",
        "completed_modules": 3,
        "total_modules": 3
      }
    },
    {
      "purchase_id": 3,
      "program": {
        "id": 5,
        "type": "advanced_program",
        "title": "Enterprise Architecture & System Design",
        "subtitle": "Scalable Systems for Senior Engineers",
        "description": "Advanced system design course for senior engineers. Learn to design scalable, distributed systems, microservices architecture.",
        "category": null,
        "image": "/media/advance_program_images/architecture.jpg",
        "duration": "20 weeks",
        "program_rating": 4.8,
        "is_best_seller": true,
        "is_bookmarked": false,
        "enrolled_students": 456,
        "pricing": {
          "original_price": 999.00,
          "discount_percentage": 20.00,
          "discounted_price": 799.20,
          "savings": 199.80
        }
      },
      "purchase_date": "2024-01-08T11:45:00Z",
      "progress": {
        "percentage": 25.0,
        "status": "onprogress",
        "completed_modules": 1,
        "total_modules": 5
      }
    }
  ]
}
```

---

### 11. Update Learning Progress
**POST** `/learning/update-progress`

Update user's progress for a specific topic/video. Video duration is automatically retrieved from database.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "program_type": "program",
  "topic_id": 1,
  "purchase_id": 5,
  "watch_time_seconds": 1200
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
    "is_completed": false,
    "last_watched_at": "2024-01-15T10:30:00Z"
  },
  "course_progress": {
    "completion_percentage": 25.5,
    "completed_topics": 3,
    "total_topics": 15,
    "is_completed": false
  }
}
```

**Notes:**
- `total_duration_seconds` is automatically retrieved from video duration stored in database
- `program_type` should match the purchase program type ('program' or 'advanced_program')
- `purchase_id` ensures security and correct program context
- Progress is considered completed at 90% watch time

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

- **All API endpoints now require JWT authentication**
- Tokens must be included in the Authorization header as: `Bearer <token>`
- Invalid or expired tokens will result in 401 Unauthorized responses
- Authentication provides personalized responses including bookmarks and progress tracking

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
- **Intro Videos**: Always accessible regardless of purchase status (`is_intro: true`)
- **Regular Videos**: Only accessible after course purchase
- **Video URLs**: Empty string when not accessible, full URL when accessible
- **Video Duration**: Automatically calculated and stored during upload

### Bookmark System
- **Universal Bookmarking**: All endpoints include `is_bookmarked` status
- **Real-time Status**: Bookmark status reflects current user's bookmarks
- **Consistent Experience**: Same bookmark interface across all program lists

### Payment Gateway
- Uses dummy payment gateway with 90% success rate
- All successful purchases have `status: "completed"`
- Transaction IDs are auto-generated

### Progress Tracking
- **Smart Duration**: Video duration automatically retrieved from database
- **90% Completion Rule**: Videos considered completed at 90% watch time
- **Real-time Updates**: Progress updates immediately
- **Course Progress**: Based on actual module/topic counts from syllabus
- **Secure Updates**: Requires purchase_id and program_type validation

### Video Management
- **Organized Storage**: Videos stored by program subtitle in `/media/program/Program_Name/`
- **Duration Calculation**: Automatic duration extraction during upload using OpenCV/MoviePy
- **Format Support**: Supports MM:SS and HH:MM:SS duration formats

---

This API provides a complete learning platform with course browsing, purchasing, progress tracking, and personalized recommendations.