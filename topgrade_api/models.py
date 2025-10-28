from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings
import datetime

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        username = email.split('@')[0]  # Auto-generate username from email
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Set role to admin for superusers

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_ROLES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
        ('operations_staff', 'Operations Staff'),
    ]
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    fullname = models.CharField(max_length=255, blank=True, null=True)
    area_of_intrest = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def save(self, *args, **kwargs):
        if self.email and not self.username:
            # Extract username from email (part before @)
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email

class OTPVerification(models.Model):
    email = models.EmailField()
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['email']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP verification expires after 10 minutes
            self.expires_at = timezone.now() + datetime.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.email} - Verified: {self.is_verified}"

class PhoneOTPVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['phone_number']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP verification expires after 10 minutes
            self.expires_at = timezone.now() + datetime.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Phone OTP for {self.phone_number} - Verified: {self.is_verified}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
    
    @classmethod
    def create_default_categories(cls):
        """Create default categories if they don't exist"""
        defaults = [
            {
                'name': 'Advanced Program',
                'description': 'Advanced level programs for professional development and career growth',
                'icon': 'fas fa-graduation-cap'
            }
        ]
        
        created_categories = []
        for category_data in defaults:
            category, created = cls.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon']
                }
            )
            if created:
                created_categories.append(category.name)
        
        return created_categories

class Program(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='programs')
    image = models.ImageField(upload_to='program_images/', blank=True, null=True)
    batch_starts = models.CharField(max_length=50)
    available_slots = models.IntegerField()
    duration = models.CharField(max_length=50)
    program_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    job_openings = models.CharField(max_length=50, blank=True, null=True)
    global_market_size = models.CharField(max_length=50, blank=True, null=True)
    avg_annual_salary = models.CharField(max_length=50, blank=True, null=True)
    is_best_seller = models.BooleanField(default=False)
    icon = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Program price")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount percentage (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.subtitle:
            return f"{self.title} - {self.subtitle}"
        return self.title
    
    @property
    def is_advanced(self):
        """Check if this is an advanced program based on category"""
        return self.category and self.category.name == 'Advanced Program'
    
    @property 
    def discounted_price(self):
        """Calculate discounted price"""
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price
    
    @classmethod
    def get_regular_programs(cls):
        """Get all regular programs (not Advanced Program category)"""
        return cls.objects.exclude(category__name='Advanced Program')
    
    @classmethod
    def get_advanced_programs(cls):
        """Get all advanced programs (Advanced Program category)"""
        return cls.objects.filter(category__name='Advanced Program')

class Syllabus(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='syllabuses')
    module_title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Syllabuses"

    def __str__(self):
        return f"{self.program.title} - {self.module_title}"

def get_topic_video_path(instance, filename):
    """Generate upload path for topic videos"""
    program_type = "advanced" if instance.syllabus.program.is_advanced else "regular"
    program_name = instance.syllabus.program.subtitle.replace(' ', '_').replace('/', '_')
    return f'programs/{program_type}/{program_name}/{filename}'

class Topic(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='topics')
    topic_title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to=get_topic_video_path, blank=True, null=True, help_text="Upload video file")
    video_duration = models.CharField(max_length=10, blank=True, null=True, help_text="Video duration in MM:SS or HH:MM:SS format")
    is_intro = models.BooleanField(default=False, help_text="Mark as intro video")
    is_free_trial = models.BooleanField(default=False, help_text="Available in free trial")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.syllabus.program.title} - {self.topic_title}"

class UserPurchase(models.Model):
    """
    Simple model to track user purchases - courses are automatically assigned
    """
    PURCHASE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PURCHASE_STATUS_CHOICES, default='pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount actually paid after discounts")
    
    class Meta:
        ordering = ['-purchase_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'program'],
                name='unique_user_program_purchase'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.program.title}"

class UserBookmark(models.Model):
    """
    Model to track user bookmarks for programs
    """
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='bookmarks')
    bookmarked_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-bookmarked_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'program'],
                name='unique_user_bookmark_program'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - Bookmarked {self.program.title}"

class UserTopicProgress(models.Model):
    """
    Track user progress for individual topics/videos
    """
    PROGRESS_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='topic_progress'
    )
    purchase = models.ForeignKey(
        UserPurchase,
        on_delete=models.CASCADE,
        related_name='topic_progress'
    )
    # Unified topic reference
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    # Progress tracking
    status = models.CharField(
        max_length=15,
        choices=PROGRESS_STATUS_CHOICES,
        default='not_started'
    )
    watch_time_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Time watched in seconds"
    )
    total_duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Total video duration in seconds"
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of topic completed (0-100)"
    )
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_watched_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'topic'],
                name='unique_user_topic_progress'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['purchase', 'status']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.topic.topic_title} ({self.status})"

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def watch_percentage(self):
        if self.total_duration_seconds == 0:
            return 0
        return min(100, (self.watch_time_seconds / self.total_duration_seconds) * 100)

    def update_progress(self, watch_time_seconds, total_duration_seconds=None):
        """Update progress based on watch time"""
        self.watch_time_seconds = watch_time_seconds
        
        if total_duration_seconds:
            self.total_duration_seconds = total_duration_seconds
        
        # Calculate completion percentage
        if self.total_duration_seconds > 0:
            self.completion_percentage = min(100, (watch_time_seconds / self.total_duration_seconds) * 100)
        
        # Update status based on progress
        if self.completion_percentage >= 90:  # Consider 90% as completed
            self.status = 'completed'
            if not self.completed_at:
                self.completed_at = timezone.now()
        elif self.completion_percentage > 0:
            self.status = 'in_progress'
            if not self.started_at:
                self.started_at = timezone.now()
        
        self.save()

class UserCourseProgress(models.Model):
    """
    Overall course progress summary for a user's purchase
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='course_progress'
    )
    purchase = models.ForeignKey(
        UserPurchase,
        on_delete=models.CASCADE,
        related_name='course_progress',
        unique=True
    )
    
    # Overall progress
    total_topics = models.PositiveIntegerField(default=0)
    completed_topics = models.PositiveIntegerField(default=0)
    in_progress_topics = models.PositiveIntegerField(default=0)
    
    # Time tracking
    total_watch_time_seconds = models.PositiveIntegerField(default=0)
    total_course_duration_seconds = models.PositiveIntegerField(default=0)
    
    # Progress percentage
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    # Status
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_activity_at']

    def __str__(self):
        program_title = self.get_program_title()
        return f"{self.user.email} - {program_title} ({self.completion_percentage}%)"

    def get_program_title(self):
        """Get the title of the purchased program"""
        return self.purchase.program.title if self.purchase.program else "Unknown Program"

    def update_progress(self):
        """Recalculate progress based on topic progress"""
        # Get all topic progress for this course
        topic_progress = UserTopicProgress.objects.filter(
            user=self.user,
            purchase=self.purchase
        )
        
        self.total_topics = topic_progress.count()
        self.completed_topics = topic_progress.filter(status='completed').count()
        self.in_progress_topics = topic_progress.filter(status='in_progress').count()
        
        # Calculate overall completion percentage
        if self.total_topics > 0:
            self.completion_percentage = (self.completed_topics / self.total_topics) * 100
        
        # Update completion status
        if self.completion_percentage >= 100:
            self.is_completed = True
            if not self.completed_at:
                self.completed_at = timezone.now()
        
        # Update start time if any progress exists
        if self.completion_percentage > 0 and not self.started_at:
            self.started_at = timezone.now()
        
        # Calculate total watch time
        self.total_watch_time_seconds = sum(
            progress.watch_time_seconds for progress in topic_progress
        )
        
        self.save()

class Carousel(models.Model):
    image = models.ImageField(upload_to='carousel_images/', help_text="Carousel image")
    is_active = models.BooleanField(default=True, help_text="Whether this slide is active in the carousel")
    order = models.PositiveIntegerField(default=0, help_text="Order of the slide in carousel (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Carousel Slide"
        verbose_name_plural = "Carousel Slides"

    def __str__(self):
        return f"Carousel Slide {self.id}"

class Testimonial(models.Model):
    """Model to store student testimonials for the website"""
    name = models.CharField(max_length=100, help_text="Student's full name")
    field_of_study = models.CharField(max_length=100, help_text="e.g., Psychology, Data Science, Web Development")
    title = models.CharField(max_length=200, help_text="Testimonial heading/title")
    content = models.TextField(help_text="Testimonial description/content")
    avatar_image = models.ImageField(
        upload_to='testimonials/avatars/', 
        blank=True, 
        null=True, 
        help_text="Upload avatar image (optional - will use default if not provided)"
    )
    is_active = models.BooleanField(default=True, help_text="Whether to display this testimonial on the website")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
    
    def __str__(self):
        return f"{self.name} - {self.field_of_study}"

class Certificate(models.Model):
    """Model to store program certificate images"""
    program = models.ForeignKey(
        Program, 
        on_delete=models.CASCADE, 
        related_name='certificates',
        help_text="Program associated with this certificate"
    )
    certificate_image = models.ImageField(
        upload_to='certificates/',
        help_text="Upload certificate image"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
    
    def __str__(self):
        return f"{self.program.title} - Certificate"

class ProgramEnquiry(models.Model):
    """Model to store program enquiry/application form data"""
    
    # Follow-up status choices
    FOLLOW_UP_STATUS_CHOICES = [
        ('new', 'New Enquiry'),
        ('contacted', 'Initial Contact Made'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('enrolled', 'Enrolled'),
        ('follow_up_needed', 'Follow-up Needed'),
        ('closed', 'Closed'),
    ]
    
    # Program enquired about
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='enquiries',
        help_text="Program the user enquired about"
    )
    
    # User information from form
    first_name = models.CharField(
        max_length=100,
        help_text="User's first name"
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="User's phone number"
    )
    email = models.EmailField(
        help_text="User's email address"
    )
    college_name = models.CharField(
        max_length=200,
        help_text="User's college/institution name"
    )
    
    # Follow-up tracking
    follow_up_status = models.CharField(
        max_length=20,
        choices=FOLLOW_UP_STATUS_CHOICES,
        default='new',
        help_text="Current follow-up status"
    )
    
    # Internal notes for follow-up
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for follow-up and tracking"
    )
    
    # Assigned to staff member for follow-up
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_enquiries',
        help_text="Staff member assigned to follow up"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this enquiry was contacted"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Program Enquiry'
        verbose_name_plural = 'Program Enquiries'
        indexes = [
            models.Index(fields=['follow_up_status', 'created_at']),
            models.Index(fields=['program', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} - {self.program.title} ({self.get_follow_up_status_display()})"
    
    @property
    def full_name(self):
        """Get user's full name"""
        return self.first_name
    
    @property
    def days_since_enquiry(self):
        """Calculate days since enquiry was made"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days
    
    @property
    def needs_follow_up(self):
        """Check if enquiry needs follow-up based on status and time"""
        if self.follow_up_status in ['enrolled', 'closed', 'not_interested']:
            return False
        
        if self.follow_up_status == 'new' and self.days_since_enquiry > 1:
            return True
            
        if self.follow_up_status == 'contacted' and self.days_since_enquiry > 3:
            return True
            
        if self.follow_up_status == 'follow_up_needed':
            return True
            
        return False


class Contact(models.Model):
    """
    Model to store contact form submissions from users
    """
    full_name = models.CharField(max_length=255, help_text="Full name of the person contacting")
    email = models.EmailField(help_text="Email address for response")
    subject = models.CharField(max_length=500, help_text="Subject of the inquiry")
    message = models.TextField(help_text="Detailed message or inquiry")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the contact was submitted")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the contact was last updated")

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ['-created_at']  # Show newest contacts first

    def __str__(self):
        return f"{self.full_name} - {self.subject[:50]}..."
