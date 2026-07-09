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
            profile = UserProfileSerializer(user, context={'request': request})
            return Response({
                'message': 'Account created successfully!',
                'user': profile.data,
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

        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Django authenticates by username; we look up by email first
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'No account found with this email.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            return Response(
                {'error': 'Incorrect password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        login(request, user)
        profile = UserProfileSerializer(user, context={'request': request})
        return Response({
            'message': 'Logged in successfully!',
            'user': profile.data,
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
