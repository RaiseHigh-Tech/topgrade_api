from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from topgrade_api.models import CustomUser, UserCourseProgress, UserCertificate
from .auth_view import admin_required
from dashboard.utils import generate_certificate_pdf


@admin_required
def student_certificates_view(request):
    """Student certificates view - List students who completed courses"""
    
    # Handle POST requests for certificate actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate_certificate':
            course_progress_id = request.POST.get('course_progress_id')
            if course_progress_id:
                try:
                    course_progress = UserCourseProgress.objects.get(id=course_progress_id, is_completed=True)
                    
                    # Check if certificate already exists
                    certificate, created = UserCertificate.objects.get_or_create(
                        user=course_progress.user,
                        course_progress=course_progress,
                        program=course_progress.purchase.program,
                        defaults={
                            'status': 'pending',
                        }
                    )
                    
                    # Generate PDF certificate
                    pdf_file = generate_certificate_pdf(
                        user=course_progress.user,
                        program=course_progress.purchase.program,
                        certificate_number=certificate.certificate_number,
                        completion_date=course_progress.completed_at
                    )
                    
                    # Save the PDF file to the certificate
                    certificate.certificate_file.save(
                        f"certificate_{certificate.certificate_number}.pdf",
                        pdf_file,
                        save=True
                    )
                    
                    messages.success(request, f'Certificate generated successfully for {course_progress.user.fullname or course_progress.user.email}')
                    
                except UserCourseProgress.DoesNotExist:
                    messages.error(request, 'Course progress not found or not completed')
                except Exception as e:
                    messages.error(request, f'Error generating certificate: {str(e)}')
            else:
                messages.error(request, 'Course progress ID is required')
        
        elif action == 'send_certificate':
            course_progress_id = request.POST.get('course_progress_id')
            if course_progress_id:
                try:
                    course_progress = UserCourseProgress.objects.get(id=course_progress_id, is_completed=True)
                    
                    # Check if certificate already exists
                    certificate, created = UserCertificate.objects.get_or_create(
                        user=course_progress.user,
                        course_progress=course_progress,
                        program=course_progress.purchase.program,
                        defaults={
                            'status': 'sent',
                            'sent_date': timezone.now()
                        }
                    )
                    
                    if created:
                        messages.success(request, f'Certificate sent to {course_progress.user.fullname or course_progress.user.email} for {course_progress.purchase.program.title}')
                    else:
                        # Update existing certificate
                        if certificate.status == 'pending':
                            certificate.status = 'sent'
                            certificate.sent_date = timezone.now()
                            certificate.save()
                            messages.success(request, f'Certificate status updated to "Sent" for {course_progress.user.fullname or course_progress.user.email}')
                        else:
                            messages.info(request, f'Certificate already sent to {course_progress.user.fullname or course_progress.user.email}')
                    
                except UserCourseProgress.DoesNotExist:
                    messages.error(request, 'Course progress not found or not completed')
                except Exception as e:
                    messages.error(request, f'Error sending certificate: {str(e)}')
            else:
                messages.error(request, 'Course progress ID is required')
        
        return redirect('dashboard:student_certificates')
    
    # GET request - display list of completed courses
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'all')
    
    # Get all completed course progress records
    completed_courses = UserCourseProgress.objects.filter(
        is_completed=True
    ).select_related(
        'user', 'purchase__program', 'purchase__program__category'
    ).order_by('-completed_at')
    
    # Apply search filter
    if search_query:
        completed_courses = completed_courses.filter(
            Q(user__fullname__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(purchase__program__title__icontains=search_query)
        )
    
    # Annotate with certificate information
    completed_courses_with_certs = []
    for course_progress in completed_courses:
        try:
            certificate = UserCertificate.objects.get(course_progress=course_progress)
            has_certificate = True
            certificate_status = certificate.status
            certificate_number = certificate.certificate_number
            certificate_sent_date = certificate.sent_date
            certificate_obj = certificate
        except UserCertificate.DoesNotExist:
            has_certificate = False
            certificate_status = 'not_issued'
            certificate_number = None
            certificate_sent_date = None
            certificate_obj = None
        
        completed_courses_with_certs.append({
            'course_progress': course_progress,
            'has_certificate': has_certificate,
            'certificate_status': certificate_status,
            'certificate_number': certificate_number,
            'certificate_sent_date': certificate_sent_date,
            'certificate_obj': certificate_obj,
        })
    
    # Apply status filter
    if status_filter == 'sent':
        completed_courses_with_certs = [item for item in completed_courses_with_certs if item['certificate_status'] == 'sent']
    elif status_filter == 'pending':
        completed_courses_with_certs = [item for item in completed_courses_with_certs if item['certificate_status'] in ['pending', 'not_issued']]
    
    # Calculate statistics
    total_completed = completed_courses.count()
    total_certificates_sent = UserCertificate.objects.filter(status='sent').count()
    total_certificates_pending = total_completed - total_certificates_sent
    
    # Pagination
    paginator = Paginator(completed_courses_with_certs, 15)  # Show 15 per page
    page = request.GET.get('page')
    
    try:
        completed_courses_page = paginator.page(page)
    except PageNotAnInteger:
        completed_courses_page = paginator.page(1)
    except EmptyPage:
        completed_courses_page = paginator.page(paginator.num_pages)
    
    # Pagination range logic
    current_page = completed_courses_page.number
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
        'completed_courses': completed_courses_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_completed': total_completed,
        'total_certificates_sent': total_certificates_sent,
        'total_certificates_pending': total_certificates_pending,
        'page_range': page_range,
        'total_pages': total_pages,
        'current_page': current_page,
    }
    return render(request, 'dashboard/student_certificates.html', context)
