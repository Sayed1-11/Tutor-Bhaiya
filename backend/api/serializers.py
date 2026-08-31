"""
TutorBhaiya — DRF Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Category, Course, Enrollment, ContactMessage,
    Module, Video, Resource, Assignment, StudentAssignment, Payment,
    CourseRoutine, Certificate, Book, JobPosting, JobApplication,
    Quiz, QuizQuestion, StudentQuiz, Notification
)

User = get_user_model()



# ─── Auth / User ─────────────────────────────────────────────────────────────

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Handles new user sign-up."""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    full_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password', 'phone')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Generate a username from email
        email = validated_data['email']
        username = email.split('@')[0]
        base = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            phone=validated_data.get('phone', ''),
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Public profile data for the logged-in user."""
    full_name = serializers.SerializerMethodField()
    avatar_initial = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'full_name', 'email', 'phone',
            'profile_picture', 'bio', 'date_joined',
            'avatar_initial', 'role',
        )
        read_only_fields = ('email', 'date_joined', 'role')

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_avatar_initial(self, obj):
        name = obj.get_full_name() or obj.username
        return name[0].upper() if name else 'U'


class UserUpdateSerializer(serializers.ModelSerializer):
    """Allow users to update their profile."""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'bio', 'profile_picture')


# ─── Category ────────────────────────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon', 'description', 'course_count')

    def get_course_count(self, obj):
        return obj.courses.filter(is_active=True).count()


# ─── Course Contents ─────────────────────────────────────────────────────────

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class ResourceSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = '__all__'

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return obj.url


class AssignmentSerializer(serializers.ModelSerializer):
    attachment_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = '__all__'

    def get_attachment_file_url(self, obj):
        if obj.attachment_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment_file.url)
            return obj.attachment_file.url
        return None


class ModuleSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    assignments = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = '__all__'

    def get_assignments(self, obj):
        qs = obj.assignments.all()
        return AssignmentSerializer(qs, many=True).data


# ─── Course ──────────────────────────────────────────────────────────────────

class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for course listing cards."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    enrollment_count = serializers.IntegerField(read_only=True)

    is_enrolled = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'instructor_name', 'price', 'discount_percentage',
            'duration_hours', 'thumbnail_url', 'badge_label', 'badge_color',
            'category_name', 'category_slug', 'is_featured', 'enrollment_count',
            'is_enrolled',
        )

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class CourseDetailSerializer(CourseListSerializer):
    """Full course detail including description, outline, roadmap, counts, modules, and resources."""
    modules = ModuleSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + (
            'description', 'created_at', 'outline', 'roadmap',
            'assignments_count', 'exams_count', 'quizzes_count', 'modules', 'resources'
        )


# ─── Enrollment ───────────────────────────────────────────────────────────────

class EnrollmentSerializer(serializers.ModelSerializer):
    """Enrollment with nested course info."""
    course = CourseListSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_active=True),
        source='course',
        write_only=True,
    )

    class Meta:
        model = Enrollment
        fields = (
            'id', 'course', 'course_id', 'enrolled_at',
            'progress', 'is_completed', 'last_accessed',
        )
        read_only_fields = ('enrolled_at', 'last_accessed')

    def create(self, validated_data):
        user = self.context['request'].user
        course = validated_data['course']
        enrollment, created = Enrollment.objects.get_or_create(
            user=user, course=course
        )
        if created:
            import uuid
            Payment.objects.create(
                user=user,
                course=course,
                amount=course.price if course else 0.00,
                payment_method='bkash',
                transaction_id=f"BKX{uuid.uuid4().hex[:8].upper()}",
                status='completed'
            )
        return enrollment


# ─── Contact Message ─────────────────────────────────────────────────────────

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('id', 'name', 'email', 'phone', 'subject', 'message', 'submitted_at')
        read_only_fields = ('submitted_at',)


class StudentAssignmentSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    assignment_description = serializers.CharField(source='assignment.description', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    course_title = serializers.CharField(source='assignment.course.title', read_only=True)
    total_marks = serializers.IntegerField(source='assignment.total_marks', read_only=True)
    submission_file_url = serializers.SerializerMethodField()

    class Meta:
        model = StudentAssignment
        fields = '__all__'
        read_only_fields = ('submitted_at',)

    def get_submission_file_url(self, obj):
        if obj.submission_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.submission_file.url)
            return obj.submission_file.url
        return None


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True, default='')

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at',)


# ─── Quizzes ──────────────────────────────────────────────────────────────────

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = '__all__'


class QuizQuestionStudentSerializer(serializers.ModelSerializer):
    """Omits correct_option for student quiz attempts."""
    class Meta:
        model = QuizQuestion
        fields = ('id', 'quiz', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'marks')


class QuizSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    total_marks = serializers.IntegerField(read_only=True)
    is_submitted = serializers.BooleanField(read_only=True, default=False)
    student_score = serializers.IntegerField(read_only=True, default=None)
    student_passed = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Quiz
        fields = '__all__'


class QuizDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    questions = QuizQuestionSerializer(many=True, read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    total_marks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'


class StudentQuizSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    course_title = serializers.CharField(source='quiz.course.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)

    class Meta:
        model = StudentQuiz
        fields = '__all__'


# ─── Accounting ──────────────────────────────────────────────────────────────

class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_at', 'status')


class CourseRoutineSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = CourseRoutine
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    instructor_name = serializers.CharField(source='course.instructor.get_full_name', read_only=True)

    class Meta:
        model = Certificate
        fields = (
            'id', 'certificate_number', 'student_name', 'course_title',
            'instructor_name', 'issued_at'
        )


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class JobPostingSerializer(serializers.ModelSerializer):
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = '__all__'

    def get_applications_count(self, obj):
        return obj.applications.count()


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job_posting.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ('applied_at',)


class CoursePlayerSerializer(CourseDetailSerializer):
    """Full course details including all nested modules, videos, and routines."""
    modules = ModuleSerializer(many=True, read_only=True)
    routines = CourseRoutineSerializer(many=True, read_only=True)

    class Meta(CourseDetailSerializer.Meta):
        fields = CourseDetailSerializer.Meta.fields + ('modules', 'routines')

