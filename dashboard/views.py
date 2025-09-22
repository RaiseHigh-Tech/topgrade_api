from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from topgrade_api.models import Category, Program, Syllabus, Topic

User = get_user_model()

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
                                    Topic.objects.create(
                                        syllabus=syllabus,
                                        topic_title=topic_data['title'],
                                        description=topic_data.get('description', '')
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
                                Topic.objects.create(
                                    syllabus=syllabus,
                                    topic_title=topic_data['title'],
                                    description=topic_data.get('description', '')
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
