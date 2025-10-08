from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json
from topgrade_api.models import ProgramEnquiry
from .auth_view import admin_required


@admin_required
def program_enquiries(request):
    """Program enquiries management view"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    enquiries = ProgramEnquiry.objects.all().order_by('-created_at')
    
    # Apply filters
    if status_filter != 'all':
        enquiries = enquiries.filter(status=status_filter)
    
    if search_query:
        enquiries = enquiries.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(program__title__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(enquiries, 10)  # Show 10 enquiries per page
    page = request.GET.get('page')
    
    try:
        enquiries_page = paginator.page(page)
    except PageNotAnInteger:
        enquiries_page = paginator.page(1)
    except EmptyPage:
        enquiries_page = paginator.page(paginator.num_pages)
    
    # Get counts for different statuses
    total_count = ProgramEnquiry.objects.count()
    pending_count = ProgramEnquiry.objects.filter(status='pending').count()
    contacted_count = ProgramEnquiry.objects.filter(status='contacted').count()
    converted_count = ProgramEnquiry.objects.filter(status='converted').count()
    closed_count = ProgramEnquiry.objects.filter(status='closed').count()
    
    context = {
        'user': request.user,
        'enquiries': enquiries_page,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_count': total_count,
        'pending_count': pending_count,
        'contacted_count': contacted_count,
        'converted_count': converted_count,
        'closed_count': closed_count,
    }
    return render(request, 'dashboard/program_enquiries.html', context)


@admin_required
@require_POST
@csrf_exempt
def update_enquiry_status(request):
    """Update enquiry status via AJAX"""
    try:
        data = json.loads(request.body)
        enquiry_id = data.get('enquiry_id')
        new_status = data.get('status')
        
        if not enquiry_id or not new_status:
            return JsonResponse({
                'success': False,
                'message': 'Enquiry ID and status are required'
            })
        
        enquiry = ProgramEnquiry.objects.get(id=enquiry_id)
        enquiry.status = new_status
        enquiry.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status updated to {new_status.title()}'
        })
        
    except ProgramEnquiry.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Enquiry not found'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating status: {str(e)}'
        })


@admin_required
@require_POST
@csrf_exempt
def assign_enquiry(request):
    """Assign enquiry to staff member via AJAX"""
    try:
        data = json.loads(request.body)
        enquiry_id = data.get('enquiry_id')
        assigned_to = data.get('assigned_to')
        
        if not enquiry_id:
            return JsonResponse({
                'success': False,
                'message': 'Enquiry ID is required'
            })
        
        enquiry = ProgramEnquiry.objects.get(id=enquiry_id)
        enquiry.assigned_to = assigned_to
        enquiry.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Enquiry assigned to {assigned_to}' if assigned_to else 'Assignment removed'
        })
        
    except ProgramEnquiry.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Enquiry not found'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error assigning enquiry: {str(e)}'
        })