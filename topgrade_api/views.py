from ninja import NinjaAPI
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .schemas import AreaOfInterestSchema, PurchaseSchema, BookmarkSchema, UpdateProgressSchema
from .models import Program, Category, UserPurchase, UserBookmark, UserCourseProgress, UserTopicProgress, Topic
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
        def format_program_data(program, user):
            """Helper function to format program data consistently"""
            discounted_price = program.discounted_price  # Use the property from unified model
            
            # Count enrolled students for this program
            enrolled_students = UserPurchase.objects.filter(
                program=program,
                status='completed'
            ).count()
            
            # Check if user has bookmarked this program
            is_bookmarked = UserBookmark.objects.filter(
                user=user,
                program=program
            ).exists() if user else False
            
            return {
                "id": program.id,
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
        top_course_programs = Program.objects.filter(
            program_rating__gte=4.0
        ).order_by('-program_rating', '-id')[:5]
        
        top_course = []
        for program in top_course_programs:
            top_course.append(format_program_data(program, user))
        
        # Recently Added - Latest programs by created_at/ID
        recently_added_programs = Program.objects.all().order_by('-created_at', '-id')[:5]
        
        recently_added = []
        for program in recently_added_programs:
            recently_added.append(format_program_data(program, user))
        
        # Featured - Best seller programs
        featured_programs = Program.objects.filter(
            is_best_seller=True
        ).order_by('-program_rating', '-id')[:5]
        
        featured = []
        for program in featured_programs:
            featured.append(format_program_data(program, user))
        
        # Programs - Regular programs only (not Advanced Program category)
        regular_programs = Program.get_regular_programs().order_by('-program_rating', '-id')[:5]
        programs = []
        for program in regular_programs:
            programs.append(format_program_data(program, user))
        
        # Advanced Programs - Advanced programs only (Advanced Program category)
        advance_programs = Program.get_advanced_programs().order_by('-program_rating', '-id')[:5]
        advanced_programs = []
        for program in advance_programs:
            advanced_programs.append(format_program_data(program, user))
        
        # Continue Watching - Recently watched programs for authenticated users only
        continue_watching = []
        
        if user:
            # Get user's recent topic progress (videos they've started but not completed)
            recent_progress = UserTopicProgress.objects.filter(
                user=user,
                status__in=['in_progress', 'completed']
            ).select_related(
                'purchase__program',
                'topic__syllabus__program'
            ).order_by('-last_watched_at')[:10]  # Get more to filter unique programs
            
            seen_programs = set()
            for progress in recent_progress:
                if len(continue_watching) >= 5:
                    break
                    
                # Get the program from the progress
                program = progress.purchase.program
                
                if program and program.id not in seen_programs:
                    seen_programs.add(program.id)
                    
                    # Get course progress for this program
                    course_progress = UserCourseProgress.objects.filter(
                        user=user,
                        purchase=progress.purchase
                    ).first()
                    
                    program_data = format_program_data(program, user)
                    
                    # Add progress information
                    program_data['progress'] = {
                        "percentage": float(course_progress.completion_percentage) if course_progress else 0.0,
                        "status": "completed" if course_progress and course_progress.is_completed else "in_progress",
                        "last_watched_at": progress.last_watched_at.isoformat(),
                        "last_watched_topic": progress.topic.topic_title if progress.topic else "Unknown Topic",
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
    Get all programs with comprehensive filtering options
    Uses unified Program model with category-based filtering
    """
    try:
        # Get authenticated user
        user = request.auth
        
        # Start with all programs
        programs_query = Program.objects.all().select_related('category')
        
        # Apply category filter
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
        
        # Apply sorting
        if sort_by == 'most_relevant':
            # Sort by relevance: best sellers first, then by rating
            programs_query = programs_query.order_by('-is_best_seller', '-program_rating', '-id')
        elif sort_by == 'recently_added':
            # Sort by creation date (newest first)
            programs_query = programs_query.order_by('-created_at', '-id')
        elif sort_by == 'top_rated':
            # Sort by rating (highest first)
            programs_query = programs_query.order_by('-program_rating', '-id')
        elif sort_by == 'title':
            order_field = 'title' if sort_order == 'asc' else '-title'
            programs_query = programs_query.order_by(order_field)
        elif sort_by == 'price':
            order_field = 'price' if sort_order == 'asc' else '-price'
            programs_query = programs_query.order_by(order_field)
        elif sort_by == 'program_rating':
            order_field = 'program_rating' if sort_order == 'asc' else '-program_rating'
            programs_query = programs_query.order_by(order_field)
        else:
            # Default sorting
            programs_query = programs_query.order_by('-program_rating', '-id')
        
        # Convert to list and format response
        all_programs = []
        for program in programs_query:
            # Check if user has bookmarked this program
            is_bookmarked = UserBookmark.objects.filter(
                user=user,
                program=program
            ).exists() if user else False
            
            # Count enrolled students
            enrolled_students = UserPurchase.objects.filter(
                program=program,
                status='completed'
            ).count()
            
            program_data = {
                "id": program.id,
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
                "enrolled_students": enrolled_students,
                "pricing": {
                    "original_price": float(program.price),
                    "discount_percentage": float(program.discount_percentage),
                    "discounted_price": float(program.discounted_price),
                    "savings": float(program.price - program.discounted_price)
                },
            }
            all_programs.append(program_data)
        
        # Get filter statistics
        total_count = len(all_programs)
        regular_count = sum(1 for p in all_programs if p['category'] and p['category']['name'] != 'Advanced Program')
        advanced_count = sum(1 for p in all_programs if p['category'] and p['category']['name'] == 'Advanced Program')
        
        return {
            "success": True,
            "filters_applied": {
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
                "total_count": total_count,
                "regular_programs_count": regular_count,
                "advanced_programs_count": advanced_count
            },
            "programs": all_programs
        }
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching filtered programs: {str(e)}"}, status=500)

@api.get("/program/{program_id}/details", auth=AuthBearer())
def get_program_details(request, program_id: int):
    """
    Get detailed information about a specific program including syllabus and topics
    Uses unified Program model - automatically handles both regular and advanced programs
    """
    try:
        # Get program from unified model
        try:
            program = Program.objects.select_related('category').prefetch_related(
                'syllabuses__topics'
            ).get(id=program_id)
        except Program.DoesNotExist:
            return JsonResponse({
                "success": False, 
                "message": "Program not found"
            }, status=404)
        
        # Check if user has purchased this program (for video access)
        user = request.auth
        has_purchased = False
        is_bookmarked = False
        
        if user:
            has_purchased = UserPurchase.objects.filter(
                user=user,
                program=program,
                status='completed'
            ).exists()
            
            # Check if user has bookmarked this program
            is_bookmarked = UserBookmark.objects.filter(
                user=user,
                program=program
            ).exists()
        
        # Get syllabus with topics
        syllabus_list = []
        syllabi = program.syllabuses.all().order_by('order', 'id')
        
        for syllabus in syllabi:
            topics_list = []
            topics = syllabus.topics.all().order_by('order', 'id')
            
            for topic in topics:
                # Determine video access: intro videos or free trial always accessible, others only if purchased
                video_url = ""
                is_accessible = False
                
                if (topic.is_intro or topic.is_free_trial) and topic.video_file:
                    # Intro videos and free trial videos are always accessible
                    video_url = topic.video_file.url
                    is_accessible = True
                elif has_purchased and topic.video_file:
                    # All videos accessible if user purchased
                    video_url = topic.video_file.url
                    is_accessible = True
                # Otherwise, video_url remains empty string
                
                topic_data = {
                    "id": topic.id,
                    "topic_title": topic.topic_title,
                    "description": topic.description,
                    "video_url": video_url,
                    "video_duration": topic.video_duration,
                    "is_intro": topic.is_intro,
                    "is_free_trial": topic.is_free_trial,
                    "is_accessible": is_accessible
                }
                
                topics_list.append(topic_data)
            
            syllabus_data = {
                "id": syllabus.id,
                "module_title": syllabus.module_title,
                "topics_count": len(topics_list),
                "topics": topics_list
            }
            syllabus_list.append(syllabus_data)
        
        # Count enrolled students
        enrolled_students = UserPurchase.objects.filter(
            program=program,
            status='completed'
        ).count()
        
        # Build program data
        program_data = {
            "id": program.id,
            "title": program.title,
            "subtitle": program.subtitle,
            "category": {
                "id": program.category.id,
                "name": program.category.name,
            } if program.category else None,
            "description": program.description,
            "image": program.image.url if program.image else None,
            "icon": program.icon,
            "duration": program.duration,
            "batch_starts": program.batch_starts,
            "available_slots": program.available_slots,
            "job_openings": program.job_openings,
            "global_market_size": program.global_market_size,
            "avg_annual_salary": program.avg_annual_salary,
            "program_rating": float(program.program_rating),
            "is_best_seller": program.is_best_seller,
            "is_bookmarked": is_bookmarked,
            "has_purchased": has_purchased,
            "enrolled_students": enrolled_students,
            "pricing": {
                "original_price": float(program.price),
                "discount_percentage": float(program.discount_percentage),
                "discounted_price": float(program.discounted_price),
                "savings": float(program.price - program.discounted_price)
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
    Add a program to user's bookmarks
    Uses unified Program model - works for both regular and advanced programs
    """
    try:
        user = request.auth
        
        # Get request data from schema
        program_id = data.program_id
        
        # Get the program from unified model
        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return JsonResponse({"success": False, "message": "Program not found"}, status=404)
        
        # Check if already bookmarked
        existing_bookmark = UserBookmark.objects.filter(
            user=user,
            program=program
        ).first()
        
        if existing_bookmark:
            return JsonResponse({
                "success": False,
                "message": "Course is already in your bookmarks"
            }, status=400)
        
        # Create bookmark
        bookmark = UserBookmark.objects.create(
            user=user,
            program=program,
            bookmarked_date=timezone.now()
        )
        
        return {
            "success": True,
            "message": "Course added to bookmarks successfully!",
            "bookmark": {
                "id": bookmark.id,
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
    Remove a program from user's bookmarks
    Uses unified Program model
    """
    try:
        user = request.auth
        
        # Get request data from schema
        program_id = data.program_id
        
        # Get the program from unified model
        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return JsonResponse({"success": False, "message": "Program not found"}, status=404)
        
        # Find and delete bookmark
        bookmark = UserBookmark.objects.filter(
            user=user,
            program=program
        ).first()
        
        if not bookmark:
            return JsonResponse({
                "success": False,
                "message": "Course is not in your bookmarks"
            }, status=404)
        
        program_title = program.title
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
    Uses unified Program model
    """
    try:
        user = request.auth
        
        # Get all user bookmarks with related program data
        bookmarks = UserBookmark.objects.filter(user=user).select_related(
            'program__category'
        ).order_by('-bookmarked_date')
        
        bookmarks_data = []
        for bookmark in bookmarks:
            if bookmark.program:
                program = bookmark.program
                
                # Count enrolled students
                enrolled_students = UserPurchase.objects.filter(
                    program=program,
                    status='completed'
                ).count()
                
                bookmark_data = {
                    "bookmark_id": bookmark.id,
                    "program": {
                        "id": program.id,
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
                        "enrolled_students": enrolled_students,
                        "pricing": {
                            "original_price": float(program.price),
                            "discount_percentage": float(program.discount_percentage),
                            "discounted_price": float(program.discounted_price),
                            "savings": float(program.price - program.discounted_price)
                        },
                    },
                    "bookmarked_date": bookmark.bookmarked_date.isoformat()
                }
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
    Purchase a program with dummy payment gateway
    Uses unified Program model - works for both regular and advanced programs
    """
    try:
        user = request.auth
        
        # Get request data from schema
        program_id = data.program_id
        payment_method = data.payment_method  # card, upi, wallet, etc.
        
        # Validate input
        if not program_id:
            return JsonResponse({"success": False, "message": "program_id is required"}, status=400)
        
        # Get the program from unified model
        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return JsonResponse({"success": False, "message": "Program not found"}, status=404)
        
        # Check if user already purchased this program
        existing_purchase = UserPurchase.objects.filter(
            user=user,
            program=program,
            status='completed'
        ).first()
        
        if existing_purchase:
            return JsonResponse({
                "success": False, 
                "message": "You have already purchased this course"
            }, status=400)
        
        # Calculate final price using the model property
        original_price = program.price
        discount_percentage = program.discount_percentage
        final_price = program.discounted_price
        
        # Generate dummy transaction ID
        import random
        import string
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
            program=program,
            amount_paid=final_price,
            purchase_date=timezone.now(),
            status='completed'  # Since payment was successful
        )
        
        # Create initial course progress tracking
        UserCourseProgress.objects.get_or_create(
            user=user,
            purchase=purchase,
            defaults={
                'total_topics': sum(s.topics.count() for s in program.syllabuses.all()),
                'completed_topics': 0,
                'in_progress_topics': 0,
                'completion_percentage': 0.0,
                'is_completed': False,
                'total_watch_time_seconds': 0,
                'last_activity_at': timezone.now()
            }
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
                "program_title": program.title,
                "program_category": program.category.name if program.category else None,
                "purchase_date": purchase.purchase_date.isoformat(),
                "status": purchase.status,
                "amount_paid": float(purchase.amount_paid),
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
    Uses unified Program model with real progress tracking
    """
    try:
        user = request.auth
        
        # Get all completed purchases for the user with related data
        purchases = UserPurchase.objects.filter(
            user=user,
            status='completed'
        ).select_related('program__category').prefetch_related(
            'program__syllabuses'
        ).order_by('-purchase_date')
        
        learnings_data = []
        for purchase in purchases:
            if purchase.program:
                program = purchase.program
                
                # Get actual course progress
                course_progress = UserCourseProgress.objects.filter(
                    user=user,
                    purchase=purchase
                ).first()
                
                # Calculate progress metrics
                if course_progress:
                    progress_percentage = course_progress.completion_percentage
                    completed_modules = course_progress.completed_topics
                    total_modules = course_progress.total_topics
                    is_completed = course_progress.is_completed
                    last_activity = course_progress.last_activity_at
                else:
                    # Fallback for purchases without progress tracking
                    progress_percentage = 0.0
                    completed_modules = 0
                    total_modules = sum(s.topics.count() for s in program.syllabuses.all())
                    is_completed = False
                    last_activity = purchase.purchase_date
                
                # Apply status filter
                if status:
                    if status == 'completed' and not is_completed:
                        continue
                    elif status == 'onprogress' and is_completed:
                        continue
                
                # Check if user has bookmarked this program
                is_bookmarked = UserBookmark.objects.filter(
                    user=user,
                    program=program
                ).exists()
                
                # Count enrolled students
                enrolled_students = UserPurchase.objects.filter(
                    program=program,
                    status='completed'
                ).count()
                
                learning_data = {
                    "purchase_id": purchase.id,
                    "program": {
                        "id": program.id,
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
                        "enrolled_students": enrolled_students,
                        "pricing": {
                            "original_price": float(program.price),
                            "discount_percentage": float(program.discount_percentage),
                            "discounted_price": float(program.discounted_price),
                            "savings": float(program.price - program.discounted_price)
                        },
                    },
                    "purchase_date": purchase.purchase_date.isoformat(),
                    "amount_paid": float(purchase.amount_paid),
                    "progress": {
                        "percentage": round(float(progress_percentage), 2),
                        "status": "completed" if is_completed else "onprogress",
                        "completed_topics": completed_modules,
                        "total_topics": total_modules,
                        "completed_modules": program.syllabuses.count() if is_completed else int((progress_percentage / 100) * program.syllabuses.count()),
                        "total_modules": program.syllabuses.count(),
                        "last_activity_at": last_activity.isoformat() if last_activity else None
                    }
                }
                learnings_data.append(learning_data)
        
        # Get statistics
        total_courses = len(learnings_data)
        completed_courses = len([l for l in learnings_data if l['progress']['status'] == 'completed'])
        in_progress_courses = total_courses - completed_courses
        
        # Calculate overall progress statistics
        total_watch_time = 0
        total_possible_topics = 0
        total_completed_topics = 0
        
        for learning in learnings_data:
            total_possible_topics += learning['progress']['total_topics']
            total_completed_topics += learning['progress']['completed_topics']
        
        overall_completion_rate = round((total_completed_topics / total_possible_topics * 100), 2) if total_possible_topics > 0 else 0
        
        return {
            "success": True,
            "statistics": {
                "total_courses": total_courses,
                "completed_courses": completed_courses,
                "in_progress_courses": in_progress_courses,
                "completion_rate": round((completed_courses / total_courses * 100), 2) if total_courses > 0 else 0,
                "overall_topic_completion": overall_completion_rate,
                "total_topics_completed": total_completed_topics,
                "total_topics_available": total_possible_topics
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
    Uses unified Program model for optimized performance
    """
    try:
        user = request.auth
        
        # Validate input
        if data.watch_time_seconds < 0:
            return JsonResponse({
                "success": False,
                "message": "Invalid watch time value"
            }, status=400)
        
        # Get and validate purchase
        try:
            purchase = UserPurchase.objects.select_related('program').get(
                id=data.purchase_id,
                user=user,
                status='completed'
            )
        except UserPurchase.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Purchase not found or access denied"
            }, status=404)
        
        # Get and validate topic
        try:
            topic = Topic.objects.select_related('syllabus__program').get(id=data.topic_id)
            
            # Verify topic belongs to the purchased program
            if topic.syllabus.program != purchase.program:
                return JsonResponse({
                    "success": False,
                    "message": "Topic does not belong to the purchased program"
                }, status=400)
                
        except Topic.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Topic not found"
            }, status=404)
        
        # Parse video duration from database
        video_duration = None
        if topic.video_duration:
            try:
                duration_parts = topic.video_duration.split(':')
                if len(duration_parts) == 2:  # MM:SS
                    video_duration = int(duration_parts[0]) * 60 + int(duration_parts[1])
                elif len(duration_parts) == 3:  # HH:MM:SS
                    video_duration = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
            except (ValueError, IndexError):
                video_duration = None
        
        total_duration = video_duration or 1800  # Default to 30 minutes if no duration found
        
        # Get or create topic progress
        topic_progress, created = UserTopicProgress.objects.get_or_create(
            user=user,
            purchase=purchase,
            topic=topic,
            defaults={
                'status': 'not_started',
                'total_duration_seconds': total_duration,
                'watch_time_seconds': 0,
                'completion_percentage': 0.0,
                'watch_percentage': 0.0,
                'last_watched_at': timezone.now(),
                'created_at': timezone.now()
            }
        )
        
        # Update progress with validation
        topic_progress.watch_time_seconds = max(topic_progress.watch_time_seconds, data.watch_time_seconds)
        topic_progress.total_duration_seconds = total_duration
        topic_progress.last_watched_at = timezone.now()
        
        # Calculate completion percentage
        completion_percentage = min(100.0, (topic_progress.watch_time_seconds / total_duration) * 100)
        topic_progress.completion_percentage = completion_percentage
        topic_progress.watch_percentage = completion_percentage
        
        # Update status based on completion
        if completion_percentage >= 90:  # Consider 90% as completed
            topic_progress.status = 'completed'
            if not hasattr(topic_progress, 'completed_at') or not topic_progress.completed_at:
                topic_progress.completed_at = timezone.now()
        elif completion_percentage > 0:
            topic_progress.status = 'in_progress'
        
        topic_progress.save()
        
        # Update course progress efficiently
        course_progress, _ = UserCourseProgress.objects.get_or_create(
            user=user,
            purchase=purchase,
            defaults={
                'completion_percentage': 0.0,
                'completed_topics': 0,
                'in_progress_topics': 0,
                'total_topics': 0,
                'is_completed': False,
                'total_watch_time_seconds': 0,
                'last_activity_at': timezone.now()
            }
        )
        
        # Calculate course progress based on all topics in the program
        total_topics = Topic.objects.filter(syllabus__program=purchase.program).count()
        completed_topics = UserTopicProgress.objects.filter(
            user=user,
            purchase=purchase,
            topic__isnull=False,
            status='completed'
        ).count()
        in_progress_topics = UserTopicProgress.objects.filter(
            user=user,
            purchase=purchase,
            topic__isnull=False,
            status='in_progress'
        ).count()
        
        # Calculate total watch time for this course
        total_watch_time = UserTopicProgress.objects.filter(
            user=user,
            purchase=purchase,
            topic__isnull=False
        ).aggregate(
            total_time=models.Sum('watch_time_seconds')
        )['total_time'] or 0
        
        course_completion = (completed_topics / total_topics * 100) if total_topics > 0 else 0
        course_progress.completion_percentage = course_completion
        course_progress.completed_topics = completed_topics
        course_progress.in_progress_topics = in_progress_topics
        course_progress.total_topics = total_topics
        course_progress.is_completed = course_completion >= 100
        course_progress.total_watch_time_seconds = total_watch_time
        course_progress.last_activity_at = timezone.now()
        course_progress.save()
        
        return {
            "success": True,
            "message": "Progress updated successfully!",
            "topic_progress": {
                "topic_id": topic.id,
                "topic_title": topic.topic_title,
                "status": topic_progress.status,
                "completion_percentage": round(float(topic_progress.completion_percentage), 2),
                "watch_time_seconds": topic_progress.watch_time_seconds,
                "total_duration_seconds": topic_progress.total_duration_seconds,
                "is_completed": topic_progress.status == 'completed',
                "last_watched_at": topic_progress.last_watched_at.isoformat()
            },
            "course_progress": {
                "completion_percentage": round(float(course_progress.completion_percentage), 2),
                "completed_topics": course_progress.completed_topics,
                "in_progress_topics": course_progress.in_progress_topics,
                "total_topics": course_progress.total_topics,
                "is_completed": course_progress.is_completed,
                "total_watch_time_seconds": course_progress.total_watch_time_seconds
            }
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error updating progress: {str(e)}"}, status=500)
