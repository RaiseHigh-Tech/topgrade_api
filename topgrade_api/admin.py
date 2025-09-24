from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, OTPVerification, PhoneOTPVerification,
    Category, Program, Syllabus, Topic, UserPurchase, UserBookmark,
    UserTopicProgress, UserCourseProgress
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
