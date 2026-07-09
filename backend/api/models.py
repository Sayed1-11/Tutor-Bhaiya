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

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
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
    instructor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='courses_teaching',
        limit_choices_to={'role': 'teacher'}
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Discount in percentage (0-100)")
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


# ─── Course Contents ─────────────────────────────────────────────────────────

class Module(models.Model):
    """A module or section within a course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Video(models.Model):
    """A video lesson inside a module."""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_url = models.URLField(max_length=500)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Resource(models.Model):
    """Downloadable files or links for a course or module."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    url = models.URLField(max_length=500, blank=True)
    
    def __str__(self):
        return self.title


class Assignment(models.Model):
    """An assignment given by a teacher."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assignments', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    total_marks = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.title


class StudentAssignment(models.Model):
    """A student's submission for an assignment."""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_submitted')
    submission_text = models.TextField(blank=True)
    submission_file = models.FileField(upload_to='assignment_submissions/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.email} - {self.assignment.title}"


# ─── Accounting ──────────────────────────────────────────────────────────────

class Payment(models.Model):
    """Tracks payments made for courses."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.amount} for {self.course.title if self.course else 'Deleted Course'}"

