from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from topgrade_api.models import Category, Program, Syllabus, Topic

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
    Dashboard home view - only accessible by admin users (superusers)
    """
    context = {
        'user': request.user,
        'total_students': User.objects.filter(role='student').count(),
        'total_admins': User.objects.filter(is_superuser=True).count(),
    }
    return render(request, 'dashboard/base.html', context)

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
                
                # Handle syllabus and topics update
                # First, delete existing syllabus and topics
                program.syllabuses.all().delete()
                
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
def adv_program_view(request):
    """Advance Programs view with CRUD operations"""
    from topgrade_api.models import AdvanceProgram, AdvanceSyllabus, AdvanceTopic
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    # Handle POST request for adding new advance program
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'advance_program':
            title = request.POST.get('advance_program_title')
            subtitle = request.POST.get('advance_program_subtitle')
            description = request.POST.get('advance_program_description')
            image = request.FILES.get('advance_program_image')
            icon = request.POST.get('advance_program_icon')
            batch_starts = request.POST.get('advance_batch_starts')
            available_slots = request.POST.get('advance_available_slots')
            duration = request.POST.get('advance_duration')
            price = request.POST.get('advance_price')
            discount_percentage = request.POST.get('advance_discount_percentage')
            program_rating = request.POST.get('advance_program_rating')
            job_openings = request.POST.get('advance_job_openings')
            global_market_size = request.POST.get('advance_global_market_size')
            avg_annual_salary = request.POST.get('advance_avg_annual_salary')
            is_best_seller = request.POST.get('advance_is_best_seller') == 'on'
            
            if title and batch_starts and available_slots and duration and price:
                try:
                    advance_program = AdvanceProgram.objects.create(
                        title=title,
                        subtitle=subtitle,
                        description=description,
                        image=image,
                        icon=icon,
                        batch_starts=batch_starts,
                        available_slots=int(available_slots),
                        duration=duration,
                        price=float(price),
                        discount_percentage=float(discount_percentage) if discount_percentage else 0.0,
                        program_rating=float(program_rating) if program_rating else 0.0,
                        job_openings=job_openings or '',
                        global_market_size=global_market_size or '',
                        avg_annual_salary=avg_annual_salary or '',
                        is_best_seller=is_best_seller
                    )
                    messages.success(request, f'Advance Program "{title}" has been added successfully.')
                except ValueError as e:
                    messages.error(request, f'Invalid input: {str(e)}')
                except Exception as e:
                    messages.error(request, f'Error creating advance program: {str(e)}')
            else:
                messages.error(request, 'Title, batch starts, available slots, duration, and price are required.')
        
        return redirect('dashboard:adv_programs')
    
    # Get advance programs list with pagination
    advance_programs_list = AdvanceProgram.objects.all().order_by('-id')
    
    # Pagination
    paginator = Paginator(advance_programs_list, 9)  # Show 9 programs per page
    page = request.GET.get('page')
    
    try:
        advance_programs = paginator.page(page)
    except PageNotAnInteger:
        advance_programs = paginator.page(1)
    except EmptyPage:
        advance_programs = paginator.page(paginator.num_pages)
    
    # Pagination range logic
    current_page = advance_programs.number
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
        'advance_programs': advance_programs,
        'page_range': page_range,
        'total_pages': total_pages,
        'current_page': current_page,
    }
    
    return render(request, 'dashboard/advance_programs.html', context)

@admin_required
def edit_advance_program_view(request, id):
    """Edit advance program view"""
    from topgrade_api.models import AdvanceProgram
    
    try:
        advance_program = AdvanceProgram.objects.get(id=id)
    except AdvanceProgram.DoesNotExist:
        messages.error(request, 'Advance Program not found')
        return redirect('dashboard:adv_programs')
    
    if request.method == 'POST':
        # Handle Edit Advance Program form
        title = request.POST.get('advance_program_title')
        subtitle = request.POST.get('advance_program_subtitle')
        description = request.POST.get('advance_program_description')
        image = request.FILES.get('advance_program_image')
        icon = request.POST.get('advance_program_icon')
        batch_starts = request.POST.get('advance_batch_starts')
        available_slots = request.POST.get('advance_available_slots')
        duration = request.POST.get('advance_duration')
        price = request.POST.get('advance_price')
        discount_percentage = request.POST.get('advance_discount_percentage')
        program_rating = request.POST.get('advance_program_rating')
        job_openings = request.POST.get('advance_job_openings')
        global_market_size = request.POST.get('advance_global_market_size')
        avg_annual_salary = request.POST.get('advance_avg_annual_salary')
        is_best_seller = request.POST.get('advance_is_best_seller') == 'on'
        
        if title and batch_starts and available_slots and duration and price:
            try:
                advance_program.title = title
                advance_program.subtitle = subtitle
                advance_program.description = description
                if image:  # Only update image if new one is provided
                    advance_program.image = image
                advance_program.icon = icon
                advance_program.batch_starts = batch_starts
                advance_program.available_slots = int(available_slots)
                advance_program.duration = duration
                advance_program.price = float(price)
                advance_program.discount_percentage = float(discount_percentage) if discount_percentage else 0.0
                advance_program.program_rating = float(program_rating) if program_rating else 0.0
                advance_program.job_openings = job_openings or ''
                advance_program.global_market_size = global_market_size or ''
                advance_program.avg_annual_salary = avg_annual_salary or ''
                advance_program.is_best_seller = is_best_seller
                advance_program.save()
                
                messages.success(request, 'Advance Program updated successfully')
            except ValueError as e:
                messages.error(request, f'Invalid input: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error updating advance program: {str(e)}')
        else:
            messages.error(request, 'Title, batch starts, available slots, duration, and price are required')
        
        # Preserve pagination parameters when redirecting
        page = request.GET.get('page', 1)
        return redirect(f'/dashboard/adv_program/?page={page}')
    
    # For GET request, we would need to show the edit form (can be implemented as modal or separate page)
    return redirect('dashboard:adv_programs')

@admin_required
def delete_advance_program_view(request, id):
    """Delete advance program view"""
    from topgrade_api.models import AdvanceProgram
    
    try:
        advance_program = AdvanceProgram.objects.get(id=id)
        program_title = advance_program.title
        advance_program.delete()
        messages.success(request, f'Advance Program "{program_title}" deleted successfully')
    except AdvanceProgram.DoesNotExist:
        messages.error(request, 'Advance Program not found')
    except Exception as e:
        messages.error(request, f'Error deleting advance program: {str(e)}')
    
    # Preserve pagination parameters when redirecting
    page = request.GET.get('page', 1)
    return redirect(f'/dashboard/adv_program/?page={page}')

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
