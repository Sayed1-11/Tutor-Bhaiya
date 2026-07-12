"""
TutorBhaiya — API Views
"""
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db.models import Exists, OuterRef

from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token

from .models import (
    Category, Course, Enrollment, ContactMessage,
    Module, Video, Resource, Assignment, StudentAssignment, Payment
)
from .permissions import IsAdmin, IsTeacher, IsStudent
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    CategorySerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    EnrollmentSerializer,
    ContactMessageSerializer,
    ModuleSerializer,
    VideoSerializer,
    ResourceSerializer,
    AssignmentSerializer,
    StudentAssignmentSerializer,
    PaymentSerializer,
    CoursePlayerSerializer,
)

User = get_user_model()


# ─── CSRF Token ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    """Return a CSRF token for the frontend to use in POST requests."""
    token = get_token(request)
    return Response({'csrfToken': token})


from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

# ─── Auth ─────────────────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    """POST /api/auth/register/ — Create a new user account."""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Auto-login after registration
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            profile = UserProfileSerializer(user, context={'request': request})
            return Response({
                'message': 'Account created successfully!',
                'user': profile.data,
                'token': token.key,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """POST /api/auth/login/ — Log in with email + password."""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        print("email and password", email, password)
        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Django authenticates by username; we look up by email first
        try:
            user_obj = User.objects.get(email=email)
            print("user_obj",user_obj)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'No account found with this email.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(request, email=user_obj.email, password=password)
        if user is None:
            return Response(
                {'error': 'Incorrect password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        profile = UserProfileSerializer(user, context={'request': request})
        return Response({
            'message': 'Login successful',
            'user': profile.data,
            'token': token.key,
        })


class LogoutView(APIView):
    """POST /api/auth/logout/ — Log out current user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully.'})


class MeView(APIView):
    """GET /api/auth/me/ — Get current logged-in user profile."""

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response({'authenticated': True, 'user': serializer.data})

    def patch(self, request):
        """Update profile fields."""
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            profile = UserProfileSerializer(request.user, context={'request': request})
            return Response(profile.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Categories ──────────────────────────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    """GET /api/categories/ — List all categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# ─── Courses ─────────────────────────────────────────────────────────────────

class CourseListView(generics.ListAPIView):
    """
    GET /api/courses/ — List courses.
    Query params:
      - ?category=<slug>  Filter by category slug
      - ?featured=true    Only featured courses
      - ?search=<term>    Search title/instructor
    """
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Course.objects.filter(is_active=True).select_related('category')
        
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_enrolled=Exists(
                    Enrollment.objects.filter(course=OuterRef('pk'), user=self.request.user)
                )
            )

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)

        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            qs = qs.filter(is_featured=True)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(instructor__icontains=search)

        return qs


class CourseDetailView(generics.RetrieveAPIView):
    """GET /api/courses/<slug>/ — Get a single course."""
    queryset = Course.objects.filter(is_active=True).select_related('category')
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_enrolled=Exists(
                    Enrollment.objects.filter(course=OuterRef('pk'), user=self.request.user)
                )
            )
        return qs

class CoursePlayerView(APIView):
    """GET /api/courses/<id>/player/ — Returns course data, modules, videos and user progress."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk, is_active=True)
            enrollment = Enrollment.objects.get(user=request.user, course=course)
        except (Course.DoesNotExist, Enrollment.DoesNotExist):
            return Response({'error': 'Not enrolled or course not found.'}, status=403)

        serializer = CoursePlayerSerializer(course, context={'request': request})
        completed_ids = list(enrollment.completed_videos.values_list('id', flat=True))

        return Response({
            'course': serializer.data,
            'progress': enrollment.progress,
            'completed_video_ids': completed_ids
        })

class MarkVideoCompleteView(APIView):
    """POST /api/enrollments/complete-video/ — Mark a video as completed and update progress."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        video_id = request.data.get('video_id')

        if not course_id or not video_id:
            return Response({'error': 'course_id and video_id are required'}, status=400)

        try:
            enrollment = Enrollment.objects.get(user=request.user, course_id=course_id)
            video = Video.objects.get(id=video_id)
        except (Enrollment.DoesNotExist, Video.DoesNotExist):
            return Response({'error': 'Enrollment or video not found'}, status=404)

        enrollment.completed_videos.add(video)
        
        # Calculate new progress
        total_videos = Video.objects.filter(module__course_id=course_id).count()
        completed = enrollment.completed_videos.count()
        
        if total_videos > 0:
            enrollment.progress = int((completed / total_videos) * 100)
            if enrollment.progress >= 100:
                enrollment.is_completed = True
            enrollment.save()
            
        return Response({
            'message': 'Video marked as complete',
            'progress': enrollment.progress,
            'completed_video_id': video.id
        })


# ─── Enrollments ──────────────────────────────────────────────────────────────

class EnrollmentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/enrollments/ — List user's enrolled courses.
    POST /api/enrollments/ — Enroll in a course { "course_id": <id> }
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course', 'course__category')

    def perform_create(self, serializer):
        serializer.save()


class EnrollmentDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/enrollments/<id>/ — Get single enrollment.
    PATCH /api/enrollments/<id>/ — Update progress.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)


class SubmitAssignmentView(APIView):
    """
    GET  /api/assignments/<id>/submit/ — Check if student already submitted.
    POST /api/assignments/<id>/submit/ — Submit assignment answer text.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            assignment = Assignment.objects.get(pk=pk)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=404)

        submission = StudentAssignment.objects.filter(
            assignment=assignment, student=request.user
        ).first()

        if submission:
            return Response({
                'submitted': True,
                'submission_text': submission.submission_text,
                'submission_file_url': request.build_absolute_uri(submission.submission_file.url) if submission.submission_file else None,
                'submitted_at': submission.submitted_at,
                'marks_obtained': submission.marks_obtained,
                'feedback': submission.feedback,
            })
        return Response({'submitted': False})

    def post(self, request, pk):
        try:
            assignment = Assignment.objects.get(pk=pk)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=404)

        submission_text = request.data.get('submission_text', '').strip()
        submission_file = request.FILES.get('submission_file')
        
        if not submission_text and not submission_file:
            return Response({'error': 'submission_text or submission_file is required'}, status=400)

        submission, created = StudentAssignment.objects.get_or_create(
            assignment=assignment,
            student=request.user,
            defaults={'submission_text': submission_text}
        )
        if not created:
            submission.submission_text = submission_text
        
        if submission_file:
            submission.submission_file = submission_file
        
        submission.save()

        return Response({
            'message': 'Assignment submitted successfully!',
            'submitted': True,
            'submitted_at': submission.submitted_at,
        }, status=201 if created else 200)

# ─── Dashboard ───────────────────────────────────────────────────────────────

class DashboardView(APIView):
    """GET /api/dashboard/ — Aggregated stats for the student dashboard."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        enrollments = Enrollment.objects.filter(
            user=user
        ).select_related('course', 'course__category')

        active_count = enrollments.filter(is_completed=False).count()
        completed_count = enrollments.filter(is_completed=True).count()

        # Average progress across all enrollments
        total = enrollments.count()
        avg_progress = 0
        if total > 0:
            avg_progress = round(
                sum(e.progress for e in enrollments) / total
            )

        # Most recent enrollment for "Continue Learning"
        recent_enrollment = enrollments.filter(is_completed=False).first()
        recent_data = None
        if recent_enrollment:
            recent_data = EnrollmentSerializer(
                recent_enrollment, context={'request': request}
            ).data

        profile = UserProfileSerializer(user, context={'request': request})

        return Response({
            'user': profile.data,
            'stats': {
                'active_courses': active_count,
                'completed_courses': completed_count,
                'total_enrollments': total,
                'average_progress': avg_progress,
            },
            'continue_learning': recent_data,
            'recent_enrollments': EnrollmentSerializer(
                enrollments[:5], many=True, context={'request': request}
            ).data,
        })


# ─── Contact ──────────────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class ContactView(APIView):
    """POST /api/contact/ — Submit a contact form message."""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Your message has been sent! We will get back to you shortly.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Teacher Dashboard & Endpoints ──────────────────────────────────────────

class TeacherCourseListView(generics.ListAPIView):
    """GET /api/teacher/courses/ — List courses taught by the teacher."""
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class TeacherStudentListView(APIView):
    """GET /api/teacher/students/ — View students enrolled in teacher's courses."""
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request):
        courses = Course.objects.filter(instructor=request.user)
        enrollments = Enrollment.objects.filter(course__in=courses).select_related('user', 'course')
        
        data = []
        for e in enrollments:
            data.append({
                'enrollment_id': e.id,
                'student_name': e.user.get_full_name(),
                'student_email': e.user.email,
                'course_title': e.course.title,
                'progress': e.progress,
                'enrolled_at': e.enrolled_at,
            })
        return Response(data)


# ─── Admin Endpoints ─────────────────────────────────────────────────────────

class AdminDashboardView(APIView):
    """GET /api/admin/dashboard/ — Financial & generic overview."""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        total_courses = Course.objects.count()
        total_students = User.objects.filter(role='student').count()
        total_teachers = User.objects.filter(role='teacher').count()
        
        from django.db.models import Sum
        total_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({
            'total_courses': total_courses,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_revenue': total_revenue,
        })
