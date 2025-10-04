from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from topgrade_api.models import Category, Program, Carousel, Testimonial, ProgramEnquiry

# Create your views here.
def index(request):
    # Get all categories except 'Advanced Program' that have at least one program
    categories = Category.objects.exclude(name='Advanced Program').filter(programs__isnull=False).distinct()
    # Get all programs (including advanced programs)
    programs = Program.get_regular_programs()
    # Get advanced programs list
    advance_programs = Program.get_advanced_programs()
    # Get active testimonials for display
    testimonials = Testimonial.objects.filter(is_active=True).order_by('created_at')
    
    context = {
        'categories': categories,
        'programs': programs,
        'advance_programs': advance_programs,
        'testimonials': testimonials
    }
    return render(request, 'website/index.html', context)

def about(request):
    """About page"""
    # Get all categories except 'Advanced Program' that have at least one program
    categories = Category.objects.exclude(name='Advanced Program').filter(programs__isnull=False).distinct()
    # Get all programs (including advanced programs)
    programs = Program.get_regular_programs()
    # Get advanced programs list
    advance_programs = Program.get_advanced_programs()

    context = {
        'categories': categories,
        'programs': programs,
        'advance_programs': advance_programs,
    }
    return render(request, 'website/about.html', context)

def blog(request):
    """Blog page"""
    # Get all categories except 'Advanced Program' that have at least one program
    categories = Category.objects.exclude(name='Advanced Program').filter(programs__isnull=False).distinct()
    # Get all programs (including advanced programs)
    programs = Program.get_regular_programs()
    # Get advanced programs list
    advance_programs = Program.get_advanced_programs()

    context = {
        'categories': categories,
        'programs': programs,
        'advance_programs': advance_programs,
    }
    return render(request, 'website/blog.html', context)

def programs(request):
    """Programs page - shows first available program or specific program"""
    # Get all regular programs
    programs_queryset = Program.get_regular_programs()
    
    # Get specific program ID from URL parameter if provided
    program_id = request.GET.get('id')
    
    if program_id:
        try:
            program = programs_queryset.get(id=program_id)
        except Program.DoesNotExist:
            # If program not found, get first available program
            program = programs_queryset.first()
    else:
        # Get first available program
        program = programs_queryset.first()
    
    context = {
        'program': program,
        'programs': programs_queryset,  # All programs for any navigation needs
    }
    return render(request, 'website/programs.html', context)

def advance_programs(request):
    """Advanced programs listing page with filtering and pagination"""
    # Get query parameters
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Base queryset - advanced programs only
    programs_queryset = Program.get_advanced_programs()
    
    # Apply search filter
    if search_query:
        programs_queryset = programs_queryset.filter(
            title__icontains=search_query
        )
    
    # Apply sorting
    valid_sort_options = ['-created_at', 'created_at', 'title', '-title', 'price', '-price', '-program_rating']
    if sort_by in valid_sort_options:
        programs_queryset = programs_queryset.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(programs_queryset, 12)  # 12 programs per page
    page_number = request.GET.get('page')
    programs = paginator.get_page(page_number)
    
    context = {
        'programs': programs,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_programs': programs_queryset.count(),
        'is_advanced': True,  # Flag to identify this is advanced programs page
    }
    return render(request, 'website/advance_programs.html', context)

def contact(request):
    """Contact page"""
    # Get all categories except 'Advanced Program' that have at least one program
    categories = Category.objects.exclude(name='Advanced Program').filter(programs__isnull=False).distinct()
    # Get all programs (including advanced programs)
    programs = Program.get_regular_programs()
    # Get advanced programs list
    advance_programs = Program.get_advanced_programs()

    context = {
        'categories': categories,
        'programs': programs,
        'advance_programs': advance_programs,
    }
    return render(request, 'website/contact.html', context)

def program_detail(request, program_id):
    """Program detail page"""
    program = get_object_or_404(Program, id=program_id)
    # Get all categories except 'Advanced Program' that have at least one program
    categories = Category.objects.exclude(name='Advanced Program').filter(programs__isnull=False).distinct()
    # Get all programs (including advanced programs)
    programs = Program.get_regular_programs()
    # Get advanced programs list
    advance_programs = Program.get_advanced_programs()
    # Get active testimonials for display
    testimonials = Testimonial.objects.filter(is_active=True).order_by('created_at')
    # Get certificates for this program (max 2)
    certificates = program.certificates.all()[:2]
    
    context = {
        'program': program,
        'categories': categories,
        'programs': programs,
        'advance_programs': advance_programs,
        'testimonials': testimonials,
        'certificates': certificates,
    }
    return render(request, 'website/program_detail.html', context)

def advance_program_detail(request, advance_program_id):
    return render(request, 'website/advance_program_detail.html')

def program_list(request):
    """All programs listing page with filters and search"""
    # Get all programs
    programs = Program.objects.all().order_by('-created_at')
    
    # Get all categories
    categories = Category.objects.all().order_by('name')
    
    # Calculate statistics
    total_programs = programs.count()
    regular_programs_count = programs.exclude(category__name='Advanced Program').count()
    advanced_programs_count = programs.filter(category__name='Advanced Program').count()
    bestseller_count = programs.filter(is_best_seller=True).count()
    
    context = {
        'programs': programs,
        'categories': categories,
        'total_programs': total_programs,
        'regular_programs_count': regular_programs_count,
        'advanced_programs_count': advanced_programs_count,
        'bestseller_count': bestseller_count,
    }
    return render(request, 'website/program_list.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def submit_program_enquiry(request):
    """Handle program enquiry form submission via AJAX"""
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        
        # Extract form data
        first_name = data.get('first_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        email = data.get('email', '').strip()
        college_name = data.get('college_name', '').strip()
        program_id = data.get('program_id')
        
        # Validate required fields
        if not all([first_name, phone_number, email, college_name, program_id]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required.'
            }, status=400)
        
        # Validate email format
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address.'
            }, status=400)
        
        # Validate program exists
        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Invalid program selected.'
            }, status=400)
        
        # Check if enquiry already exists for this email and program
        existing_enquiry = ProgramEnquiry.objects.filter(
            email=email,
            program=program
        ).first()
        
        if existing_enquiry:
            # Update existing enquiry if it's older than 30 days or in closed status
            from django.utils import timezone
            days_since_enquiry = (timezone.now() - existing_enquiry.created_at).days
            
            if existing_enquiry.follow_up_status in ['closed', 'not_interested'] or days_since_enquiry > 30:
                # Update existing enquiry
                existing_enquiry.first_name = first_name
                existing_enquiry.phone_number = phone_number
                existing_enquiry.college_name = college_name
                existing_enquiry.follow_up_status = 'new'
                existing_enquiry.notes = f"Updated enquiry on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                existing_enquiry.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you! Your enquiry has been updated. Our team will contact you soon.',
                    'enquiry_id': existing_enquiry.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'You have already enquired about this program. Our team will contact you soon.'
                })
        
        # Create new enquiry
        enquiry = ProgramEnquiry.objects.create(
            program=program,
            first_name=first_name,
            phone_number=phone_number,
            email=email,
            college_name=college_name,
            follow_up_status='new'
        )
        
        # Optional: Send notification email to admin (uncomment if needed)
        # try:
        #     from django.core.mail import send_mail
        #     from django.conf import settings
        #     
        #     subject = f"New Program Enquiry - {program.title}"
        #     message = f"""
        #     New enquiry received:
        #     
        #     Name: {first_name}
        #     Email: {email}
        #     Phone: {phone_number}
        #     College: {college_name}
        #     Program: {program.title} - {program.subtitle}
        #     
        #     Please follow up with the student.
        #     """
        #     
        #     send_mail(
        #         subject,
        #         message,
        #         settings.DEFAULT_FROM_EMAIL,
        #         [settings.ADMIN_EMAIL],
        #         fail_silently=True
        #     )
        # except Exception as e:
        #     # Log error but don't fail the request
        #     print(f"Failed to send notification email: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your enquiry! Our team will contact you within 24 hours.',
            'enquiry_id': enquiry.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request format.'
        }, status=400)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in submit_program_enquiry: {e}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while processing your enquiry. Please try again.'
        }, status=500)
