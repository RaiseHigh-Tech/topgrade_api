from ninja import NinjaAPI
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .schemas import AreaOfInterestSchema, PurchaseSchema, BookmarkSchema, UpdateProgressSchema
from .models import Program, AdvanceProgram, Category, UserPurchase, UserBookmark, UserCourseProgress, UserTopicProgress
from django.db import models
from django.utils import timezone
from typing import List
import random
import string

User = get_user_model()

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Validate the token
            UntypedToken(token)
            # Get user from token
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return user
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

# Initialize Django Ninja API for general endpoints
api = NinjaAPI(version="1.0.0", title="General API")

@api.post("/add-area-of-interest", auth=AuthBearer())
def add_area_of_interest(request, data: AreaOfInterestSchema):
    """
    Add area of interest for authenticated user
    """
    try:
        user = request.auth
        user.area_of_intrest = data.area_of_intrest
        user.save()
        
        return {
            "success": True,
            "message": "Area of interest updated successfully",
            "area_of_intrest": user.area_of_intrest
        }
    except Exception as e:
        return JsonResponse({"message": f"Error updating area of interest: {str(e)}"}, status=500)


@api.get("/categories", auth=AuthBearer())
def get_categories(request):
    """
    Get list of all categories
    """
    try:
        categories = Category.objects.all().order_by('name')
        
        categories_data = []
        for category in categories:
            category_data = {
                "id": category.id,
                "name": category.name,
            }
            categories_data.append(category_data)
        
        return {
            "success": True,
            "count": len(categories_data),
            "categories": categories_data
        }
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching categories: {str(e)}"}, status=500)

@api.get("/landing", auth=AuthBearer())
def get_landing_data(request):
    """
    Get landing page data with different program groups
    Returns: top_course, recently_added, featured, programs, advanced_programs
    Each group contains max 5 programs
    """
    try:
        def format_program_data(program, program_type, user):
            """Helper function to format program data consistently"""
            discounted_price = program.price
            if program.discount_percentage > 0:
                discounted_price = program.price * (1 - program.discount_percentage / 100)
            
            enrolled_students = 0
            if program_type == 'program':
                enrolled_students = UserPurchase.objects.filter(
                    program=program,
                    status='completed'
                ).count()
            else:
                enrolled_students = UserPurchase.objects.filter(
                    advanced_program=program,
                    status='completed'
                ).count()
            
            # Check if user has bookmarked this program
            is_bookmarked = False
            if program_type == 'program':
                is_bookmarked = UserBookmark.objects.filter(
                    user=user,
                    program_type='program',
                    program=program
                ).exists()
            else:
                is_bookmarked = UserBookmark.objects.filter(
                    user=user,
                    program_type='advanced_program',
                    advanced_program=program
                ).exists()
            
            return {
                "id": program.id,
                "type": program_type,
                "title": program.title,
                "subtitle": program.subtitle,
                "description": program.description,
                "category": {
                    "id": program.category.id,
                    "name": program.category.name,
                } if hasattr(program, 'category') and program.category else None,
                "image": program.image.url if program.image else None,
                "duration": program.duration,
                "program_rating": float(program.program_rating),
                "is_best_seller": program.is_best_seller,
                "is_bookmarked": is_bookmarked,
                "enrolled_students": enrolled_students,
                "pricing": {
                    "original_price": float(program.price),
                    "discount_percentage": float(program.discount_percentage),
                    "discounted_price": float(discounted_price),
                    "savings": float(program.price - discounted_price)
                },
            }
        
        # Get authenticated user
        user = request.auth
        
        # Top Courses - Highest rated programs (both regular and advanced)
        top_programs = Program.objects.filter(program_rating__gte=4.0).order_by('-program_rating', '-id')[:3]
        top_advanced = AdvanceProgram.objects.filter(program_rating__gte=4.0).order_by('-program_rating', '-id')[:2]
        
        top_course = []
        for program in top_programs:
            top_course.append(format_program_data(program, 'program', user))
        for program in top_advanced:
            top_course.append(format_program_data(program, 'advanced_program', user))
        
        # Recently Added - Latest programs by ID (assuming higher ID = newer)
        recent_programs = Program.objects.all().order_by('-id')[:3]
        recent_advanced = AdvanceProgram.objects.all().order_by('-id')[:2]
        
        recently_added = []
        for program in recent_programs:
            recently_added.append(format_program_data(program, 'program', user))
        for program in recent_advanced:
            recently_added.append(format_program_data(program, 'advanced_program', user))
        
        # Featured - Best seller programs
        featured_programs = Program.objects.filter(is_best_seller=True).order_by('-program_rating', '-id')[:3]
        featured_advanced = AdvanceProgram.objects.filter(is_best_seller=True).order_by('-program_rating', '-id')[:2]
        
        featured = []
        for program in featured_programs:
            featured.append(format_program_data(program, 'program', user))
        for program in featured_advanced:
            featured.append(format_program_data(program, 'advanced_program', user))
        
        # Programs - Regular programs only (max 5)
        regular_programs = Program.objects.all().order_by('-program_rating', '-id')[:5]
        programs = []
        for program in regular_programs:
            programs.append(format_program_data(program, 'program', user))
        
        # Advanced Programs - Advanced programs only (max 5)
        advance_programs = AdvanceProgram.objects.all().order_by('-program_rating', '-id')[:5]
        advanced_programs = []
        for program in advance_programs:
            advanced_programs.append(format_program_data(program, 'advanced_program', user))
        
        # Continue Watching - Recently watched programs for authenticated users only
        continue_watching = []
        
        if user:
            # Get user's recent topic progress (videos they've started but not completed)
            recent_progress = UserTopicProgress.objects.filter(
                user=user,
                status__in=['in_progress', 'completed']
            ).select_related(
                'purchase__program', 
                'purchase__advanced_program',
                'topic__syllabus__program',
                'advance_topic__advance_syllabus__advance_program'
            ).order_by('-last_watched_at')[:10]  # Get more to filter unique programs
            
            seen_programs = set()
            for progress in recent_progress:
                if len(continue_watching) >= 2:
                    break
                    
                # Get the program from the progress
                program = None
                program_type = None
                
                if progress.purchase.program_type == 'program' and progress.purchase.program:
                    program = progress.purchase.program
                    program_type = 'program'
                elif progress.purchase.program_type == 'advanced_program' and progress.purchase.advanced_program:
                    program = progress.purchase.advanced_program
                    program_type = 'advanced_program'
                
                if program and program.id not in seen_programs:
                    seen_programs.add(program.id)
                    
                    # Get course progress for this program
                    course_progress = UserCourseProgress.objects.filter(
                        user=user,
                        purchase=progress.purchase
                    ).first()
                    
                    program_data = format_program_data(program, program_type, user)
                    
                    # Add progress information
                    program_data['progress'] = {
                        "percentage": float(course_progress.completion_percentage) if course_progress else 0.0,
                        "status": "completed" if course_progress and course_progress.is_completed else "in_progress",
                        "last_watched_at": progress.last_watched_at.isoformat(),
                        "last_watched_topic": progress.topic.topic_title if progress.topic else progress.advance_topic.topic_title,
                        "completed_topics": course_progress.completed_topics if course_progress else 0,
                        "total_topics": course_progress.total_topics if course_progress else 0
                    }
                    
                    continue_watching.append(program_data)
        
        return {
            "success": True,
            "data": {
                "top_course": top_course[:5],  # Ensure max 5
                "recently_added": recently_added[:5],  # Ensure max 5
                "featured": featured[:5],  # Ensure max 5
                "programs": programs,  # Already limited to 5
                "advanced_programs": advanced_programs,  # Already limited to 5
                "continue_watching": continue_watching  # Max 5, empty if not authenticated
            },
            "counts": {
                "top_course": len(top_course[:5]),
                "recently_added": len(recently_added[:5]),
                "featured": len(featured[:5]),
                "programs": len(programs),
                "advanced_programs": len(advanced_programs),
                "continue_watching": len(continue_watching)
            }
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching landing data: {str(e)}"}, status=500)

@api.get("/programs/filter", auth=AuthBearer())
def get_all_programs_with_filters(
    request,
    program_type: str = None,
    category_id: int = None,
    is_best_seller: bool = None,
    min_price: float = None,
    max_price: float = None,
    min_rating: float = None,
    search: str = None,
    sort_by: str = 'most_relevant',
    sort_order: str = 'asc'
):
    """
    Get all programs (regular and advanced) with comprehensive filtering options
    """
    try:
        # Get authenticated user
        user = request.auth
        
        # Filter parameters are now function arguments
        # Convert string category_id to int if provided
        if category_id is not None:
            category_id = str(category_id)
        
        all_programs = []
        
        # Include regular programs
        if program_type in [None, 'all', 'program']:
            programs_query = Program.objects.all().select_related('category')
            
            # Apply category filter for regular programs
            if category_id is not None:
                try:
                    category = Category.objects.get(id=category_id)
                    programs_query = programs_query.filter(category=category)
                except Category.DoesNotExist:
                    pass  # Skip invalid category
            
            # Apply other filters
            if is_best_seller is not None:
                programs_query = programs_query.filter(is_best_seller=is_best_seller)
            
            if min_price is not None:
                programs_query = programs_query.filter(price__gte=min_price)
            
            if max_price is not None:
                programs_query = programs_query.filter(price__lte=max_price)
            
            if min_rating is not None:
                programs_query = programs_query.filter(program_rating__gte=min_rating)
            
            if search:
                programs_query = programs_query.filter(
                    models.Q(title__icontains=search) | 
                    models.Q(description__icontains=search) |
                    models.Q(subtitle__icontains=search)
                )
            
            # Convert regular programs to unified format
            for program in programs_query:
                discounted_price = program.price
                if program.discount_percentage > 0:
                    discounted_price = program.price * (1 - program.discount_percentage / 100)
                
                # Check if user has bookmarked this program
                is_bookmarked = UserBookmark.objects.filter(
                    user=user,
                    program_type='program',
                    program=program
                ).exists()
                
                program_data = {
                    "id": program.id,
                    "type": "program",
                    "title": program.title,
                    "subtitle": program.subtitle,
                    "description": program.description,
                    "category": {
                        "id": program.category.id,
                        "name": program.category.name,
                    } if program.category else None,
                    "image": program.image.url if program.image else None,
                    "duration": program.duration,
                    "program_rating": float(program.program_rating),
                    "is_best_seller": program.is_best_seller,
                    "is_bookmarked": is_bookmarked,
                    "enrolled_students": UserPurchase.objects.filter(
                        program=program,
                        status='completed'
                    ).count(),
                    "pricing": {
                        "original_price": float(program.price),
                        "discount_percentage": float(program.discount_percentage),
                        "discounted_price": float(discounted_price),
                        "savings": float(program.price - discounted_price)
                    },
                }
                all_programs.append(program_data)
        
        # Include advanced programs
        if program_type in [None, 'all', 'advanced_program']:
            advanced_programs_query = AdvanceProgram.objects.all()
            
            # Apply filters (category filter not applicable for advanced programs)
            if is_best_seller is not None:
                advanced_programs_query = advanced_programs_query.filter(is_best_seller=is_best_seller)
            
            if min_price is not None:
                advanced_programs_query = advanced_programs_query.filter(price__gte=min_price)
            
            if max_price is not None:
                advanced_programs_query = advanced_programs_query.filter(price__lte=max_price)
            
            if min_rating is not None:
                advanced_programs_query = advanced_programs_query.filter(program_rating__gte=min_rating)
            
            if search:
                advanced_programs_query = advanced_programs_query.filter(
                    models.Q(title__icontains=search) | 
                    models.Q(description__icontains=search) |
                    models.Q(subtitle__icontains=search)
                )
            
            # Convert advanced programs to unified format
            for program in advanced_programs_query:
                discounted_price = program.price
                if program.discount_percentage > 0:
                    discounted_price = program.price * (1 - program.discount_percentage / 100)
                
                # Check if user has bookmarked this advanced program
                is_bookmarked = UserBookmark.objects.filter(
                    user=user,
                    program_type='advanced_program',
                    advanced_program=program
                ).exists()
                
                program_data = {
                    "id": program.id,
                    "type": "advanced_program",
                    "title": program.title,
                    "subtitle": program.subtitle,
                    "description": program.description,
                    "category": None,  # Advanced programs don't have categories
                    "image": program.image.url if program.image else None,
                    "duration": program.duration,
                    "program_rating": float(program.program_rating),
                    "is_best_seller": program.is_best_seller,
                    "is_bookmarked": is_bookmarked,
                    "enrolled_students": UserPurchase.objects.filter(
                        advanced_program=program,
                        status='completed'
                    ).count(),
                    "pricing": {
                        "original_price": float(program.price),
                        "discount_percentage": float(program.discount_percentage),
                        "discounted_price": float(discounted_price),
                        "savings": float(program.price - discounted_price)
                    },
                }
                all_programs.append(program_data)
        
        # Apply sorting to combined results
        if sort_by in ['title', 'price', 'program_rating', 'available_slots', 'discounted_price', 'most_relevant', 'recently_added', 'top_rated']:
            reverse_order = sort_order == 'desc'
            
            if sort_by == 'most_relevant':
                # Sort by relevance: best sellers first, then by rating, then by enrolled students
                all_programs.sort(key=lambda x: (
                    not x.get('is_best_seller', False),  # Best sellers first (False sorts before True)
                    -x.get('program_rating', 0),         # Higher rating first
                    -x.get('enrolled_students', 0)       # More enrolled students first
                ))
            elif sort_by == 'recently_added':
                # Sort by creation date (newest first) - using ID as proxy for creation order
                all_programs.sort(key=lambda x: x.get('id', 0), reverse=True)
            elif sort_by == 'top_rated':
                # Sort by rating (highest first), then by number of enrolled students
                all_programs.sort(key=lambda x: (
                    -x.get('program_rating', 0),         # Higher rating first
                    -x.get('enrolled_students', 0)       # More enrolled students as tiebreaker
                ))
            else:
                # Standard sorting for other fields
                all_programs.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse_order)
        
        # Get filter statistics
        regular_count = sum(1 for p in all_programs if p['type'] == 'program')
        advanced_count = sum(1 for p in all_programs if p['type'] == 'advanced_program')
        
        return {
            "success": True,
            "filters_applied": {
                "program_type": program_type or 'all',
                "category_id": category_id,
                "is_best_seller": is_best_seller,
                "min_price": min_price,
                "max_price": max_price,
                "min_rating": min_rating,
                "search": search,
                "sort_by": sort_by,
                "sort_order": sort_order
            },
            "statistics": {
                "total_count": len(all_programs),
                "regular_programs_count": regular_count,
                "advanced_programs_count": advanced_count
            },
            "programs": all_programs
        }
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching filtered programs: {str(e)}"}, status=500)

@api.get("/program/{program_type}/{program_id}/details", auth=AuthBearer())
def get_program_details(request, program_type: str, program_id: int):
    """
    Get detailed information about a specific program (regular or advanced) including syllabus and topics
    """
    try:
        # Validate program type
        if program_type not in ['program', 'advanced-program']:
            return JsonResponse({
                "success": False, 
                "message": "Invalid program_type. Must be 'program' or 'advanced-program'"
            }, status=400)
        
        # Get program based on type
        try:
            if program_type == 'program':
                program = Program.objects.select_related('category').get(id=program_id)
                program_model_type = 'program'
            else:
                program = AdvanceProgram.objects.get(id=program_id)
                program_model_type = 'advanced_program'
        except (Program.DoesNotExist, AdvanceProgram.DoesNotExist):
            return JsonResponse({
                "success": False, 
                "message": f"{program_type.replace('-', ' ').title()} not found"
            }, status=404)
        
        # Calculate discounted price
        discounted_price = program.price
        if program.discount_percentage > 0:
            discounted_price = program.price * (1 - program.discount_percentage / 100)
        
        # Check if user has purchased this program (for video access)
        user = request.auth
        has_purchased = False
        is_bookmarked = False
        
        if user:
            if program_type == 'program':
                has_purchased = UserPurchase.objects.filter(
                    user=user,
                    program=program,
                    status='completed'
                ).exists()
                
                # Check if user has bookmarked this program
                is_bookmarked = UserBookmark.objects.filter(
                    user=user,
                    program_type='program',
                    program=program
                ).exists()
            else:
                has_purchased = UserPurchase.objects.filter(
                    user=user,
                    advanced_program=program,
                    status='completed'
                ).exists()
                
                # Check if user has bookmarked this advanced program
                is_bookmarked = UserBookmark.objects.filter(
                    user=user,
                    program_type='advanced_program',
                    advanced_program=program
                ).exists()
        
        # Get syllabus with topics
        syllabus_list = []
        syllabi = program.syllabuses.all().prefetch_related('topics')
        
        for syllabus in syllabi:
            topics_list = []
            for topic in syllabus.topics.all():
                if program_type == 'program':
                    # Regular programs have intro videos
                    is_accessible = has_purchased or topic.is_intro
                    topic_data = {
                        "id": topic.id,
                        "topic_title": topic.topic_title,
                        "is_free_trail": topic.is_free_trail,
                        "is_intro": topic.is_intro,
                        "is_locked": not is_accessible
                    }
                else:
                    # Advanced programs - all videos locked unless purchased
                    topic_data = {
                        "id": topic.id,
                        "topic_title": topic.topic_title,
                        "is_locked": not has_purchased
                    }
                    is_accessible = has_purchased
                
                # Only add video_url if accessible
                if is_accessible:
                    topic_data["video_url"] = topic.video_url
                
                topics_list.append(topic_data)
            
            syllabus_data = {
                "id": syllabus.id,
                "module_title": syllabus.module_title,
                "topics_count": len(topics_list),
                "topics": topics_list
            }
            syllabus_list.append(syllabus_data)
        
        # Build program data
        program_data = {
            "id": program.id,
            "type": program_model_type,
            "title": program.title,
            "subtitle": program.subtitle,
            "category": {
                "id": program.category.id,
                "name": program.category.name,
            } if program.category else None,
            "description": program.description,
            "image": program.image.url if program.image else None,
            "duration": program.duration,
            "program_rating": float(program.program_rating),
            "is_best_seller": program.is_best_seller,
            "is_bookmarked": is_bookmarked,
            "enrolled_students": UserPurchase.objects.filter(
                program=program,
                status='completed'
            ).count(),
            "pricing": {
                "original_price": float(program.price),
                "discount_percentage": float(program.discount_percentage),
                "discounted_price": float(discounted_price),
                "savings": float(program.price - discounted_price)
            },
        }
        
        return {
            "success": True,
            "program": program_data,
            "syllabus": {
                "total_modules": len(syllabus_list),
                "total_topics": sum(len(s["topics"]) for s in syllabus_list),
                "modules": syllabus_list
            }
        }
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching program details: {str(e)}"}, status=500)

@api.post("/bookmark", auth=AuthBearer())
def add_to_bookmark(request, data: BookmarkSchema):
    """
    Add a course (program or advanced program) to user's bookmarks
    """
    try:
        user = request.auth
        
        # Get request data from schema
        program_type = data.program_type  # 'program' or 'advanced_program'
        program_id = data.program_id
        
        # Validate input
        if program_type not in ['program', 'advanced_program']:
            return JsonResponse({"success": False, "message": "Invalid program_type. Must be 'program' or 'advanced_program'"}, status=400)
        
        # Get the program
        try:
            if program_type == 'program':
                program = Program.objects.get(id=program_id)
                program_obj = program
                advanced_program_obj = None
            else:
                program = AdvanceProgram.objects.get(id=program_id)
                program_obj = None
                advanced_program_obj = program
        except (Program.DoesNotExist, AdvanceProgram.DoesNotExist):
            return JsonResponse({"success": False, "message": "Program not found"}, status=404)
        
        # Check if already bookmarked
        existing_bookmark = UserBookmark.objects.filter(
            user=user,
            program_type=program_type,
            program=program_obj,
            advanced_program=advanced_program_obj
        ).first()
        
        if existing_bookmark:
            return JsonResponse({
                "success": False,
                "message": "Course is already in your bookmarks"
            }, status=400)
        
        # Create bookmark
        bookmark = UserBookmark.objects.create(
            user=user,
            program_type=program_type,
            program=program_obj,
            advanced_program=advanced_program_obj,
            bookmarked_date=timezone.now()
        )
        
        return {
            "success": True,
            "message": "Course added to bookmarks successfully!",
            "bookmark": {
                "id": bookmark.id,
                "program_type": bookmark.program_type,
                "program_title": program.title,
                "program_id": program.id,
                "bookmarked_date": bookmark.bookmarked_date.isoformat()
            }
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error adding bookmark: {str(e)}"}, status=500)

@api.delete("/bookmark", auth=AuthBearer())
def remove_from_bookmark(request, data: BookmarkSchema):
    """
    Remove a course from user's bookmarks
    """
    try:
        user = request.auth
        
        # Get request data from schema
        program_type = data.program_type
        program_id = data.program_id
        
        # Validate input
        if program_type not in ['program', 'advanced_program']:
            return JsonResponse({"success": False, "message": "Invalid program_type. Must be 'program' or 'advanced_program'"}, status=400)
        
        # Get the program objects
        try:
            if program_type == 'program':
                program_obj = Program.objects.get(id=program_id)
                advanced_program_obj = None
            else:
                program_obj = None
                advanced_program_obj = AdvanceProgram.objects.get(id=program_id)
        except (Program.DoesNotExist, AdvanceProgram.DoesNotExist):
            return JsonResponse({"success": False, "message": "Program not found"}, status=404)
        
        # Find and delete bookmark
        bookmark = UserBookmark.objects.filter(
            user=user,
            program_type=program_type,
            program=program_obj,
            advanced_program=advanced_program_obj
        ).first()
        
        if not bookmark:
            return JsonResponse({
                "success": False,
                "message": "Course is not in your bookmarks"
            }, status=404)
        
        program_title = program_obj.title if program_obj else advanced_program_obj.title
        bookmark.delete()
        
        return {
            "success": True,
            "message": f"'{program_title}' removed from bookmarks successfully!"
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error removing bookmark: {str(e)}"}, status=500)

@api.get("/bookmarks", auth=AuthBearer())
def get_user_bookmarks(request):
    """
    Get all bookmarks for the authenticated user
    """
    try:
        user = request.auth
        
        # Get all user bookmarks
        bookmarks = UserBookmark.objects.filter(user=user).order_by('-bookmarked_date')
        
        bookmarks_data = []
        for bookmark in bookmarks:
            if bookmark.program_type == 'program' and bookmark.program:
                program = bookmark.program
                # Calculate discounted price
                discounted_price = program.price
                if program.discount_percentage > 0:
                    discounted_price = program.price * (1 - program.discount_percentage / 100)
                
                bookmark_data = {
                    "bookmark_id": bookmark.id,
                    "program": {
                        "id": program.id,
                        "type": "program",
                        "title": program.title,
                        "subtitle": program.subtitle,
                        "description": program.description,
                        "category": {
                            "id": program.category.id,
                            "name": program.category.name,
                        } if program.category else None,
                        "image": program.image.url if program.image else None,
                        "duration": program.duration,
                        "program_rating": float(program.program_rating),
                        "is_best_seller": program.is_best_seller,
                        "enrolled_students": UserPurchase.objects.filter(
                            program=program,
                            status='completed'
                        ).count(),
                        "pricing": {
                            "original_price": float(program.price),
                            "discount_percentage": float(program.discount_percentage),
                            "discounted_price": float(discounted_price),
                            "savings": float(program.price - discounted_price)
                        },
                    },
                    "bookmarked_date": bookmark.bookmarked_date.isoformat()
                }
            elif bookmark.program_type == 'advanced_program' and bookmark.advanced_program:
                program = bookmark.advanced_program
                # Calculate discounted price
                discounted_price = program.price
                if program.discount_percentage > 0:
                    discounted_price = program.price * (1 - program.discount_percentage / 100)
                
                bookmark_data = {
                    "bookmark_id": bookmark.id,
                    "program": {
                        "id": program.id,
                        "type": "advanced_program",
                        "title": program.title,
                        "subtitle": program.subtitle,
                        "description": program.description,
                        "category": None,  # Advanced programs don't have categories
                        "image": program.image.url if program.image else None,
                        "duration": program.duration,
                        "program_rating": float(program.program_rating),
                        "is_best_seller": program.is_best_seller,
                        "enrolled_students": UserPurchase.objects.filter(
                            advanced_program=program,
                            status='completed'
                        ).count(),
                        "pricing": {
                            "original_price": float(program.price),
                            "discount_percentage": float(program.discount_percentage),
                            "discounted_price": float(discounted_price),
                            "savings": float(program.price - discounted_price)
                        },
                    },
                    "bookmarked_date": bookmark.bookmarked_date.isoformat()
                }
            else:
                continue  # Skip invalid bookmarks
            
            bookmarks_data.append(bookmark_data)
        
        return {
            "success": True,
            "count": len(bookmarks_data),
            "bookmarks": bookmarks_data
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching bookmarks: {str(e)}"}, status=500)

@api.post("/purchase", auth=AuthBearer())
def purchase_course(request, data: PurchaseSchema):
    """
    Purchase a course (program or advanced program) with dummy payment gateway
    """
    try:
        user = request.auth
        
        # Get request data from schema
        program_type = data.program_type  # 'program' or 'advanced_program'
        program_id = data.program_id
        payment_method = data.payment_method  # card, upi, wallet, etc.
        
        # Validate input
        if not program_type or not program_id:
            return JsonResponse({"success": False, "message": "program_type and program_id are required"}, status=400)
        
        if program_type not in ['program', 'advanced_program']:
            return JsonResponse({"success": False, "message": "Invalid program_type. Must be 'program' or 'advanced_program'"}, status=400)
        
        # Get the program
        try:
            if program_type == 'program':
                program = Program.objects.get(id=program_id)
                program_obj = program
                advanced_program_obj = None
            else:
                program = AdvanceProgram.objects.get(id=program_id)
                program_obj = None
                advanced_program_obj = program
        except (Program.DoesNotExist, AdvanceProgram.DoesNotExist):
            return JsonResponse({"success": False, "message": "Program not found"}, status=404)
        
        # Check if user already purchased this course
        existing_purchase = UserPurchase.objects.filter(
            user=user,
            program_type=program_type,
            program=program_obj,
            advanced_program=advanced_program_obj,
            status='completed'
        ).first()
        
        if existing_purchase:
            return JsonResponse({
                "success": False, 
                "message": "You have already purchased this course"
            }, status=400)
        
        # Calculate final price with discount
        original_price = program.price
        discount_percentage = program.discount_percentage
        final_price = original_price
        
        if discount_percentage > 0:
            final_price = original_price * (1 - discount_percentage / 100)
        
        # Generate dummy transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
        # Dummy Payment Gateway Processing
        payment_success = dummy_payment_gateway(
            amount=final_price,
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        
        if not payment_success:
            return JsonResponse({
                "success": False,
                "message": "Payment failed. Please try again.",
                "transaction_id": transaction_id
            }, status=400)
        
        # Create purchase record
        purchase = UserPurchase.objects.create(
            user=user,
            program_type=program_type,
            program=program_obj,
            advanced_program=advanced_program_obj,
            purchase_date=timezone.now(),
            status='completed'  # Since payment was successful
        )
        
        return {
            "success": True,
            "message": "Course purchased successfully!",
            "pricing": {
                "original_price": float(original_price),
                "discount_percentage": float(discount_percentage),
                "discounted_price": float(final_price),
                "savings": float(original_price - final_price)
            },
            "purchase": {
                "id": purchase.id,
                "program_type": purchase.program_type,
                "program_title": program.title,
                "purchase_date": purchase.purchase_date.isoformat(),
                "status": purchase.status,
                "transaction_id": transaction_id
            }
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error processing purchase: {str(e)}"}, status=500)

def dummy_payment_gateway(amount, payment_method, transaction_id):
    """
    Dummy payment gateway implementation
    Returns True for successful payment, False for failed payment
    """
    # Simulate payment processing delay
    import time
    time.sleep(0.5)
    
    # Dummy logic: 90% success rate, 10% failure rate
    success_rate = 0.9
    random_value = random.random()
    
    if random_value <= success_rate:
        # Payment successful
        print(f"[DUMMY PAYMENT] SUCCESS - Transaction ID: {transaction_id}, Amount: ₹{amount}, Method: {payment_method}")
        return True
    else:
        # Payment failed
        print(f"[DUMMY PAYMENT] FAILED - Transaction ID: {transaction_id}, Amount: ₹{amount}, Method: {payment_method}")
        return False

@api.get("/my-learnings", auth=AuthBearer())
def get_my_learnings(
    request,
    status: str = None  # 'onprogress', 'completed', or None for all
):
    """
    Get user's purchased courses (my learnings) with optional status filter
    """
    try:
        user = request.auth
        
        # Get all completed purchases for the user
        purchases = UserPurchase.objects.filter(
            user=user,
            status='completed'
        ).order_by('-purchase_date')
        
        # Apply status filter if provided
        if status:
            if status not in ['onprogress', 'completed']:
                return JsonResponse({
                    "success": False, 
                    "message": "Invalid status. Must be 'onprogress' or 'completed'"
                }, status=400)
            
            # For now, we'll simulate progress based on purchase date
            # In a real implementation, you'd have actual progress tracking
            if status == 'completed':
                # Consider courses purchased more than 30 days ago as completed
                from datetime import timedelta
                thirty_days_ago = timezone.now() - timedelta(days=30)
                purchases = purchases.filter(purchase_date__lt=thirty_days_ago)
            elif status == 'onprogress':
                # Consider courses purchased within last 30 days as in progress
                from datetime import timedelta
                thirty_days_ago = timezone.now() - timedelta(days=30)
                purchases = purchases.filter(purchase_date__gte=thirty_days_ago)
        
        learnings_data = []
        for purchase in purchases:
            if purchase.program_type == 'program' and purchase.program:
                program = purchase.program
                # Calculate discounted price
                discounted_price = program.price
                if program.discount_percentage > 0:
                    discounted_price = program.price * (1 - program.discount_percentage / 100)
                
                # Simulate progress (in real app, this would come from actual progress tracking)
                from datetime import timedelta
                days_since_purchase = (timezone.now() - purchase.purchase_date).days
                progress_percentage = min(100, max(0, (days_since_purchase / 30) * 100))
                is_completed = progress_percentage >= 100
                
                learning_data = {
                    "purchase_id": purchase.id,
                    "program": {
                        "id": program.id,
                        "type": "program",
                        "title": program.title,
                        "subtitle": program.subtitle,
                        "description": program.description,
                        "category": {
                            "id": program.category.id,
                            "name": program.category.name,
                        } if program.category else None,
                        "image": program.image.url if program.image else None,
                        "duration": program.duration,
                        "program_rating": float(program.program_rating),
                        "is_best_seller": program.is_best_seller,
                        "enrolled_students": UserPurchase.objects.filter(
                            program=program,
                            status='completed'
                        ).count(),
                        "pricing": {
                            "original_price": float(program.price),
                            "discount_percentage": float(program.discount_percentage),
                            "discounted_price": float(discounted_price),
                            "savings": float(program.price - discounted_price)
                        },
                    },
                    "purchase_date": purchase.purchase_date.isoformat(),
                    "progress": {
                        "percentage": round(progress_percentage, 2),
                        "status": "completed" if is_completed else "onprogress",
                        "completed_modules": int((progress_percentage / 100) * 10),  # Simulate modules
                        "total_modules": 10,  # Simulate total modules
                        "estimated_completion": "2-3 weeks" if not is_completed else "Completed"
                    }
                }
            elif purchase.program_type == 'advanced_program' and purchase.advanced_program:
                program = purchase.advanced_program
                # Calculate discounted price
                discounted_price = program.price
                if program.discount_percentage > 0:
                    discounted_price = program.price * (1 - program.discount_percentage / 100)
                
                # Simulate progress
                from datetime import timedelta
                days_since_purchase = (timezone.now() - purchase.purchase_date).days
                progress_percentage = min(100, max(0, (days_since_purchase / 45) * 100))  # Advanced courses take longer
                is_completed = progress_percentage >= 100
                
                learning_data = {
                    "purchase_id": purchase.id,
                    "program": {
                        "id": program.id,
                        "type": "advanced_program",
                        "title": program.title,
                        "subtitle": program.subtitle,
                        "description": program.description,
                        "category": None,  # Advanced programs don't have categories
                        "image": program.image.url if program.image else None,
                        "duration": program.duration,
                        "program_rating": float(program.program_rating),
                        "is_best_seller": program.is_best_seller,
                        "enrolled_students": UserPurchase.objects.filter(
                            advanced_program=program,
                            status='completed'
                        ).count(),
                        "pricing": {
                            "original_price": float(program.price),
                            "discount_percentage": float(program.discount_percentage),
                            "discounted_price": float(discounted_price),
                            "savings": float(program.price - discounted_price)
                        },
                    },
                    "purchase_date": purchase.purchase_date.isoformat(),
                    "progress": {
                        "percentage": round(progress_percentage, 2),
                        "status": "completed" if is_completed else "onprogress",
                        "completed_modules": int((progress_percentage / 100) * 15),  # Advanced programs have more modules
                        "total_modules": 15,
                        "estimated_completion": "4-6 weeks" if not is_completed else "Completed"
                    }
                }
            else:
                continue  # Skip invalid purchases
            
            learnings_data.append(learning_data)
        
        # Get statistics
        total_courses = len(learnings_data)
        completed_courses = len([l for l in learnings_data if l['progress']['status'] == 'completed'])
        in_progress_courses = total_courses - completed_courses
        
        return {
            "success": True,
            "statistics": {
                "total_courses": total_courses,
                "completed_courses": completed_courses,
                "in_progress_courses": in_progress_courses,
                "completion_rate": round((completed_courses / total_courses * 100), 2) if total_courses > 0 else 0
            },
            "filter_applied": status or "all",
            "learnings": learnings_data
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching learnings: {str(e)}"}, status=500)

@api.post("/learning/update-progress", auth=AuthBearer())
def update_learning_progress(request, data: UpdateProgressSchema):
    """
    Update user's progress for a specific topic/video
    """
    try:
        user = request.auth
        
        # Validate topic type
        if data.topic_type not in ['topic', 'advance_topic']:
            return JsonResponse({
                "success": False,
                "message": "Invalid topic_type. Must be 'topic' or 'advance_topic'"
            }, status=400)
        
        # Get the topic and associated purchase
        from .models import Topic, AdvanceTopic, Syllabus, AdvanceSyllabus
        
        if data.topic_type == 'topic':
            try:
                topic = Topic.objects.get(id=data.topic_id)
                # Find the purchase for this topic's program
                program = topic.syllabus.program
                purchase = UserPurchase.objects.get(
                    user=user,
                    program=program,
                    status='completed'
                )
                topic_obj = topic
                advance_topic_obj = None
            except (Topic.DoesNotExist, UserPurchase.DoesNotExist):
                return JsonResponse({
                    "success": False,
                    "message": "Topic not found or you don't have access to this course"
                }, status=404)
        else:
            try:
                advance_topic = AdvanceTopic.objects.get(id=data.topic_id)
                # Find the purchase for this topic's program
                program = advance_topic.advance_syllabus.advance_program
                purchase = UserPurchase.objects.get(
                    user=user,
                    advanced_program=program,
                    status='completed'
                )
                topic_obj = None
                advance_topic_obj = advance_topic
            except (AdvanceTopic.DoesNotExist, UserPurchase.DoesNotExist):
                return JsonResponse({
                    "success": False,
                    "message": "Advanced topic not found or you don't have access to this course"
                }, status=404)
        
        # Get or create topic progress
        topic_progress, created = UserTopicProgress.objects.get_or_create(
            user=user,
            purchase=purchase,
            topic=topic_obj,
            advance_topic=advance_topic_obj,
            defaults={
                'status': 'not_started',
                'total_duration_seconds': data.total_duration_seconds or 1800
            }
        )
        
        # Update progress
        topic_progress.update_progress(
            watch_time_seconds=data.watch_time_seconds,
            total_duration_seconds=data.total_duration_seconds
        )
        
        # Update course progress
        course_progress, _ = UserCourseProgress.objects.get_or_create(
            user=user,
            purchase=purchase
        )
        course_progress.update_progress()
        
        topic_title = topic_obj.topic_title if topic_obj else advance_topic_obj.topic_title
        
        return {
            "success": True,
            "message": "Progress updated successfully!",
            "topic_progress": {
                "topic_title": topic_title,
                "status": topic_progress.status,
                "completion_percentage": float(topic_progress.completion_percentage),
                "watch_time_seconds": topic_progress.watch_time_seconds,
                "total_duration_seconds": topic_progress.total_duration_seconds,
                "is_completed": topic_progress.is_completed
            },
            "course_progress": {
                "completion_percentage": float(course_progress.completion_percentage),
                "completed_topics": course_progress.completed_topics,
                "total_topics": course_progress.total_topics,
                "is_completed": course_progress.is_completed
            }
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error updating progress: {str(e)}"}, status=500)

@api.get("/learning/course/{purchase_id}", auth=AuthBearer())
def get_course_learning_details(request, purchase_id: int):
    """
    Get detailed learning information for a specific purchased course with all topics and progress
    """
    try:
        user = request.auth
        
        # Get the purchase
        try:
            purchase = UserPurchase.objects.get(
                id=purchase_id,
                user=user,
                status='completed'
            )
        except UserPurchase.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Course not found or you don't have access"
            }, status=404)
        
        # Get or create course progress
        course_progress, created = UserCourseProgress.objects.get_or_create(
            user=user,
            purchase=purchase
        )
        
        if created:
            # Initialize progress for new purchase
            from .models import Syllabus, AdvanceSyllabus
            
            if purchase.program_type == 'program' and purchase.program:
                syllabi = Syllabus.objects.filter(program=purchase.program).prefetch_related('topics')
                for syllabus in syllabi:
                    for topic in syllabus.topics.all():
                        UserTopicProgress.objects.get_or_create(
                            user=user,
                            purchase=purchase,
                            topic=topic,
                            defaults={
                                'status': 'not_started',
                                'total_duration_seconds': 1800,  # 30 minutes default
                            }
                        )
            elif purchase.program_type == 'advanced_program' and purchase.advanced_program:
                syllabi = AdvanceSyllabus.objects.filter(advance_program=purchase.advanced_program).prefetch_related('topics')
                for syllabus in syllabi:
                    for topic in syllabus.topics.all():
                        UserTopicProgress.objects.get_or_create(
                            user=user,
                            purchase=purchase,
                            advance_topic=topic,
                            defaults={
                                'status': 'not_started',
                                'total_duration_seconds': 2700,  # 45 minutes default
                            }
                        )
        course_progress.update_progress()
        
        # Get program details
        if purchase.program_type == 'program':
            program = purchase.program
            syllabi = program.syllabuses.all().prefetch_related('topics')
        else:
            program = purchase.advanced_program
            syllabi = program.syllabuses.all().prefetch_related('topics')
        
        # Build syllabus with progress
        syllabus_data = []
        for syllabus in syllabi:
            topics_data = []
            
            if purchase.program_type == 'program':
                topics = syllabus.topics.all()
                topic_type = 'topic'
            else:
                topics = syllabus.topics.all()
                topic_type = 'advance_topic'
            
            for topic in topics:
                # Get topic progress
                if purchase.program_type == 'program':
                    topic_progress = UserTopicProgress.objects.filter(
                        user=user,
                        purchase=purchase,
                        topic=topic
                    ).first()
                else:
                    topic_progress = UserTopicProgress.objects.filter(
                        user=user,
                        purchase=purchase,
                        advance_topic=topic
                    ).first()
                
                if topic_progress:
                    watch_hours = topic_progress.watch_time_seconds // 3600
                    watch_minutes = (topic_progress.watch_time_seconds % 3600) // 60
                    watch_seconds = topic_progress.watch_time_seconds % 60
                    
                    total_hours = topic_progress.total_duration_seconds // 3600
                    total_minutes = (topic_progress.total_duration_seconds % 3600) // 60
                    
                    is_intro = getattr(topic, 'is_intro', False)
                    topic_data = {
                        "id": topic.id,
                        "topic_title": topic.topic_title,
                        "topic_type": topic_type,
                        "is_free_trail": getattr(topic, 'is_free_trail', False),
                        "is_intro": is_intro,
                        "is_locked": False,  # User has purchased, so not locked
                        "video_url": topic.video_url,  # Show video URL since user purchased
                        "progress": {
                            "status": topic_progress.status,
                            "completion_percentage": float(topic_progress.completion_percentage),
                            "watch_time": f"{watch_hours:02d}:{watch_minutes:02d}:{watch_seconds:02d}",
                            "watch_time_seconds": topic_progress.watch_time_seconds,
                            "total_duration": f"{total_hours:02d}:{total_minutes:02d}",
                            "total_duration_seconds": topic_progress.total_duration_seconds,
                            "started_at": topic_progress.started_at.isoformat() if topic_progress.started_at else None,
                            "completed_at": topic_progress.completed_at.isoformat() if topic_progress.completed_at else None,
                            "last_watched_at": topic_progress.last_watched_at.isoformat()
                        }
                    }
                else:
                    # Topic not started
                    is_intro = getattr(topic, 'is_intro', False)
                    topic_data = {
                        "id": topic.id,
                        "topic_title": topic.topic_title,
                        "topic_type": topic_type,
                        "is_free_trail": getattr(topic, 'is_free_trail', False),
                        "is_intro": is_intro,
                        "is_locked": False,  # User has purchased, so not locked
                        "video_url": topic.video_url,  # Show video URL since user purchased
                        "progress": {
                            "status": "not_started",
                            "completion_percentage": 0,
                            "watch_time": "00:00:00",
                            "watch_time_seconds": 0,
                            "total_duration": "30:00" if purchase.program_type == 'program' else "45:00",
                            "total_duration_seconds": 1800 if purchase.program_type == 'program' else 2700,
                            "started_at": None,
                            "completed_at": None,
                            "last_watched_at": None
                        }
                    }
                
                topics_data.append(topic_data)
            
            syllabus_data.append({
                "id": syllabus.id,
                "module_title": syllabus.module_title,
                "topics_count": len(topics_data),
                "completed_topics": len([t for t in topics_data if t['progress']['status'] == 'completed']),
                "topics": topics_data
            })
        
        # Format course progress times
        total_watch_hours = course_progress.total_watch_time_seconds // 3600
        total_watch_minutes = (course_progress.total_watch_time_seconds % 3600) // 60
        
        return {
            "success": True,
            "course": {
                "purchase_id": purchase.id,
                "program_type": purchase.program_type,
                "program_title": program.title,
                "program_subtitle": program.subtitle,
                "program_description": program.description,
                "program_image": program.image.url if program.image else None,
                "purchase_date": purchase.purchase_date.isoformat(),
                "progress": {
                    "completion_percentage": float(course_progress.completion_percentage),
                    "completed_topics": course_progress.completed_topics,
                    "total_topics": course_progress.total_topics,
                    "in_progress_topics": course_progress.in_progress_topics,
                    "total_watch_time": f"{total_watch_hours}h {total_watch_minutes}m",
                    "total_watch_time_seconds": course_progress.total_watch_time_seconds,
                    "is_completed": course_progress.is_completed,
                    "started_at": course_progress.started_at.isoformat() if course_progress.started_at else None,
                    "completed_at": course_progress.completed_at.isoformat() if course_progress.completed_at else None,
                    "last_activity_at": course_progress.last_activity_at.isoformat()
                },
                "syllabus": syllabus_data
            }
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching course details: {str(e)}"}, status=500)
