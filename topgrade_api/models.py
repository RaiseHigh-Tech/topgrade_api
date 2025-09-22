from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
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
    job_openings = models.CharField(max_length=50)
    global_market_size = models.CharField(max_length=50)
    avg_annual_salary = models.CharField(max_length=50)
    is_best_seller = models.BooleanField(default=False)
    icon = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Program price")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount percentage (0-100)")

    def __str__(self):
        return self.title

class Syllabus(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='syllabuses')
    module_title = models.CharField(max_length=200)

    def __str__(self):
        return self.module_title

def get_topic_video_path(instance, filename):
    """Generate upload path for topic videos"""
    program_subtitle = instance.syllabus.program.subtitle.replace(' ', '_').replace('/', '_') if instance.syllabus.program.subtitle else instance.syllabus.program.title.replace(' ', '_').replace('/', '_')
    return f'program/{program_subtitle}/{filename}'

class Topic(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='topics')
    topic_title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to=get_topic_video_path, blank=True, null=True, help_text="Upload video file")
    description = models.TextField(blank=True, null=True)
    is_intro = models.BooleanField(default=False)

    def __str__(self):
        return self.topic_title

class AdvanceProgram(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='advance_program_images/', blank=True, null=True)
    batch_starts = models.CharField(max_length=50)
    available_slots = models.IntegerField()
    duration = models.CharField(max_length=50)
    program_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    job_openings = models.CharField(max_length=50)
    global_market_size = models.CharField(max_length=50)
    avg_annual_salary = models.CharField(max_length=50)
    is_best_seller = models.BooleanField(default=False)
    icon = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Advanced program price")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount percentage (0-100)")

    def __str__(self):
        return self.title

class AdvanceSyllabus(models.Model):
    advance_program = models.ForeignKey(AdvanceProgram, on_delete=models.CASCADE, related_name='syllabuses')
    module_title = models.CharField(max_length=200)

    def __str__(self):
        return self.module_title

def get_advance_topic_video_path(instance, filename):
    """Generate upload path for advance topic videos"""
    program_subtitle = instance.advance_syllabus.advance_program.subtitle.replace(' ', '_').replace('/', '_') if instance.advance_syllabus.advance_program.subtitle else instance.advance_syllabus.advance_program.title.replace(' ', '_').replace('/', '_')
    return f'advance_program/{program_subtitle}/{filename}'

class AdvanceTopic(models.Model):
    advance_syllabus = models.ForeignKey(AdvanceSyllabus, on_delete=models.CASCADE, related_name='topics')
    topic_title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to=get_advance_topic_video_path, blank=True, null=True, help_text="Upload video file")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.topic_title


class UserPurchase(models.Model):
    """
    Simple model to track user purchases - courses are automatically assigned
    """
    PURCHASE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PROGRAM_TYPE_CHOICES = [
        ('program', 'Program'),
        ('advanced_program', 'Advanced Program'),
    ]

    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    advanced_program = models.ForeignKey(AdvanceProgram, on_delete=models.CASCADE, null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PURCHASE_STATUS_CHOICES, default='pending')
    
    class Meta:
        ordering = ['-purchase_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'program'],
                condition=models.Q(program__isnull=False),
                name='unique_user_program'
            ),
            models.UniqueConstraint(
                fields=['user', 'advanced_program'],
                condition=models.Q(advanced_program__isnull=False),
                name='unique_user_advanced_program'
            )
        ]

    def __str__(self):
        if self.program_type == 'program' and self.program:
            return f"{self.user.email} - {self.program.title}"
        elif self.program_type == 'advanced_program' and self.advanced_program:
            return f"{self.user.email} - {self.advanced_program.title}"
        return f"{self.user.email} - Purchase #{self.id}"


class UserBookmark(models.Model):
    """
    Model to track user bookmarks for programs and advanced programs
    """
    PROGRAM_TYPE_CHOICES = [
        ('program', 'Program'),
        ('advanced_program', 'Advanced Program'),
    ]

    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    advanced_program = models.ForeignKey(AdvanceProgram, on_delete=models.CASCADE, null=True, blank=True)
    bookmarked_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-bookmarked_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'program'],
                condition=models.Q(program__isnull=False),
                name='unique_user_bookmark_program'
            ),
            models.UniqueConstraint(
                fields=['user', 'advanced_program'],
                condition=models.Q(advanced_program__isnull=False),
                name='unique_user_bookmark_advanced_program'
            )
        ]

    def __str__(self):
        if self.program_type == 'program' and self.program:
            return f"{self.user.email} - Bookmarked {self.program.title}"
        elif self.program_type == 'advanced_program' and self.advanced_program:
            return f"{self.user.email} - Bookmarked {self.advanced_program.title}"
        return f"{self.user.email} - Bookmark #{self.id}"


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
    # For regular programs
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_progress'
    )
    # For advanced programs
    advance_topic = models.ForeignKey(
        AdvanceTopic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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
                condition=models.Q(topic__isnull=False),
                name='unique_user_topic_progress'
            ),
            models.UniqueConstraint(
                fields=['user', 'advance_topic'],
                condition=models.Q(advance_topic__isnull=False),
                name='unique_user_advance_topic_progress'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['purchase', 'status']),
        ]

    def __str__(self):
        topic_name = self.topic.topic_title if self.topic else self.advance_topic.topic_title
        return f"{self.user.email} - {topic_name} ({self.status})"

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
        if self.purchase.program_type == 'program' and self.purchase.program:
            return self.purchase.program.title
        elif self.purchase.program_type == 'advanced_program' and self.purchase.advanced_program:
            return self.purchase.advanced_program.title
        return "Unknown Program"

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
