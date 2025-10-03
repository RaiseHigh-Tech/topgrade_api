from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from topgrade_api.models import Category, Program, Carousel, Testimonial

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
    return render(request, 'website/about.html')

def blog(request):
    return render(request, 'website/blog.html')

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
    return render(request, 'website/contact.html')

def program_detail(request, program_id):
    """Program detail page"""
    program = get_object_or_404(Program, id=program_id)
    # Get all programs (including advanced programs)
    programs = Program.get_regular_programs()
    # Get advanced programs list
    advance_programs = Program.get_advanced_programs()
    # Get active testimonials for display
    testimonials = Testimonial.objects.filter(is_active=True).order_by('created_at')
    
    context = {
        'program': program,
        'programs': programs,
        'advance_programs': advance_programs,
        'testimonials': testimonials,
    }
    return render(request, 'website/program_detail.html', context)

def advance_program_detail(request, advance_program_id):
    return render(request, 'website/advance_program_detail.html')
