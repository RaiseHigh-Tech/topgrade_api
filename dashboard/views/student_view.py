from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Count, Q
from topgrade_api.models import CustomUser, UserPurchase, Program, Category
from .auth_view import admin_required

User = get_user_model()

@admin_required
def students_view(request):
    """Students view with statistics and student list"""
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
        'students': students,
        'total_students': total_students,
        'today_enrolled': today_enrolled,
        'high_interest_area': high_interest_area,
        'high_interest_count': high_interest_count,
        'active_students': active_students,
        'page_range': page_range,
        'total_pages': total_pages,
        'current_page': current_page,
    }
    return render(request, 'dashboard/students.html', context)

@admin_required
def student_details_view(request, student_id):
    """Student details view"""
    try:
        student = CustomUser.objects.get(id=student_id, role='student')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Student not found')
        return redirect('dashboard:students')
    
    # Get student's purchases/enrollments
    purchases = UserPurchase.objects.filter(user=student).select_related('program').order_by('-purchase_date')
    
    # Calculate statistics for this student
    total_enrollments = purchases.count()
    completed_enrollments = purchases.filter(status='completed').count()
    pending_enrollments = purchases.filter(status='pending').count()
    total_amount_paid = purchases.filter(status='completed').aggregate(
        total=models.Sum('amount_paid')
    )['total'] or 0
    
    context = {
        'user': request.user,
        'student': student,
        'purchases': purchases,
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'pending_enrollments': pending_enrollments,
        'total_amount_paid': total_amount_paid,
    }
    return render(request, 'dashboard/student_details.html', context)

@admin_required
def assign_programs_view(request):
    """Assign programs to students view"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        program_id = request.POST.get('program_id')
        amount_paid = request.POST.get('amount_paid', 0)
        
        if student_id and program_id:
            try:
                student = CustomUser.objects.get(id=student_id, role='student')
                program = Program.objects.get(id=program_id)
                
                # Check if student already has this program
                existing_purchase = UserPurchase.objects.filter(
                    user=student,
                    program=program
                ).first()
                
                if existing_purchase:
                    messages.warning(request, f'{student.fullname or student.email} is already enrolled in {program.title}')
                else:
                    # Create new purchase/enrollment
                    purchase = UserPurchase.objects.create(
                        user=student,
                        program=program,
                        amount_paid=float(amount_paid) if amount_paid else 0.0,
                        status='completed',
                        purchase_date=timezone.now()
                    )
                    messages.success(request, f'Successfully assigned {program.title} to {student.fullname or student.email}')
                    
            except CustomUser.DoesNotExist:
                messages.error(request, 'Student not found')
            except Program.DoesNotExist:
                messages.error(request, 'Program not found')
            except Exception as e:
                messages.error(request, f'Error assigning program: {str(e)}')
        else:
            messages.error(request, 'Student and program selection are required')
        
        return redirect('dashboard:assign_programs')
    
    # GET request - show assignment form
    students = CustomUser.objects.filter(role='student').order_by('fullname', 'email')
    programs = Program.objects.all().order_by('title')
    categories = Category.objects.all().order_by('name')
    
    # Recent assignments
    recent_assignments = UserPurchase.objects.select_related('user', 'program').order_by('-purchase_date')[:10]
    
    context = {
        'user': request.user,
        'students': students,
        'programs': programs,
        'categories': categories,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'dashboard/assign_programs.html', context)
