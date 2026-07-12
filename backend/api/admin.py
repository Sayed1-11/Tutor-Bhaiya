"""
TutorBhaiya — Django Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Category, Course, Enrollment, ContactMessage

admin.site.site_header = "TutorBhaiya Admin"
admin.site.site_title = "TutorBhaiya"
admin.site.index_title = "Platform Management"


# ─── User ────────────────────────────────────────────────────────────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'get_full_name', 'phone', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('phone', 'bio', 'profile_picture')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('email', 'first_name', 'last_name', 'phone')}),
    )


# ─── Category ────────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order', 'course_count')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def course_count(self, obj):
        return obj.courses.filter(is_active=True).count()
    course_count.short_description = 'Active Courses'


# ─── Course ──────────────────────────────────────────────────────────────────

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'instructor', 'price',
        'duration_hours', 'is_featured', 'is_active', 'enrollment_count', 'created_at'
    )
    list_filter = ('is_active', 'is_featured', 'category')
    search_fields = ('title', 'instructor', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_active')
    ordering = ('-created_at',)

    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Enrollments'

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="80" style="border-radius:8px">', obj.thumbnail.url)
        return '—'
    thumbnail_preview.short_description = 'Thumbnail'


# ─── Enrollment ───────────────────────────────────────────────────────────────

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_bar', 'is_completed', 'enrolled_at')
    list_filter = ('is_completed', 'course__category')
    search_fields = ('user__email', 'course__title')
    ordering = ('-enrolled_at',)
    readonly_fields = ('enrolled_at', 'last_accessed')

    def progress_bar(self, obj):
        color = '#10B981' if obj.progress >= 80 else '#8B5CF6' if obj.progress >= 40 else '#F59E0B'
        return format_html(
            '<div style="width:100px;background:#eee;border-radius:4px">'
            '<div style="width:{0}%;background:{1};height:10px;border-radius:4px"></div>'
            '</div> {0}%',
            obj.progress, color
        )
    progress_bar.short_description = 'Progress'


# ─── ContactMessage ──────────────────────────────────────────────────────────

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'submitted_at', 'is_read')
    list_filter = ('is_read', 'submitted_at')
    search_fields = ('name', 'email', 'message')
    ordering = ('-submitted_at',)
    list_editable = ('is_read',)
    readonly_fields = ('submitted_at',)

# ─── Course Contents ─────────────────────────────────────────────────────────

from .models import Module, Video, Resource, Assignment, StudentAssignment, Payment

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'duration_minutes', 'order')
    list_filter = ('module__course', 'module')
    search_fields = ('title', 'module__title')
    ordering = ('module', 'order')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'module')
    list_filter = ('course', 'module')
    search_fields = ('title', 'course__title', 'module__title')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'module', 'due_date', 'total_marks')
    list_filter = ('course', 'module')
    search_fields = ('title', 'course__title')

@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'marks_obtained')
    list_filter = ('assignment__course', 'assignment')
    search_fields = ('student__email', 'assignment__title')

# ─── Accounting ──────────────────────────────────────────────────────────────

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'course__title', 'transaction_id')
    ordering = ('-created_at',)
