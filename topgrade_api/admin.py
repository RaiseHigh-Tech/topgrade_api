from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, OTPVerification, PhoneOTPVerification,
    Category, Program, Syllabus, Topic, UserPurchase, UserBookmark,
    UserTopicProgress, UserCourseProgress, Carousel, Testimonial, Certificate,
    ProgramEnquiry, Contact
)

# Restrict admin access to superusers only
def admin_login_required(view_func):
    """
    Decorator to ensure only superusers can access Django admin
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Access denied. Only superusers can access the admin panel.")
        return view_func(request, *args, **kwargs)
    return wrapper

# Override admin site login
original_admin_view = admin.site.admin_view
admin.site.admin_view = lambda view, cacheable=False: original_admin_view(admin_login_required(view), cacheable)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'fullname', 'role', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'fullname', 'phone_number']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('fullname', 'phone_number', 'area_of_intrest')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'fullname', 'role'),
        }),
    )
    
    def has_module_permission(self, request):
        """Only superusers can access this module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only superusers can view users"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only superusers can add users"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only superusers can change users"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete users"""
        return request.user.is_superuser

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_verified', 'verified_at', 'expires_at', 'is_expired_status']
    list_filter = ['is_verified', 'verified_at', 'expires_at']
    search_fields = ['email']
    readonly_fields = ['verified_at']
    ordering = ['-expires_at']
    
    def is_expired_status(self, obj):
        return obj.is_expired()
    is_expired_status.boolean = True
    is_expired_status.short_description = 'Is Expired'
    
    def has_module_permission(self, request):
        """Only superusers can access this module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only superusers can view OTP verifications"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only superusers can add OTP verifications"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only superusers can change OTP verifications"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete OTP verifications"""
        return request.user.is_superuser


@admin.register(PhoneOTPVerification)
class PhoneOTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'is_verified', 'verified_at', 'expires_at', 'is_expired_status']
    list_filter = ['is_verified', 'verified_at', 'expires_at']
    search_fields = ['phone_number']
    readonly_fields = ['verified_at']
    ordering = ['-expires_at']
    
    def is_expired_status(self, obj):
        return obj.is_expired()
    is_expired_status.boolean = True
    is_expired_status.short_description = 'Is Expired'
    
    def has_module_permission(self, request):
        """Only superusers can access this module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only superusers can view phone OTP verifications"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only superusers can add phone OTP verifications"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only superusers can change phone OTP verifications"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete phone OTP verifications"""
        return request.user.is_superuser


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'category', 'price', 'discount_percentage', 'batch_starts', 'available_slots', 'is_best_seller']
    list_filter = ['category', 'is_best_seller', 'batch_starts']
    search_fields = ['title', 'subtitle']
    ordering = ['title']


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ['module_title', 'program']
    list_filter = ['program']
    search_fields = ['module_title']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['topic_title', 'syllabus', 'is_intro']
    list_filter = ['is_intro', 'syllabus__program']
    search_fields = ['topic_title']




@admin.register(UserPurchase)
class UserPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_program_title', 'get_program_type', 'purchase_date', 'status', 'amount_paid']
    list_filter = ['status', 'purchase_date', 'program__category']
    search_fields = ['user__email', 'program__title']
    ordering = ['-purchase_date']
    
    def get_program_title(self, obj):
        return obj.program.title if obj.program else "N/A"
    get_program_title.short_description = 'Program Title'
    
    def get_program_type(self, obj):
        return 'Advanced' if obj.program and obj.program.is_advanced else 'Regular'
    get_program_type.short_description = 'Program Type'


@admin.register(UserBookmark)
class UserBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_program_title', 'get_program_type', 'bookmarked_date']
    list_filter = ['bookmarked_date', 'program__category']
    search_fields = ['user__email', 'program__title']
    ordering = ['-bookmarked_date']
    
    def get_program_title(self, obj):
        return obj.program.title if obj.program else "N/A"
    get_program_title.short_description = 'Bookmarked Program'
    
    def get_program_type(self, obj):
        return 'Advanced' if obj.program and obj.program.is_advanced else 'Regular'
    get_program_type.short_description = 'Program Type'


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_topic_title', 'status', 'completion_percentage', 'watch_time_formatted', 'last_watched_at']
    list_filter = ['status', 'last_watched_at', 'topic__syllabus__program__category']
    search_fields = ['user__email', 'topic__topic_title']
    ordering = ['-last_watched_at']
    readonly_fields = ['completion_percentage', 'watch_percentage']
    
    def get_topic_title(self, obj):
        return obj.topic.topic_title if obj.topic else "N/A"
    get_topic_title.short_description = 'Topic'
    
    def watch_time_formatted(self, obj):
        hours = obj.watch_time_seconds // 3600
        minutes = (obj.watch_time_seconds % 3600) // 60
        seconds = obj.watch_time_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    watch_time_formatted.short_description = 'Watch Time'


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_program_title', 'completion_percentage', 'completed_topics', 'total_topics', 'is_completed', 'last_activity_at']
    list_filter = ['is_completed', 'last_activity_at', 'purchase__program__category']
    search_fields = ['user__email', 'purchase__program__title']
    ordering = ['-last_activity_at']
    readonly_fields = ['total_topics', 'completed_topics', 'in_progress_topics', 'completion_percentage', 'total_watch_time_formatted']
    
    def get_program_title(self, obj):
        return obj.get_program_title()
    get_program_title.short_description = 'Program'
    
    def total_watch_time_formatted(self, obj):
        hours = obj.total_watch_time_seconds // 3600
        minutes = (obj.total_watch_time_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    total_watch_time_formatted.short_description = 'Total Watch Time'


# Carousel Admin
@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    ordering = ('order', 'created_at')
    list_editable = ('is_active', 'order')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('image', 'is_active', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_of_study', 'is_active', 'created_at')
    list_filter = ('is_active', 'field_of_study', 'created_at')
    search_fields = ('name', 'field_of_study', 'title', 'content')
    ordering = ('created_at',)
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Student Information', {
            'fields': ('name', 'field_of_study')
        }),
        ('Testimonial Content', {
            'fields': ('title', 'content')
        }),
        ('Display Settings', {
            'fields': ('avatar_image', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Override to show active testimonials first"""
        qs = super().get_queryset(request)
        return qs.order_by('-is_active', 'created_at')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('program', 'certificate_image', 'created_at')
    list_filter = ('program', 'created_at')
    search_fields = ('program__title', 'program__subtitle')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Certificate Information', {
            'fields': ('program', 'certificate_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize the program dropdown to show title and subtitle"""
        if db_field.name == "program":
            kwargs["queryset"] = Program.objects.all().order_by('title')
            kwargs["empty_label"] = "Select a program..."
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        """Optimize query with program data"""
        qs = super().get_queryset(request)
        return qs.select_related('program')


@admin.register(ProgramEnquiry)
class ProgramEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'email', 'phone_number', 'get_program_title', 
        'follow_up_status', 'assigned_to', 'days_since_enquiry_display',
        'needs_follow_up_display', 'created_at'
    )
    list_filter = (
        'follow_up_status', 'program', 'assigned_to', 'created_at',
        'last_contacted'
    )
    search_fields = (
        'first_name', 'email', 'phone_number', 'college_name',
        'program__title', 'program__subtitle'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'days_since_enquiry_display')
    list_editable = ('follow_up_status', 'assigned_to')
    list_per_page = 50
    
    fieldsets = (
        ('Student Information', {
            'fields': ('first_name', 'email', 'phone_number', 'college_name')
        }),
        ('Program Details', {
            'fields': ('program',)
        }),
        ('Follow-up Management', {
            'fields': ('follow_up_status', 'assigned_to', 'last_contacted', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_contacted', 'mark_as_interested', 'mark_as_enrolled', 'assign_to_me']
    
    def get_program_title(self, obj):
        """Display program title and subtitle"""
        if obj.program:
            return f"{obj.program.title} - {obj.program.subtitle}"
        return "N/A"
    get_program_title.short_description = 'Program'
    get_program_title.admin_order_field = 'program__title'
    
    def days_since_enquiry_display(self, obj):
        """Display days since enquiry with color coding"""
        days = obj.days_since_enquiry
        if days == 0:
            return "Today"
        elif days == 1:
            return "1 day ago"
        else:
            return f"{days} days ago"
    days_since_enquiry_display.short_description = 'Days Since Enquiry'
    
    def needs_follow_up_display(self, obj):
        """Display if enquiry needs follow-up with visual indicator"""
        return obj.needs_follow_up
    needs_follow_up_display.boolean = True
    needs_follow_up_display.short_description = 'Needs Follow-up'
    
    def get_queryset(self, request):
        """Optimize query with related data"""
        qs = super().get_queryset(request)
        return qs.select_related('program', 'assigned_to')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize form fields"""
        if db_field.name == "program":
            kwargs["queryset"] = Program.objects.all().order_by('title')
            kwargs["empty_label"] = "Select a program..."
        elif db_field.name == "assigned_to":
            # Only show staff users for assignment
            kwargs["queryset"] = CustomUser.objects.filter(is_staff=True).order_by('fullname')
            kwargs["empty_label"] = "Assign to staff member..."
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Custom admin actions
    def mark_as_contacted(self, request, queryset):
        """Mark selected enquiries as contacted"""
        from django.utils import timezone
        updated = queryset.update(
            follow_up_status='contacted',
            last_contacted=timezone.now()
        )
        self.message_user(request, f"{updated} enquiries marked as contacted.")
    mark_as_contacted.short_description = "Mark as contacted"
    
    def mark_as_interested(self, request, queryset):
        """Mark selected enquiries as interested"""
        updated = queryset.update(follow_up_status='interested')
        self.message_user(request, f"{updated} enquiries marked as interested.")
    mark_as_interested.short_description = "Mark as interested"
    
    def mark_as_enrolled(self, request, queryset):
        """Mark selected enquiries as enrolled"""
        updated = queryset.update(follow_up_status='enrolled')
        self.message_user(request, f"{updated} enquiries marked as enrolled.")
    mark_as_enrolled.short_description = "Mark as enrolled"
    
    def assign_to_me(self, request, queryset):
        """Assign selected enquiries to current user"""
        if request.user.is_staff:
            updated = queryset.update(assigned_to=request.user)
            self.message_user(request, f"{updated} enquiries assigned to you.")
        else:
            self.message_user(request, "Only staff members can assign enquiries.", level='ERROR')
    assign_to_me.short_description = "Assign to me"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface for Contact model
    """
    list_display = ['full_name', 'email', 'subject', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['full_name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable adding contacts through admin (they should come from forms)"""
        return False
    
    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly except for staff notes if needed"""
        if obj:  # editing an existing object
            return ['full_name', 'email', 'subject', 'message', 'created_at', 'updated_at']
        return self.readonly_fields
