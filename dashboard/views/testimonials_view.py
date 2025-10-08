from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from topgrade_api.models import Testimonial
from .auth_view import admin_required


@admin_required
def testimonials_view(request):
    """Testimonials management view"""
    testimonials = Testimonial.objects.all().order_by('-created_at')
    context = {
        'user': request.user,
        'testimonials': testimonials
    }
    return render(request, 'dashboard/testimonials.html', context)

@admin_required
def add_testimonial(request):
    """Add new testimonial"""
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        program_name = request.POST.get('program_name')
        student_image = request.FILES.get('student_image')
        
        if student_name and content and rating:
            try:
                testimonial = Testimonial.objects.create(
                    student_name=student_name,
                    content=content,
                    rating=int(rating),
                    program_name=program_name or '',
                    student_image=student_image,
                    is_active=True
                )
                messages.success(request, 'Testimonial added successfully')
            except Exception as e:
                messages.error(request, f'Error adding testimonial: {str(e)}')
        else:
            messages.error(request, 'Student name, content, and rating are required')
    
    return redirect('dashboard:testimonials')

@admin_required
def edit_testimonial(request, testimonial_id):
    """Edit testimonial"""
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
    except Testimonial.DoesNotExist:
        messages.error(request, 'Testimonial not found')
        return redirect('dashboard:testimonials')
    
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        program_name = request.POST.get('program_name')
        student_image = request.FILES.get('student_image')
        
        if student_name and content and rating:
            try:
                testimonial.student_name = student_name
                testimonial.content = content
                testimonial.rating = int(rating)
                testimonial.program_name = program_name or ''
                if student_image:
                    testimonial.student_image = student_image
                testimonial.save()
                messages.success(request, 'Testimonial updated successfully')
            except Exception as e:
                messages.error(request, f'Error updating testimonial: {str(e)}')
        else:
            messages.error(request, 'Student name, content, and rating are required')
    
    return redirect('dashboard:testimonials')

@admin_required
def delete_testimonial(request, testimonial_id):
    """Delete testimonial"""
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        testimonial.delete()
        messages.success(request, 'Testimonial deleted successfully')
    except Testimonial.DoesNotExist:
        messages.error(request, 'Testimonial not found')
    except Exception as e:
        messages.error(request, f'Error deleting testimonial: {str(e)}')
    
    return redirect('dashboard:testimonials')

@admin_required
@require_POST
@csrf_exempt
def toggle_testimonial_status(request, testimonial_id):
    """Toggle testimonial active status"""
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        testimonial.is_active = not testimonial.is_active
        testimonial.save()
        
        return JsonResponse({
            'success': True,
            'is_active': testimonial.is_active,
            'message': f'Testimonial {"activated" if testimonial.is_active else "deactivated"} successfully'
        })
    except Testimonial.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Testimonial not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating testimonial: {str(e)}'
        })