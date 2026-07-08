"""
TutorBhaiya — Database Models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


# ─── User ────────────────────────────────────────────────────────────────────

class User(AbstractUser):
    """Extended user model with extra profile fields."""
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True
    )
    bio = models.TextField(blank=True)

    # Use email as the unique identifier
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def full_name(self):
        return self.get_full_name() or self.username


# ─── Category ────────────────────────────────────────────────────────────────

class Category(models.Model):
    """Course category (e.g. SSC Batch, O Level, Skills)."""
    ICON_CHOICES = [
        ('ph-books', 'Books'),
        ('ph-exam', 'Exam'),
        ('ph-graduation-cap', 'Graduation Cap'),
        ('ph-student', 'Student'),
        ('ph-certificate', 'Certificate'),
        ('ph-code', 'Code'),
        ('ph-globe', 'Globe'),
        ('ph-rocket', 'Rocket'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='ph-books')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ─── Course ──────────────────────────────────────────────────────────────────

class Course(models.Model):
    """A course offered on TutorBhaiya."""

    BADGE_COLOR_CHOICES = [
        ('bg-primary', 'Purple'),
        ('bg-accent1', 'Amber'),
        ('bg-accent2', 'Sky Blue'),
        ('bg-secondary', 'Emerald'),
        ('bg-violet-600', 'Violet'),
        ('bg-emerald-600', 'Dark Emerald'),
        ('bg-amber-500', 'Orange'),
        ('bg-pink-500', 'Pink'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='courses'
    )
    instructor = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    badge_label = models.CharField(max_length=50, blank=True, help_text="e.g. SSC BATCH")
    badge_color = models.CharField(max_length=30, choices=BADGE_COLOR_CHOICES, default='bg-primary')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    outline = models.JSONField(default=list, blank=True, help_text="List of outline topics")
    roadmap = models.JSONField(default=list, blank=True, help_text="List of roadmap milestones")
    assignments_count = models.PositiveIntegerField(default=0)
    exams_count = models.PositiveIntegerField(default=0)
    quizzes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def enrollment_count(self):
        return self.enrollments.count()


# ─── Enrollment ───────────────────────────────────────────────────────────────

class Enrollment(models.Model):
    """Tracks a user's enrollment in a course."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(
        default=0, help_text="Progress percentage (0–100)"
    )
    is_completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ('user', 'course')
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"


# ─── ContactMessage ──────────────────────────────────────────────────────────

class ContactMessage(models.Model):
    """Message submitted via the contact form."""
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"From {self.name} ({self.email}) — {self.submitted_at.strftime('%Y-%m-%d')}"
