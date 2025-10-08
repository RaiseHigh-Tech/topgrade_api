from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
import json
from topgrade_api.models import ProgramEnquiry
from .auth_view import admin_required


@admin_required
def program_enquiries(request):
    """Program enquiries management view"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    program_filter = request.GET.get('program', '')
    assigned_filter = request.GET.get('assigned', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    enquiries = ProgramEnquiry.objects.select_related('program', 'assigned_to').all().order_by('-created_at')
    
    # Apply filters
    if status_filter != 'all':
        enquiries = enquiries.filter(follow_up_status=status_filter)
    
    if program_filter:
        enquiries = enquiries.filter(program_id=program_filter)
    
    if assigned_filter == 'unassigned':
        enquiries = enquiries.filter(assigned_to__isnull=True)
    elif assigned_filter:
        enquiries = enquiries.filter(assigned_to_id=assigned_filter)
    
    if search_query:
        enquiries = enquiries.filter(
            Q(first_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
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
    new_count = ProgramEnquiry.objects.filter(follow_up_status='new').count()
    contacted_count = ProgramEnquiry.objects.filter(follow_up_status='contacted').count()
    interested_count = ProgramEnquiry.objects.filter(follow_up_status='interested').count()
    enrolled_count = ProgramEnquiry.objects.filter(follow_up_status='enrolled').count()
    closed_count = ProgramEnquiry.objects.filter(follow_up_status='closed').count()
    
    # Calculate needs_follow_up count
    needs_follow_up_count = sum([
        ProgramEnquiry.objects.filter(follow_up_status='new', created_at__lt=timezone.now() - timezone.timedelta(days=1)).count(),
        ProgramEnquiry.objects.filter(follow_up_status='contacted', created_at__lt=timezone.now() - timezone.timedelta(days=3)).count(),
        ProgramEnquiry.objects.filter(follow_up_status='follow_up_needed').count(),
    ])
    
    # Get all programs for filter dropdown
    from topgrade_api.models import Program
    programs = Program.objects.all()
    
    # Get all staff members for assignment dropdown
    from django.contrib.auth import get_user_model
    User = get_user_model()
    staff_members = User.objects.filter(role__in=['admin', 'operations_staff'])
    
    context = {
        'user': request.user,
        'page_obj': enquiries_page,  # Template expects 'page_obj'
        'stats': {  # Template expects 'stats' object
            'total': total_count,
            'new': new_count,
            'needs_follow_up': needs_follow_up_count,
            'enrolled': enrolled_count,
        },
        'current_filters': {  # Template expects 'current_filters' object
            'search': search_query,
            'status': status_filter,
            'program': program_filter,
            'assigned': assigned_filter,
        },
        'programs': programs,
        'staff_members': staff_members,
        'status_choices': ProgramEnquiry.FOLLOW_UP_STATUS_CHOICES,
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
        enquiry.follow_up_status = new_status
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
        staff_id = data.get('staff_id')
        
        if not enquiry_id:
            return JsonResponse({
                'success': False,
                'message': 'Enquiry ID is required'
            })
        
        enquiry = ProgramEnquiry.objects.get(id=enquiry_id)
        
        if staff_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                staff_member = User.objects.get(id=staff_id)
                enquiry.assigned_to = staff_member
                message = f'Enquiry assigned to {staff_member.email}'
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Staff member not found'
                })
        else:
            enquiry.assigned_to = None
            message = 'Assignment removed'
        
        enquiry.save()
        
        return JsonResponse({
            'success': True,
            'message': message
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