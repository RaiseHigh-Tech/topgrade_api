from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from topgrade_api.models import Category, Program, Syllabus, Topic, UserPurchase, UserBookmark

User = get_user_model()

def calculate_video_duration(video_file):
    """Calculate video duration and return formatted string"""
    try:
        import tempfile
        import os
        
        # Save video file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
            for chunk in video_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        video_duration = None
        try:
            # Try with OpenCV first
            import cv2
            cap = cv2.VideoCapture(temp_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if fps > 0:
                duration_seconds = frame_count / fps
                # Format duration as MM:SS or HH:MM:SS
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                if minutes >= 60:
                    hours = minutes // 60
                    minutes = minutes % 60
                    video_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    video_duration = f"{minutes:02d}:{seconds:02d}"
            cap.release()
        except Exception:
            # Fallback to moviepy
            try:
                from moviepy.editor import VideoFileClip
                clip = VideoFileClip(temp_path)
                duration_seconds = clip.duration
                clip.close()
                # Format duration
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                if minutes >= 60:
                    hours = minutes // 60
                    minutes = minutes % 60
                    video_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    video_duration = f"{minutes:02d}:{seconds:02d}"
            except Exception:
                video_duration = None
        
        # Clean up temp file
        os.unlink(temp_path)
        return video_duration
        
    except Exception:
        return None

def admin_required(view_func):
    """
    Decorator to ensure only admin users (superusers) can access dashboard views
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/dashboard/signin/')
        
        if not request.user.is_superuser:
            messages.error(request, 'You are not authorized to access the dashboard.')
            return redirect('/dashboard/signin/')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def signin_view(request):
    """
    Custom login view for dashboard - only allows admin users (superusers)
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Use AdminOnlyBackend for authentication
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('/dashboard/')
        else:
            messages.error(request, 'Invalid credentials or you are not authorized to access the dashboard.')
    
    return render(request, 'dashboard/signin.html')

def dashboard_logout(request):
    """
    Logout view for dashboard
    """
    logout(request)
    return redirect('/dashboard/signin/')

@admin_required
def dashboard_home(request):
    """
    Dashboard home view with comprehensive analytics - only accessible by admin users (superusers)
    """
    from django.utils import timezone
    from django.db.models import Count, Sum, Avg, Q
    from datetime import datetime, timedelta
    import calendar
    
    # Date calculations
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Students Analytics
    all_students = User.objects.filter(role='student')
    total_students = all_students.count()
    new_students_today = all_students.filter(date_joined__date=today).count()
    new_students_this_month = all_students.filter(date_joined__month=current_month, date_joined__year=current_year).count()
    active_students = User.objects.filter(role='student', purchases__status='completed').distinct().count()
    
    # Programs Analytics
    total_programs = Program.objects.count()
    total_categories = Category.objects.count()
    advanced_programs = Program.objects.filter(category__name='Advanced Program').count()
    best_seller_programs = Program.objects.filter(is_best_seller=True).count()
    
    # Enrollment Analytics
    all_purchases = UserPurchase.objects.all()
    total_enrollments = all_purchases.count()
    completed_enrollments = all_purchases.filter(status='completed').count()
    pending_enrollments = all_purchases.filter(status='pending').count()
    enrollments_today = all_purchases.filter(purchase_date__date=today).count()
    enrollments_this_month = all_purchases.filter(purchase_date__month=current_month, purchase_date__year=current_year).count()
    
    # Revenue Analytics
    total_revenue = all_purchases.filter(status='completed').aggregate(total=Sum('amount_paid'))['total'] or 0
    revenue_this_month = all_purchases.filter(
        status='completed', 
        purchase_date__month=current_month, 
        purchase_date__year=current_year
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Average revenue per enrollment
    avg_revenue_per_enrollment = total_revenue / completed_enrollments if completed_enrollments > 0 else 0
    
    # Monthly enrollment trends (last 12 months)
    enrollment_trends = []
    for i in range(11, -1, -1):
        date = today.replace(day=1) - timedelta(days=30*i)
        month_enrollments = all_purchases.filter(
            purchase_date__month=date.month, 
            purchase_date__year=date.year
        ).count()
        enrollment_trends.append({
            'month': calendar.month_abbr[date.month],
            'count': month_enrollments
        })
    
    # Weekly enrollment trends (last 4 weeks)
    weekly_trends = []
    for i in range(3, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7*i)
        week_end = week_start + timedelta(days=6)
        week_enrollments = all_purchases.filter(
            purchase_date__date__range=[week_start, week_end]
        ).count()
        weekly_trends.append({
            'week': f"Week {4-i}",
            'count': week_enrollments
        })
    
    # Top performing programs
    top_programs = Program.objects.annotate(
        enrollment_count=Count('purchases')
    ).order_by('-enrollment_count')[:5]
    
    # Recent enrollments
    recent_enrollments = UserPurchase.objects.select_related('user', 'program').order_by('-purchase_date')[:10]
    
    # Program category distribution
    category_distribution = Category.objects.annotate(
        program_count=Count('programs')
    ).values('name', 'program_count')
    
    # Student area of interest distribution
    interest_distribution = all_students.exclude(
        Q(area_of_intrest__isnull=True) | Q(area_of_intrest__exact='')
    ).values('area_of_intrest').annotate(count=Count('area_of_intrest')).order_by('-count')[:5]
    
    # Revenue by program
    revenue_by_program = Program.objects.annotate(
        revenue=Sum('purchases__amount_paid', filter=Q(purchases__status='completed'))
    ).order_by('-revenue')[:5]
    
    # Calculate growth rates
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month_enrollments = all_purchases.filter(
        purchase_date__month=last_month.month, 
        purchase_date__year=last_month.year
    ).count()
    
    if last_month_enrollments > 0:
        enrollment_growth = round(((enrollments_this_month - last_month_enrollments) / last_month_enrollments) * 100, 1)
    else:
        enrollment_growth = 100 if enrollments_this_month > 0 else 0
    
    # Students registered last month
    last_month_students = all_students.filter(
        date_joined__month=last_month.month, 
        date_joined__year=last_month.year
    ).count()
    
    if last_month_students > 0:
        student_growth = round(((new_students_this_month - last_month_students) / last_month_students) * 100, 1)
    else:
        student_growth = 100 if new_students_this_month > 0 else 0
    
    context = {
        'user': request.user,
        # Student metrics
        'total_students': total_students,
        'new_students_today': new_students_today,
        'new_students_this_month': new_students_this_month,
        'active_students': active_students,
        'student_growth': student_growth,
        
        # Program metrics
        'total_programs': total_programs,
        'total_categories': total_categories,
        'advanced_programs': advanced_programs,
        'best_seller_programs': best_seller_programs,
        
        # Enrollment metrics
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'pending_enrollments': pending_enrollments,
        'enrollments_today': enrollments_today,
        'enrollments_this_month': enrollments_this_month,
        'enrollment_growth': enrollment_growth,
        
        # Revenue metrics
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        'avg_revenue_per_enrollment': avg_revenue_per_enrollment,
        
        # Charts data
        'enrollment_trends': enrollment_trends,
        'weekly_trends': weekly_trends,
        'category_distribution': list(category_distribution),
        'interest_distribution': list(interest_distribution),
        'revenue_by_program': revenue_by_program,
        
        # Tables data
        'top_programs': top_programs,
        'recent_enrollments': recent_enrollments,
    }
    return render(request, 'dashboard/dashboard.html', context)

@admin_required
def programs_view(request):
    """Programs view""" 
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'category':
            # Handle Add Category form
            name = request.POST.get('category_name')
            description = request.POST.get('category_description')
            icon = request.POST.get('category_icon')
            if name:
                Category.objects.create(name=name, description=description, icon=icon)
                messages.success(request, 'Category added successfully')
            else:
                messages.error(request, 'Category name is required')
                
        elif form_type == 'program':
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
                        discount_percentage=float(discount_percentage) if discount_percentage else 0.0
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
                                    if f'modules[{module_index}][topics][{topic_index}][video_file]' in request.FILES:
                                        video_file = request.FILES[f'modules[{module_index}][topics][{topic_index}][video_file]']
                                        # Calculate video duration
                                        video_duration = calculate_video_duration(video_file)
                                    
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
    categories_list = Category.objects.all().order_by('-id')  # Order by newest first
    programs_list = Program.objects.all().order_by('-id')  # Order by newest first
    
    # Programs Pagination
    programs_paginator = Paginator(programs_list, 9)  # Show 6 programs per page
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
    categories_paginator = Paginator(categories_list, 5)  # Show 5 categories per page
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
        'categories_current_page': categories_current_page
    }
    return render(request, 'dashboard/programs.html', context)

@admin_required
def edit_category_view(request, id):
    """Edit category view"""
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        messages.error(request, 'Category not found')
        return redirect('dashboard:programs')
    
    if request.method == 'POST':
        # Handle Edit Category form
        name = request.POST.get('category_name')
        description = request.POST.get('category_description')
        icon = request.POST.get('category_icon')
        if name:
            category.name = name
            category.description = description
            category.icon = icon
            category.save()
            messages.success(request, 'Category updated successfully')
        else:
            messages.error(request, 'Category name is required')
        # Preserve pagination parameters when redirecting
        programs_page = request.GET.get('programs_page', 1)
        categories_page = request.GET.get('categories_page', 1)
        return redirect(f'/dashboard/programs/?programs_page={programs_page}&categories_page={categories_page}')
    
    # GET request - show edit form
    user = request.user
    categories_list = Category.objects.all().order_by('-id')
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
    categories_paginator = Paginator(categories_list, 5)
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
        'edit_category': category  # Pass the category to edit
    }
    return render(request, 'dashboard/programs.html', context)

@admin_required
def delete_category_view(request, id):
    """Delete category view""" 
    try:
        category = Category.objects.get(id=id)
        category.delete()
        messages.success(request, 'Category deleted successfully')
    except Category.DoesNotExist:
        messages.error(request, 'Category not found')
    # Preserve pagination parameters when redirecting
    programs_page = request.GET.get('programs_page', 1)
    categories_page = request.GET.get('categories_page', 1)
    return redirect(f'/dashboard/programs/?programs_page={programs_page}&categories_page={categories_page}')

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
                                        topic.video_duration = calculate_video_duration(topic.video_file)
                                    
                                    topic.save()
                                else:
                                    # Create new topic
                                    video_file = None
                                    video_duration = None
                                    
                                    if f'modules[{module_index}][topics][{topic_index}][video_file]' in request.FILES:
                                        video_file = request.FILES[f'modules[{module_index}][topics][{topic_index}][video_file]']
                                        video_duration = calculate_video_duration(video_file)
                                    
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
    
    # Preserve pagination parameters when redirecting
    programs_page = request.GET.get('programs_page', 1)
    categories_page = request.GET.get('categories_page', 1)
    return redirect(f'/dashboard/programs/?programs_page={programs_page}&categories_page={categories_page}')

@admin_required
def students_view(request):
    """Students view with statistics and student list"""
    from django.utils import timezone
    from django.db.models import Count
    from topgrade_api.models import CustomUser, UserPurchase
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    # Handle POST request for adding new student
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'add_student':
            fullname = request.POST.get('fullname')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')
            area_of_intrest = request.POST.get('area_of_intrest')
            
            if fullname and email and password:
                try:
                    # Check if email already exists
                    if CustomUser.objects.filter(email=email).exists():
                        messages.error(request, 'A user with this email already exists.')
                    else:
                        # Create new student
                        student = CustomUser.objects.create_user(
                            email=email,
                            password=password,
                            fullname=fullname,
                            phone_number=phone_number,
                            area_of_intrest=area_of_intrest,
                            role='student'
                        )
                        messages.success(request, f'Student "{fullname}" has been added successfully.')
                except Exception as e:
                    messages.error(request, f'Error creating student: {str(e)}')
            else:
                messages.error(request, 'Full name, email, and password are required.')
        
        elif form_type == 'delete_student':
            student_id = request.POST.get('student_id')
            if student_id:
                try:
                    student = CustomUser.objects.get(id=student_id, role='student')
                    student_name = student.fullname or student.username or student.email
                    student.delete()
                    messages.success(request, f'Student "{student_name}" has been deleted successfully.')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Student not found.')
                except Exception as e:
                    messages.error(request, f'Error deleting student: {str(e)}')
            else:
                messages.error(request, 'Student ID is required for deletion.')
        
        return redirect('dashboard:students')
    
    # Calculate statistics
    today = timezone.now().date()
    
    # Get all students
    all_students = CustomUser.objects.filter(role='student')
    total_students = all_students.count()
    
    # Students enrolled today
    today_enrolled = all_students.filter(date_joined__date=today).count()
    
    # Most popular area of interest
    popular_interest = all_students.exclude(area_of_intrest__isnull=True)\
                                 .exclude(area_of_intrest__exact='')\
                                 .values('area_of_intrest')\
                                 .annotate(count=Count('area_of_intrest'))\
                                 .order_by('-count')\
                                 .first()
    
    high_interest_area = popular_interest['area_of_intrest'] if popular_interest else 'N/A'
    high_interest_count = popular_interest['count'] if popular_interest else 0
    
    # Students with purchases (active learners)
    active_students = CustomUser.objects.filter(
        role='student',
        purchases__status='completed'
    ).distinct().count()
    
    # Get students list with pagination
    students_list = all_students.select_related().order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(students_list, 10)  # Show 10 students per page
    page = request.GET.get('page')
    
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
    
    # Pagination range logic
    current_page = students.number
    total_pages = paginator.num_pages
    
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    
    if end_page - start_page < 4:
        if start_page == 1:
            end_page = min(total_pages, start_page + 4)
        elif end_page == total_pages:
            start_page = max(1, end_page - 4)
    
    page_range = range(start_page, end_page + 1)
    
    context = {
        'user': request.user,
        'total_students': total_students,
        'today_enrolled': today_enrolled,
        'high_interest_area': high_interest_area,
        'high_interest_count': high_interest_count,
        'active_students': active_students,
        'students': students,
        'page_range': page_range,
        'total_pages': total_pages,
        'current_page': current_page,
    }
    
    return render(request, 'dashboard/students.html', context)

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
