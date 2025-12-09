from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from topgrade_api.models import Category, Program, Syllabus, Topic, UserBookmark, UserPurchase
from .auth_view import admin_required


def calculate_video_duration(video_file):
    """Calculate video duration and return formatted string with improved reliability"""
    import tempfile
    import os
    import logging
    
    logger = logging.getLogger(__name__)
    temp_path = None
    
    try:
        # Create temporary file with proper suffix based on file extension
        file_extension = os.path.splitext(video_file.name)[1] if video_file.name else '.mp4'
        if not file_extension:
            file_extension = '.mp4'
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Reset file pointer to beginning
            video_file.seek(0)
            
            # Write file in chunks
            for chunk in video_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        # Reset file pointer back to beginning for any subsequent use
        video_file.seek(0)
        
        video_duration = None
        last_error = None
        
        # Method 1: Try with moviepy first (more reliable for various formats)
        try:
            try:
                from moviepy import VideoFileClip
            except ImportError:
                # Try alternative import
                import moviepy as mp
                VideoFileClip = mp.VideoFileClip
            
            with VideoFileClip(temp_path) as clip:
                duration_seconds = clip.duration
                if duration_seconds and duration_seconds > 0:
                    video_duration = format_duration(duration_seconds)
                    logger.info(f"Successfully calculated duration using moviepy: {video_duration}")
                    
        except Exception as e:
            last_error = f"Moviepy error: {str(e)}"
            logger.warning(f"Moviepy failed: {e}")
            
            # Method 2: Fallback to OpenCV
            try:
                import cv2
                
                cap = cv2.VideoCapture(temp_path)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    
                    if fps > 0 and frame_count > 0:
                        duration_seconds = frame_count / fps
                        video_duration = format_duration(duration_seconds)
                        logger.info(f"Successfully calculated duration using OpenCV: {video_duration}")
                    else:
                        logger.warning("OpenCV: Invalid FPS or frame count")
                        
                cap.release()
                
            except Exception as cv_error:
                last_error = f"OpenCV error: {str(cv_error)}"
                logger.error(f"OpenCV also failed: {cv_error}")
        
        if video_duration is None:
            logger.error(f"Failed to calculate video duration. Last error: {last_error}")
            
        return video_duration
        
    except Exception as e:
        logger.error(f"Unexpected error in calculate_video_duration: {e}")
        return None
        
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_path}: {e}")

def format_duration(duration_seconds):
    """Format duration in seconds to HH:MM:SS or MM:SS string"""
    if not duration_seconds or duration_seconds <= 0:
        return None
        
    total_seconds = int(duration_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

@admin_required
def programs_view(request):
    """Programs view"""
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'program':
            # Handle Add Program form
            title = request.POST.get('program_title')
            subtitle = request.POST.get('program_subtitle')
            description = request.POST.get('program_description')
            category_id = request.POST.get('program_category')
            image = request.FILES.get('program_image')
            batch_starts = request.POST.get('batch_starts')
            available_slots = request.POST.get('available_slots')
            duration = request.POST.get('duration')
            job_openings = request.POST.get('job_openings')
            global_market_size = request.POST.get('global_market_size')
            avg_annual_salary = request.POST.get('avg_annual_salary')
            program_rating = request.POST.get('program_rating')
            is_best_seller = request.POST.get('is_best_seller') == 'on'
            icon = request.POST.get('program_icon')
            price = request.POST.get('price')
            discount_percentage = request.POST.get('discount_percentage')
            skills_input = request.POST.get('program_skills', '')
            
            # Process skills input
            skills = None
            if skills_input and skills_input.strip():
                # Split by comma and clean up
                skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
            
            if title and category_id and batch_starts and available_slots and duration:
                try:
                    category = Category.objects.get(id=category_id)
                    program = Program.objects.create(
                        title=title,
                        subtitle=subtitle,
                        description=description,
                        category=category,
                        image=image,
                        batch_starts=batch_starts,
                        available_slots=int(available_slots),
                        duration=duration,
                        job_openings=job_openings or '',
                        global_market_size=global_market_size or '',
                        avg_annual_salary=avg_annual_salary or '',
                        program_rating=float(program_rating) if program_rating else 0.0,
                        is_best_seller=is_best_seller,
                        icon=icon,
                        price=float(price) if price else 0.0,
                        discount_percentage=float(discount_percentage) if discount_percentage else 0.0,
                        skills=skills
                    )
                    
                    # Handle syllabus and topics creation
                    modules_data = {}
                    
                    # Parse modules and topics from POST data
                    for key, value in request.POST.items():
                        if key.startswith('modules[') and value.strip():
                            # Extract module index and field type
                            # Format: modules[0][title] or modules[0][topics][0][title]
                            parts = key.replace('modules[', '').replace(']', '').split('[')
                            
                            if len(parts) >= 2:
                                module_index = int(parts[0])
                                
                                if module_index not in modules_data:
                                    modules_data[module_index] = {'title': '', 'topics': {}}
                                
                                if parts[1] == 'title':
                                    # Module title
                                    modules_data[module_index]['title'] = value
                                elif parts[1] == 'topics' and len(parts) >= 4:
                                    # Topic data
                                    topic_index = int(parts[2])
                                    topic_field = parts[3]
                                    
                                    if topic_index not in modules_data[module_index]['topics']:
                                        modules_data[module_index]['topics'][topic_index] = {}
                                    
                                    modules_data[module_index]['topics'][topic_index][topic_field] = value
                    
                    # Create syllabus modules and topics
                    for module_index, module_data in modules_data.items():
                        if module_data['title']:
                            # Create syllabus module
                            syllabus = Syllabus.objects.create(
                                program=program,
                                module_title=module_data['title']
                            )
                            
                            # Create topics for this module
                            for topic_index, topic_data in module_data['topics'].items():
                                if topic_data.get('title'):
                                    # Handle video file upload and duration calculation
                                    video_file = None
                                    video_duration = None
                                    video_s3_url = topic_data.get('video_s3_url', '')
                                    
                                    # Check if S3 URL was provided (direct upload)
                                    if video_s3_url:
                                        # Video was uploaded directly to S3
                                        # Store the S3 URL in the video_file field
                                        video_file = video_s3_url
                                        # Note: Duration calculation for S3 videos would require downloading
                                        # which is not efficient. Consider calculating on client side or skipping.
                                    elif f'modules[{module_index}][topics][{topic_index}][video_file]' in request.FILES:
                                        # Traditional file upload (fallback)
                                        video_file = request.FILES[f'modules[{module_index}][topics][{topic_index}][video_file]']
                                        # Calculate video duration with error handling
                                        try:
                                            video_duration = calculate_video_duration(video_file)
                                            if video_duration is None:
                                                messages.warning(request, f'Could not calculate duration for video in module {module_index + 1}, topic {topic_index + 1}. Video saved without duration.')
                                        except Exception as e:
                                            messages.warning(request, f'Error calculating video duration: {str(e)}. Video saved without duration.')
                                            video_duration = None
                                    
                                    Topic.objects.create(
                                        syllabus=syllabus,
                                        topic_title=topic_data['title'],
                                        description=topic_data.get('description', ''),
                                        video_file=video_file,
                                        video_duration=video_duration,
                                        is_intro=topic_data.get('is_intro') == 'on'
                                    )
                    
                    messages.success(request, 'Program with syllabus added successfully')
                except Category.DoesNotExist:
                    messages.error(request, 'Selected category does not exist')
                except ValueError:
                    messages.error(request, 'Available slots must be a number')
                except Exception as e:
                    messages.error(request, f'Error creating program: {str(e)}')
            else:
                messages.error(request, 'Title, category, batch starts, available slots, and duration are required')
        
        elif form_type == 'delete_program':
            program_id = request.POST.get('program_id')
            if program_id:
                try:
                    program = Program.objects.get(id=program_id)
                    program_title = program.title
                    program.delete()
                    messages.success(request, f'Program "{program_title}" has been deleted successfully.')
                except Program.DoesNotExist:
                    messages.error(request, 'Program not found.')
                except Exception as e:
                    messages.error(request, f'Error deleting program: {str(e)}')
            else:
                messages.error(request, 'Program ID is required for deletion.')
        
        return redirect('dashboard:programs')

    user = request.user
    categories_list = Category.objects.all().order_by('-id')
    
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Filter programs based on search query
    if search_query:
        programs_list = Program.objects.filter(
            title__icontains=search_query
        ) | Program.objects.filter(
            subtitle__icontains=search_query
        ) | Program.objects.filter(
            category__name__icontains=search_query
        )
        programs_list = programs_list.distinct().order_by('-id')
    else:
        programs_list = Program.objects.all().order_by('-id')
    
    # Programs Pagination
    programs_paginator = Paginator(programs_list, 9)
    programs_page = request.GET.get('programs_page')
    
    try:
        programs = programs_paginator.page(programs_page)
    except PageNotAnInteger:
        programs = programs_paginator.page(1)
    except EmptyPage:
        programs = programs_paginator.page(programs_paginator.num_pages)
    
    # Programs pagination range logic
    programs_current_page = programs.number
    programs_total_pages = programs_paginator.num_pages
    
    programs_start_page = max(1, programs_current_page - 1)
    programs_end_page = min(programs_total_pages, programs_current_page + 1)
    
    if programs_end_page - programs_start_page < 2:
        if programs_start_page == 1:
            programs_end_page = min(programs_total_pages, programs_start_page + 2)
        elif programs_end_page == programs_total_pages:
            programs_start_page = max(1, programs_end_page - 2)
    
    programs_page_range = range(programs_start_page, programs_end_page + 1)
    
    # Categories Pagination
    categories_paginator = Paginator(categories_list, 9)
    categories_page = request.GET.get('categories_page')
    
    try:
        categories = categories_paginator.page(categories_page)
    except PageNotAnInteger:
        categories = categories_paginator.page(1)
    except EmptyPage:
        categories = categories_paginator.page(categories_paginator.num_pages)
    
    # Categories pagination range logic
    categories_current_page = categories.number
    categories_total_pages = categories_paginator.num_pages
    
    categories_start_page = max(1, categories_current_page - 1)
    categories_end_page = min(categories_total_pages, categories_current_page + 1)
    
    if categories_end_page - categories_start_page < 2:
        if categories_start_page == 1:
            categories_end_page = min(categories_total_pages, categories_start_page + 2)
        elif categories_end_page == categories_total_pages:
            categories_start_page = max(1, categories_end_page - 2)
    
    categories_page_range = range(categories_start_page, categories_end_page + 1)
    
    context = {
        'user': user, 
        'categories': categories, 
        'programs': programs,
        'programs_page_range': programs_page_range,
        'programs_total_pages': programs_total_pages,
        'programs_current_page': programs_current_page,
        'categories_page_range': categories_page_range,
        'categories_total_pages': categories_total_pages,
        'categories_current_page': categories_current_page,
        'search_query': search_query
    }
    return render(request, 'dashboard/programs.html', context)

@admin_required
def edit_program_view(request, id):
    """Edit program view"""
    try:
        program = Program.objects.get(id=id)
    except Program.DoesNotExist:
        messages.error(request, 'Program not found')
        return redirect('dashboard:programs')
    
    if request.method == 'POST':
        # Handle Edit Program form
        title = request.POST.get('program_title')
        subtitle = request.POST.get('program_subtitle')
        description = request.POST.get('program_description')
        category_id = request.POST.get('program_category')
        image = request.FILES.get('program_image')
        batch_starts = request.POST.get('batch_starts')
        available_slots = request.POST.get('available_slots')
        duration = request.POST.get('duration')
        job_openings = request.POST.get('job_openings')
        global_market_size = request.POST.get('global_market_size')
        avg_annual_salary = request.POST.get('avg_annual_salary')
        program_rating = request.POST.get('program_rating')
        is_best_seller = request.POST.get('is_best_seller') == 'on'
        icon = request.POST.get('program_icon')
        price = request.POST.get('price')
        discount_percentage = request.POST.get('discount_percentage')
        skills_input = request.POST.get('program_skills', '')
        
        # Process skills input
        skills = None
        if skills_input and skills_input.strip():
            # Split by comma and clean up
            skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
        
        if title and category_id and batch_starts and available_slots and duration:
            try:
                category = Category.objects.get(id=category_id)
                program.title = title
                program.subtitle = subtitle
                program.description = description
                program.category = category
                if image:  # Only update image if new one is provided
                    program.image = image
                program.batch_starts = batch_starts
                program.available_slots = int(available_slots)
                program.duration = duration
                program.job_openings = job_openings or ''
                program.global_market_size = global_market_size or ''
                program.avg_annual_salary = avg_annual_salary or ''
                program.program_rating = float(program_rating) if program_rating else 0.0
                program.is_best_seller = is_best_seller
                program.icon = icon
                program.price = float(price) if price else 0.0
                program.discount_percentage = float(discount_percentage) if discount_percentage else 0.0
                program.skills = skills
                program.save()
                
                # Handle syllabus and topics update WITHOUT deleting existing data
                # Parse modules and topics from POST data
                modules_data = {}
                
                for key, value in request.POST.items():
                    if key.startswith('modules[') and value.strip():
                        # Extract module index and field type
                        # Format: modules[0][title] or modules[0][topics][0][title]
                        parts = key.replace('modules[', '').replace(']', '').split('[')
                        
                        if len(parts) >= 2:
                            module_index = int(parts[0])
                            
                            if module_index not in modules_data:
                                modules_data[module_index] = {'title': '', 'topics': {}}
                            
                            if parts[1] == 'title':
                                # Module title
                                modules_data[module_index]['title'] = value
                            elif parts[1] == 'topics' and len(parts) >= 4:
                                # Topic data
                                topic_index = int(parts[2])
                                topic_field = parts[3]
                                
                                if topic_index not in modules_data[module_index]['topics']:
                                    modules_data[module_index]['topics'][topic_index] = {}
                                
                                modules_data[module_index]['topics'][topic_index][topic_field] = value
                
                # Get existing syllabuses
                existing_syllabuses = list(program.syllabuses.all())
                
                # Update or create syllabus modules and topics
                for module_index, module_data in modules_data.items():
                    if module_data['title']:
                        # Update existing syllabus or create new one
                        if module_index < len(existing_syllabuses):
                            syllabus = existing_syllabuses[module_index]
                            syllabus.module_title = module_data['title']
                            syllabus.save()
                        else:
                            # Create new syllabus module
                            syllabus = Syllabus.objects.create(
                                program=program,
                                module_title=module_data['title']
                            )
                        
                        # Get existing topics for this syllabus
                        existing_topics = list(syllabus.topics.all())
                        
                        # Update or create topics for this module
                        topic_indices = list(module_data['topics'].keys())
                        for topic_index in topic_indices:
                            topic_data = module_data['topics'][topic_index]
                            if topic_data.get('title'):
                                # Update existing topic or create new one
                                if topic_index < len(existing_topics):
                                    topic = existing_topics[topic_index]
                                    topic.topic_title = topic_data['title']
                                    topic.description = topic_data.get('description', '')
                                    topic.is_intro = topic_data.get('is_intro') == 'on'
                                    
                                    # Only update video if new one is uploaded
                                    if f'modules[{module_index}][topics][{topic_index}][video_file]' in request.FILES:
                                        topic.video_file = request.FILES[f'modules[{module_index}][topics][{topic_index}][video_file]']
                                        try:
                                            topic.video_duration = calculate_video_duration(topic.video_file)
                                            if topic.video_duration is None:
                                                messages.warning(request, f'Could not calculate duration for updated video in module {module_index + 1}, topic {topic_index + 1}.')
                                        except Exception as e:
                                            messages.warning(request, f'Error calculating video duration: {str(e)}. Video updated without duration.')
                                            topic.video_duration = None
                                    
                                    topic.save()
                                else:
                                    # Create new topic
                                    video_file = None
                                    video_duration = None
                                    
                                    if f'modules[{module_index}][topics][{topic_index}][video_file]' in request.FILES:
                                        video_file = request.FILES[f'modules[{module_index}][topics][{topic_index}][video_file]']
                                        try:
                                            video_duration = calculate_video_duration(video_file)
                                            if video_duration is None:
                                                messages.warning(request, f'Could not calculate duration for new video in module {module_index + 1}, topic {topic_index + 1}. Video saved without duration.')
                                        except Exception as e:
                                            messages.warning(request, f'Error calculating video duration: {str(e)}. Video saved without duration.')
                                            video_duration = None
                                    
                                    Topic.objects.create(
                                        syllabus=syllabus,
                                        topic_title=topic_data['title'],
                                        description=topic_data.get('description', ''),
                                        video_file=video_file,
                                        video_duration=video_duration,
                                        is_intro=topic_data.get('is_intro') == 'on'
                                    )
                        
                        # Remove extra topics if there are fewer topics now
                        if len(topic_indices) < len(existing_topics):
                            for i in range(len(topic_indices), len(existing_topics)):
                                existing_topics[i].delete()
                
                # Remove extra syllabuses if there are fewer modules now
                if len(modules_data) < len(existing_syllabuses):
                    for i in range(len(modules_data), len(existing_syllabuses)):
                        existing_syllabuses[i].delete()
                
                messages.success(request, 'Program updated successfully')
            except Category.DoesNotExist:
                messages.error(request, 'Selected category does not exist')
            except ValueError:
                messages.error(request, 'Available slots must be a number')
        else:
            messages.error(request, 'Title, category, batch starts, available slots, and duration are required')
        
        # Preserve pagination parameters when redirecting
        programs_page = request.GET.get('programs_page', 1)
        categories_page = request.GET.get('categories_page', 1)
        return redirect(f'/dashboard/programs/?programs_page={programs_page}&categories_page={categories_page}')
    
    # GET request - show edit form
    user = request.user
    categories = Category.objects.all()
    programs_list = Program.objects.all().order_by('-id')
    
    # Pagination for edit view
    paginator = Paginator(programs_list, 6)
    page = request.GET.get('page', 1)
    
    try:
        programs = paginator.page(page)
    except PageNotAnInteger:
        programs = paginator.page(1)
    except EmptyPage:
        programs = paginator.page(paginator.num_pages)
    
    # Custom pagination range logic
    current_page = programs.number
    total_pages = paginator.num_pages
    
    start_page = max(1, current_page - 1)
    end_page = min(total_pages, current_page + 1)
    
    if end_page - start_page < 2:
        if start_page == 1:
            end_page = min(total_pages, start_page + 2)
        elif end_page == total_pages:
            start_page = max(1, end_page - 2)
    
    page_range = range(start_page, end_page + 1)
    
    context = {
        'user': user, 
        'categories': categories, 
        'programs': programs,
        'page_range': page_range,
        'total_pages': total_pages,
        'current_page': current_page,
        'edit_program': program  # Pass the program to edit
    }
    return render(request, 'dashboard/programs.html', context)

@admin_required
def delete_program_view(request, id):
    """Delete program view"""
    try:
        program = Program.objects.get(id=id)
        program.delete()
        messages.success(request, 'Program deleted successfully')
    except Program.DoesNotExist:
        messages.error(request, 'Program not found')
    
    # Preserve pagination and search parameters when redirecting
    programs_page = request.GET.get('programs_page', 1)
    categories_page = request.GET.get('categories_page', 1)
    search_query = request.GET.get('search', '')
    
    redirect_url = f'/dashboard/programs/?programs_page={programs_page}&categories_page={categories_page}'
    if search_query:
        redirect_url += f'&search={search_query}'
    
    return redirect(redirect_url)

@admin_required
def program_details_view(request, program_id):
    """Program details view with comprehensive information"""
    from django.shortcuts import get_object_or_404
    from django.db.models import Count, Sum, Avg
    from django.utils import timezone
    
    try:
        program = get_object_or_404(Program, id=program_id)
    except Program.DoesNotExist:
        messages.error(request, 'Program not found')
        return redirect('dashboard:programs')
    
    # Get program syllabuses with topics
    syllabuses = program.syllabuses.prefetch_related('topics').all()
    
    # Calculate total topics
    total_topics = sum(syllabus.topics.count() for syllabus in syllabuses)
    
    # Get enrolled students (purchases)
    enrolled_students = UserPurchase.objects.filter(
        program=program
    ).select_related('user').order_by('-purchase_date')
    
    # Calculate enrollment statistics
    total_enrollments = enrolled_students.count()
    active_enrollments = enrolled_students.filter(status='completed').count()
    pending_enrollments = enrolled_students.filter(status='pending').count()
    available_slots = max(0, program.available_slots - active_enrollments)
    
    # Calculate analytics data
    # Program views (placeholder - you can implement tracking later)
    program_views = 0  # Implement view tracking if needed
    
    # Enrollment rate calculation
    if program_views > 0:
        enrollment_rate = round((total_enrollments / program_views) * 100, 1)
    else:
        enrollment_rate = 0
    
    # Bookmarks count
    bookmarks_count = UserBookmark.objects.filter(program=program).count()
    
    # Revenue calculation
    total_revenue = enrolled_students.filter(status='completed').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    # Sample reviews data (you can create a Review model later)
    reviews = []  # Placeholder for reviews
    reviews_count = 0
    
    # Sample enrollment trends data (you can implement actual tracking)
    enrollment_trends = {
        'Jan': enrolled_students.filter(purchase_date__month=1).count(),
        'Feb': enrolled_students.filter(purchase_date__month=2).count(),
        'Mar': enrolled_students.filter(purchase_date__month=3).count(),
        'Apr': enrolled_students.filter(purchase_date__month=4).count(),
        'May': enrolled_students.filter(purchase_date__month=5).count(),
        'Jun': enrolled_students.filter(purchase_date__month=6).count(),
        'Jul': enrolled_students.filter(purchase_date__month=7).count(),
        'Aug': enrolled_students.filter(purchase_date__month=8).count(),
        'Sep': enrolled_students.filter(purchase_date__month=9).count(),
        'Oct': enrolled_students.filter(purchase_date__month=10).count(),
        'Nov': enrolled_students.filter(purchase_date__month=11).count(),
        'Dec': enrolled_students.filter(purchase_date__month=12).count(),
    }
    
    context = {
        'user': request.user,
        'program': program,
        'syllabuses': syllabuses,
        'total_topics': total_topics,
        'enrolled_students': enrolled_students[:20],  # Limit to recent 20 for performance
        'total_enrollments': total_enrollments,
        'active_enrollments': active_enrollments,
        'pending_enrollments': pending_enrollments,
        'available_slots': available_slots,
        'program_views': program_views,
        'enrollment_rate': enrollment_rate,
        'bookmarks_count': bookmarks_count,
        'total_revenue': total_revenue,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'enrollment_trends': enrollment_trends,
    }
    
    return render(request, 'dashboard/program_details.html', context)
