from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from topgrade_api.models import Certificate
from .auth_view import admin_required


@admin_required
def certificates_view(request):
    """Certificates management view"""
    certificates = Certificate.objects.all().order_by('-created_at')
    context = {
        'user': request.user,
        'certificates': certificates
    }
    return render(request, 'dashboard/certificates.html', context)

@admin_required
def add_certificate(request):
    """Add new certificate"""
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        program_name = request.POST.get('program_name')
        completion_date = request.POST.get('completion_date')
        certificate_id = request.POST.get('certificate_id')
        grade = request.POST.get('grade')
        
        if student_name and program_name and completion_date and certificate_id:
            try:
                certificate = Certificate.objects.create(
                    student_name=student_name,
                    program_name=program_name,
                    completion_date=completion_date,
                    certificate_id=certificate_id,
                    grade=grade or ''
                )
                messages.success(request, 'Certificate added successfully')
            except Exception as e:
                messages.error(request, f'Error adding certificate: {str(e)}')
        else:
            messages.error(request, 'Student name, program name, completion date, and certificate ID are required')
    
    return redirect('dashboard:certificates')

@admin_required
def edit_certificate(request, certificate_id):
    """Edit certificate"""
    try:
        certificate = Certificate.objects.get(id=certificate_id)
    except Certificate.DoesNotExist:
        messages.error(request, 'Certificate not found')
        return redirect('dashboard:certificates')
    
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        program_name = request.POST.get('program_name')
        completion_date = request.POST.get('completion_date')
        cert_id = request.POST.get('certificate_id')
        grade = request.POST.get('grade')
        
        if student_name and program_name and completion_date and cert_id:
            try:
                certificate.student_name = student_name
                certificate.program_name = program_name
                certificate.completion_date = completion_date
                certificate.certificate_id = cert_id
                certificate.grade = grade or ''
                certificate.save()
                messages.success(request, 'Certificate updated successfully')
            except Exception as e:
                messages.error(request, f'Error updating certificate: {str(e)}')
        else:
            messages.error(request, 'Student name, program name, completion date, and certificate ID are required')
    
    return redirect('dashboard:certificates')

@admin_required
def delete_certificate(request, certificate_id):
    """Delete certificate"""
    try:
        certificate = Certificate.objects.get(id=certificate_id)
        certificate.delete()
        messages.success(request, 'Certificate deleted successfully')
    except Certificate.DoesNotExist:
        messages.error(request, 'Certificate not found')
    except Exception as e:
        messages.error(request, f'Error deleting certificate: {str(e)}')
    
    return redirect('dashboard:certificates')