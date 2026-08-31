"""
TutorBhaiya — API Views
"""
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db.models import Exists, OuterRef, Q

from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token

from .models import (
    Category, Course, Enrollment, ContactMessage,
    Module, Video, Resource, Assignment, StudentAssignment, Payment,
    CourseRoutine, Certificate, Book, JobPosting, JobApplication,
    Quiz, QuizQuestion, StudentQuiz, Notification
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
    CourseRoutineSerializer,
    CertificateSerializer,
    BookSerializer,
    JobPostingSerializer,
    JobApplicationSerializer,
    QuizSerializer,
    QuizDetailSerializer,
    QuizQuestionSerializer,
    QuizQuestionStudentSerializer,
    StudentQuizSerializer,
    NotificationSerializer,
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
        """Update profile fields. If old_password + new_password are sent, change password."""
        user = request.user

        # ── Password change ───────────────────────────────────────────────────
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if old_password or new_password:
            if not old_password or not new_password:
                return Response(
                    {'error': 'Both old_password and new_password are required to change your password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not user.check_password(old_password):
                return Response(
                    {'error': 'Your current password is incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if len(new_password) < 8:
                return Response(
                    {'error': 'New password must be at least 8 characters long.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(new_password)
            user.save()
            # Re-issue token so the user stays logged in after password change
            from rest_framework.authtoken.models import Token
            Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            profile = UserProfileSerializer(user, context={'request': request})
            return Response({
                'message': 'Password changed successfully!',
                'user': profile.data,
                'token': token.key,
            })

        # ── Profile fields update ─────────────────────────────────────────────
        serializer = UserUpdateSerializer(
            user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            profile = UserProfileSerializer(user, context={'request': request})
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
        except Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=404)

        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if not enrollment and request.user.role not in ['teacher', 'admin'] and course.instructor != request.user:
            return Response({'error': 'Not enrolled in this course.'}, status=403)

        serializer = CoursePlayerSerializer(course, context={'request': request})
        completed_ids = list(enrollment.completed_videos.values_list('id', flat=True)) if enrollment else []
        progress = enrollment.progress if enrollment else 100

        return Response({
            'course': serializer.data,
            'progress': progress,
            'completed_video_ids': completed_ids
        })

def check_and_issue_certificate(user, course):
    """
    Evaluates whether the student has met all conditions to earn a certificate:
    1. Video completion progress is 100%.
    2. All assignments in the course are submitted AND approved by the teacher.
    3. All quizzes in the course are passed.
    """
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if not enrollment:
        return None, {'eligible': False, 'reason': 'User is not enrolled in this course.'}

    # 1. Check video lessons completion
    total_videos = Video.objects.filter(module__course=course).count()
    completed_videos = enrollment.completed_videos.count()
    if total_videos > 0 and completed_videos < total_videos:
        return None, {
            'eligible': False,
            'reason': f"Incomplete video lessons ({completed_videos}/{total_videos} watched)."
        }

    # 2. Check assignments (only those that belong to a module)
    course_assignments = Assignment.objects.filter(course=course, module__isnull=False)
    pending_list = []
    for assign in course_assignments:
        sub = StudentAssignment.objects.filter(assignment=assign, student=user).first()
        if not sub:
            pending_list.append(f"'{assign.title}' not submitted")
        elif sub.status != 'approved':
            status_disp = sub.get_status_display()
            pending_list.append(f"'{assign.title}' status is '{status_disp}'")

    if pending_list:
        return None, {
            'eligible': False,
            'reason': f"Assignments pending teacher approval: {'; '.join(pending_list)}"
        }

    # 3. Check quizzes (only those that belong to a module)
    course_quizzes = Quiz.objects.filter(course=course, module__isnull=False)
    unpassed_list = []
    for q in course_quizzes:
        qsub = StudentQuiz.objects.filter(quiz=q, student=user).first()
        if not qsub:
            unpassed_list.append(f"Quiz '{q.title}' not submitted")
        elif not qsub.passed:
            unpassed_list.append(f"Quiz '{q.title}' failed ({qsub.score}/{qsub.total_marks})")

    if unpassed_list:
        return None, {
            'eligible': False,
            'reason': f"Quizzes not passed: {'; '.join(unpassed_list)}"
        }

    # All criteria met! Mark completed and issue certificate.
    enrollment.is_completed = True
    enrollment.save()

    cert = Certificate.objects.filter(enrollment=enrollment).first()
    if not cert:
        import uuid
        cert_num = f"TB-{course.id:03d}-{uuid.uuid4().hex[:6].upper()}"
        cert = Certificate.objects.create(
            enrollment=enrollment,
            user=user,
            course=course,
            certificate_number=cert_num
        )

    return cert, {'eligible': True, 'reason': 'Certificate issued successfully!'}


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
            enrollment.save()
            
        cert, status_info = check_and_issue_certificate(request.user, enrollment.course)
            
        return Response({
            'message': 'Video marked as complete',
            'progress': enrollment.progress,
            'completed_video_id': video.id,
            'is_completed': enrollment.is_completed,
            'certificate_number': cert.certificate_number if cert else None,
            'certificate_eligible': status_info['eligible'],
            'certificate_reason': status_info['reason'],
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
    POST /api/assignments/<id>/submit/ — Submit assignment answer text/file.
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
                'status': submission.status,
                'status_display': submission.get_status_display(),
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
            defaults={'submission_text': submission_text, 'status': 'pending'}
        )
        if not created:
            submission.submission_text = submission_text
            submission.status = 'pending'  # Resubmission resets to pending review
        
        if submission_file:
            submission.submission_file = submission_file
        
        submission.save()

        # Notify teacher(s) of new submission
        recipients = []
        if assignment.course.instructor:
            recipients.append(assignment.course.instructor)
        else:
            recipients = list(User.objects.filter(role='teacher'))

        file_url = request.build_absolute_uri(submission.submission_file.url) if submission.submission_file else ''
        for t in recipients:
            if t:
                Notification.objects.create(
                    user=t,
                    sender=request.user,
                    title=f"New Assignment Submission: {assignment.title}",
                    message=f"Student {request.user.get_full_name()} submitted assignment '{assignment.title}' for '{assignment.course.title}'.",
                    notification_type='assignment_submitted',
                    resource_url=file_url
                )

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
        user = self.request.user
        if user.role == 'admin':
            return Course.objects.all()
        return Course.objects.filter(Q(instructor=user) | Q(instructor__isnull=True))


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

        from django.db.models import Sum, Count
        total_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        total_enrollments = Enrollment.objects.count()

        # Recent 10 payments for transaction feed
        recent_payments = []
        for p in Payment.objects.select_related('user', 'course').order_by('-created_at')[:10]:
            recent_payments.append({
                'student_name': p.user.get_full_name() or p.user.email,
                'student_email': p.user.email,
                'course_title': p.course.title if p.course else 'Deleted Course',
                'amount': str(p.amount),
                'payment_method': p.payment_method,
                'transaction_id': p.transaction_id,
                'status': p.status,
                'date': p.created_at.strftime('%b %d, %Y'),
            })

        # Top courses by revenue
        top_courses = []
        courses_revenue = (
            Payment.objects
            .filter(course__isnull=False)
            .values('course__id', 'course__title')
            .annotate(revenue=Sum('amount'), enrollments=Count('id'))
            .order_by('-revenue')[:5]
        )
        for c in courses_revenue:
            top_courses.append({
                'course_id': c['course__id'],
                'course_title': c['course__title'],
                'revenue': str(c['revenue']),
                'enrollments': c['enrollments'],
            })

        return Response({
            'stats': {
                'total_courses': total_courses,
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_revenue': total_revenue,
                'total_enrollments': total_enrollments,
            },
            'recent_payments': recent_payments,
            'top_courses': top_courses,
        })


# ─── Certificates ────────────────────────────────────────────────────────────

class CertificateListView(generics.ListAPIView):
    """GET /api/certificates/ — List certificates earned by current user."""
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user).select_related('user', 'course', 'course__instructor')


class CertificateDetailView(APIView):
    """GET /api/certificates/<cert_number>/ — Retrieve certificate details."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, certificate_number):
        try:
            cert = Certificate.objects.select_related('user', 'course', 'course__instructor').get(certificate_number=certificate_number)
        except Certificate.DoesNotExist:
            return Response({'error': 'Certificate not found.'}, status=404)

        serializer = CertificateSerializer(cert)
        return Response(serializer.data)


# ─── Books ───────────────────────────────────────────────────────────────────

class BookListView(generics.ListAPIView):
    """
    GET /api/books/ — List sample textbooks & guides.
    Query params: ?category=<slug>&search=<query>
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Book.objects.select_related('category')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(author__icontains=search)
        return qs


# ─── Careers ─────────────────────────────────────────────────────────────────

class JobPostingListView(generics.ListAPIView):
    """GET /api/careers/ — List active job postings."""
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.AllowAny]
    queryset = JobPosting.objects.filter(is_active=True)


@method_decorator(csrf_exempt, name='dispatch')
class JobApplicationCreateView(APIView):
    """POST /api/careers/<id>/apply/ — Submit application for a job posting."""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            job = JobPosting.objects.get(pk=pk, is_active=True)
        except JobPosting.DoesNotExist:
            return Response({'error': 'Job posting not found or no longer active.'}, status=404)

        data = request.data.copy()
        data['job_posting'] = job.id

        serializer = JobApplicationSerializer(data=data)
        if serializer.is_valid():
            serializer.save(job_posting=job)
            return Response({'message': 'Your job application has been submitted successfully!'}, status=201)
        return Response(serializer.errors, status=400)


# ─── Teacher Work & Dashboard Endpoints ─────────────────────────────────────

class TeacherDashboardView(APIView):
    """GET /api/teacher/dashboard/ — Teacher overview metrics & pending grading tasks."""
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request):
        teacher = request.user
        courses = Course.objects.filter(Q(instructor=teacher) | Q(instructor__isnull=True)) if teacher.role == 'teacher' else Course.objects.all()
        total_courses = courses.count()
        total_students = Enrollment.objects.filter(course__in=courses).values('user').distinct().count()
        
        pending_assignments = StudentAssignment.objects.filter(
            assignment__course__in=courses, status='pending'
        ).count()
        
        total_quizzes = Quiz.objects.filter(course__in=courses).count()
        total_resources = Resource.objects.filter(course__in=courses).count()

        return Response({
            'stats': {
                'total_courses': total_courses,
                'total_students': total_students,
                'pending_grading': pending_assignments,
                'total_quizzes': total_quizzes,
                'total_resources': total_resources,
            }
        })


class TeacherAssignmentGradingView(APIView):
    """
    GET  /api/teacher/assignments/submissions/ — List submissions for teacher's courses.
    POST /api/teacher/assignments/grade/ — Grade & approve/reject a student submission.
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request):
        courses = Course.objects.filter(Q(instructor=request.user) | Q(instructor__isnull=True)) if request.user.role == 'teacher' else Course.objects.all()
        submissions = StudentAssignment.objects.filter(
            assignment__course__in=courses
        ).select_related('assignment', 'assignment__course', 'student').order_by('-submitted_at')
        
        status_filter = request.query_params.get('status')
        if status_filter:
            submissions = submissions.filter(status=status_filter)
            
        serializer = StudentAssignmentSerializer(submissions, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        submission_id = request.data.get('submission_id')
        marks = request.data.get('marks_obtained')
        feedback = request.data.get('feedback', '')
        status_val = request.data.get('status', 'approved')

        if not submission_id or marks is None:
            return Response({'error': 'submission_id and marks_obtained are required.'}, status=400)

        try:
            sub = StudentAssignment.objects.get(pk=submission_id)
        except StudentAssignment.DoesNotExist:
            return Response({'error': 'Submission not found.'}, status=404)

        sub.marks_obtained = int(marks)
        sub.feedback = feedback
        sub.status = status_val
        sub.is_passed = (status_val == 'approved')
        sub.save()

        # Re-evaluate certificate eligibility for this student!
        check_and_issue_certificate(sub.student, sub.assignment.course)

        # Notify student!
        res_file_url = request.build_absolute_uri(sub.submission_file.url) if sub.submission_file else ''
        Notification.objects.create(
            user=sub.student,
            sender=request.user,
            title=f"Assignment Evaluated: {sub.assignment.title}",
            message=f"Your submission for '{sub.assignment.title}' in '{sub.assignment.course.title}' has been evaluated. Status: {status_val.upper()}. Marks: {sub.marks_obtained}/{sub.assignment.total_marks}. Feedback: {feedback or 'No feedback provided.'}",
            notification_type='assignment_graded',
            resource_url=res_file_url
        )

        return Response({
            'message': f"Submission successfully {status_val}!",
            'submission': StudentAssignmentSerializer(sub, context={'request': request}).data
        })


class TeacherContentManageView(APIView):
    """
    POST /api/teacher/content/<target_type>/ — Add module, video, resource, or assignment.
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def post(self, request, target_type):
        data = request.data
        if target_type == 'module':
            serializer = ModuleSerializer(data=data, context={'request': request})
        elif target_type == 'video':
            serializer = VideoSerializer(data=data, context={'request': request})
        elif target_type == 'resource':
            serializer = ResourceSerializer(data=data, context={'request': request})
        elif target_type == 'assignment':
            serializer = AssignmentSerializer(data=data, context={'request': request})
        else:
            return Response({'error': 'Invalid content type.'}, status=400)

        if serializer.is_valid():
            instance = serializer.save()

            # Find target course to set instructor if null and notify enrolled students
            course = None
            if hasattr(instance, 'course') and instance.course:
                course = instance.course
            elif hasattr(instance, 'module') and instance.module and instance.module.course:
                course = instance.module.course

            if course:
                if not course.instructor:
                    course.instructor = request.user
                    course.save()

                # Notify enrolled students
                enrolled_students = User.objects.filter(enrollments__course=course).distinct()
                res_url = ''
                if target_type == 'video' and hasattr(instance, 'video_url'):
                    res_url = instance.video_url
                elif target_type == 'resource':
                    res_url = instance.url or (request.build_absolute_uri(instance.file.url) if instance.file else '')

                title_text = f"New {target_type.capitalize()} Added: {getattr(instance, 'title', 'Content')}"
                msg_text = f"New {target_type} '{getattr(instance, 'title', '')}' was added to course '{course.title}'."

                for student in enrolled_students:
                    Notification.objects.create(
                        user=student,
                        sender=request.user,
                        title=title_text,
                        message=msg_text,
                        notification_type='content_added',
                        resource_url=res_url
                    )

            return Response({'message': f"{target_type.capitalize()} created successfully!", 'data': serializer.data}, status=201)
        return Response(serializer.errors, status=400)


class TeacherContentItemManageView(APIView):
    """
    GET/PATCH/DELETE /api/teacher/content/<target_type>/<pk>/ — Update or remove teacher-owned course content.
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_queryset(self, target_type):
        user = self.request.user
        if user.role == 'admin':
            if target_type == 'module':
                return Module.objects.all()
            if target_type == 'video':
                return Video.objects.all()
            if target_type == 'resource':
                return Resource.objects.all()
            if target_type == 'assignment':
                return Assignment.objects.all()
            return None

        if target_type == 'module':
            return Module.objects.filter(course__instructor=user)
        if target_type == 'video':
            return Video.objects.filter(module__course__instructor=user)
        if target_type == 'resource':
            return Resource.objects.filter(Q(course__instructor=user) | Q(module__course__instructor=user))
        if target_type == 'assignment':
            return Assignment.objects.filter(Q(course__instructor=user) | Q(module__course__instructor=user))
        return None

    def get_serializer(self, target_type, instance, request):
        if target_type == 'module':
            return ModuleSerializer(instance, context={'request': request})
        if target_type == 'video':
            return VideoSerializer(instance, context={'request': request})
        if target_type == 'resource':
            return ResourceSerializer(instance, context={'request': request})
        if target_type == 'assignment':
            return AssignmentSerializer(instance, context={'request': request})
        return None

    def get(self, request, target_type, pk):
        qs = self.get_queryset(target_type)
        if qs is None:
            return Response({'error': 'Invalid content type.'}, status=400)
        try:
            item = qs.get(pk=pk)
        except (Module.DoesNotExist, Video.DoesNotExist, Resource.DoesNotExist, Assignment.DoesNotExist):
            return Response({'error': 'Content not found or you do not have permission to access it.'}, status=404)

        serializer = self.get_serializer(target_type, item, request)
        return Response(serializer.data)

    def patch(self, request, target_type, pk):
        qs = self.get_queryset(target_type)
        if qs is None:
            return Response({'error': 'Invalid content type.'}, status=400)
        try:
            item = qs.get(pk=pk)
        except (Module.DoesNotExist, Video.DoesNotExist, Resource.DoesNotExist, Assignment.DoesNotExist):
            return Response({'error': 'Content not found or you do not have permission to modify it.'}, status=404)

        if target_type == 'module':
            serializer = ModuleSerializer(item, data=request.data, partial=True, context={'request': request})
        elif target_type == 'video':
            serializer = VideoSerializer(item, data=request.data, partial=True, context={'request': request})
        elif target_type == 'resource':
            serializer = ResourceSerializer(item, data=request.data, partial=True, context={'request': request})
        elif target_type == 'assignment':
            serializer = AssignmentSerializer(item, data=request.data, partial=True, context={'request': request})
        else:
            return Response({'error': 'Invalid content type.'}, status=400)

        if serializer.is_valid():
            updated = serializer.save()
            return Response(self.get_serializer(target_type, updated, request).data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, target_type, pk):
        qs = self.get_queryset(target_type)
        if qs is None:
            return Response({'error': 'Invalid content type.'}, status=400)
        try:
            item = qs.get(pk=pk)
        except (Module.DoesNotExist, Video.DoesNotExist, Resource.DoesNotExist, Assignment.DoesNotExist):
            return Response({'error': 'Content not found or you do not have permission to delete it.'}, status=404)

        item.delete()
        return Response({'message': f'{target_type.capitalize()} deleted successfully.'}, status=200)


# ─── Quiz APIs ────────────────────────────────────────────────────────────────

class QuizListCreateView(APIView):
    """
    GET  /api/quizzes/ — List quizzes (filtered by ?course_id=<id>).
    POST /api/quizzes/ — Create quiz with questions (Teacher/Admin).
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsTeacher()]
        return [permissions.AllowAny()]

    def get(self, request):
        course_id = request.query_params.get('course_id')
        qs = Quiz.objects.all()
        if course_id:
            qs = qs.filter(course_id=course_id)

        data = []
        for q in qs:
            item = QuizSerializer(q).data
            if request.user.is_authenticated:
                sub = StudentQuiz.objects.filter(quiz=q, student=request.user).first()
                item['is_submitted'] = bool(sub)
                item['student_score'] = sub.score if sub else None
                item['student_passed'] = sub.passed if sub else False
            data.append(item)
        return Response(data)

    def post(self, request):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            quiz = serializer.save()
            questions_data = request.data.get('questions', [])
            for q in questions_data:
                QuizQuestion.objects.create(
                    quiz=quiz,
                    question_text=q.get('question_text'),
                    option_a=q.get('option_a'),
                    option_b=q.get('option_b'),
                    option_c=q.get('option_c'),
                    option_d=q.get('option_d'),
                    correct_option=q.get('correct_option', 'A'),
                    marks=q.get('marks', 1)
                )
            course = quiz.course
            course.quizzes_count = course.quizzes.count()
            course.save()
            return Response(QuizDetailSerializer(quiz).data, status=201)
        return Response(serializer.errors, status=400)


class QuizDetailView(APIView):
    """
    GET /api/quizzes/<id>/ — Retrieve a single quiz with questions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found.'}, status=404)

        if request.user.role in ['teacher', 'admin']:
            serializer = QuizDetailSerializer(quiz)
            return Response(serializer.data)
        else:
            data = QuizSerializer(quiz).data
            questions = QuizQuestionStudentSerializer(quiz.questions.all(), many=True).data
            data['questions'] = questions
            sub = StudentQuiz.objects.filter(quiz=quiz, student=request.user).first()
            data['submission'] = StudentQuizSerializer(sub).data if sub else None
            return Response(data)


class QuizSubmitView(APIView):
    """
    POST /api/quizzes/<id>/submit/ — Evaluate and save student quiz answers.
    Body format: { "answers": { "<question_id>": "A", "<question_id_2>": "C" } }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found.'}, status=404)

        user_answers = request.data.get('answers', {})
        questions = quiz.questions.all()

        score = 0
        total_marks = 0
        results_breakdown = []

        for q in questions:
            total_marks += q.marks
            chosen = str(user_answers.get(str(q.id)) or user_answers.get(q.id) or '').upper()
            is_correct = (chosen == q.correct_option)
            if is_correct:
                score += q.marks
            results_breakdown.append({
                'question_id': q.id,
                'question_text': q.question_text,
                'chosen_option': chosen,
                'correct_option': q.correct_option,
                'is_correct': is_correct,
                'marks': q.marks if is_correct else 0
            })

        passing_pct = quiz.passing_percentage
        earned_pct = (score / total_marks * 100) if total_marks > 0 else 0
        passed = (earned_pct >= passing_pct)

        sub, created = StudentQuiz.objects.get_or_create(
            quiz=quiz,
            student=request.user,
            defaults={
                'score': score,
                'total_marks': total_marks,
                'passed': passed,
                'answers': user_answers,
            }
        )
        if not created:
            sub.score = score
            sub.total_marks = total_marks
            sub.passed = passed
            sub.answers = user_answers
            sub.save()

        # Re-evaluate certificate eligibility for this student!
        cert, status_info = check_and_issue_certificate(request.user, quiz.course)

        return Response({
            'message': 'Quiz evaluated successfully!',
            'score': score,
            'total_marks': total_marks,
            'percentage': round(earned_pct, 1),
            'passed': passed,
            'certificate_unlocked': bool(cert),
            'certificate_number': cert.certificate_number if cert else None,
            'certificate_reason': status_info['reason'],
            'results': results_breakdown
        })


# ─── Admin Oversight & Leaderboards ──────────────────────────────────────────

class AdminTeacherActivityView(APIView):
    """
    GET /api/admin/teachers/ — Detailed work activity matrix for all teachers.
    Admin can monitor who is creating videos, uploading resources/links, setting assignments & quizzes.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        teachers = User.objects.filter(role='teacher')
        data = []
        for t in teachers:
            courses = Course.objects.filter(instructor=t)
            videos_count = Video.objects.filter(module__course__in=courses).count()
            resources_count = Resource.objects.filter(course__in=courses).count()
            assignments_count = Assignment.objects.filter(course__in=courses).count()
            quizzes_count = Quiz.objects.filter(course__in=courses).count()
            routines_count = CourseRoutine.objects.filter(course__in=courses).count()
            students_count = Enrollment.objects.filter(course__in=courses).values('user').distinct().count()

            data.append({
                'id': t.id,
                'name': t.get_full_name() or t.username,
                'email': t.email,
                'avatar': request.build_absolute_uri(t.profile_picture.url) if t.profile_picture else None,
                'courses_count': courses.count(),
                'videos_count': videos_count,
                'resources_count': resources_count,
                'assignments_count': assignments_count,
                'quizzes_count': quizzes_count,
                'routines_count': routines_count,
                'students_count': students_count,
            })
        return Response(data)


class AdminSubmissionsView(APIView):
    """
    GET /api/admin/submissions/ — All student assignment and quiz submissions platform-wide.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        assignments = StudentAssignment.objects.select_related('assignment', 'assignment__course', 'student').order_by('-submitted_at')[:50]
        quizzes = StudentQuiz.objects.select_related('quiz', 'quiz__course', 'student').order_by('-submitted_at')[:50]

        assignments_data = StudentAssignmentSerializer(assignments, many=True).data
        quizzes_data = StudentQuizSerializer(quizzes, many=True).data

        return Response({
            'assignment_submissions': assignments_data,
            'quiz_submissions': quizzes_data,
        })


class LeaderboardView(APIView):
    """
    GET /api/leaderboard/ — Platform-wide student leaderboard ranking.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        students = User.objects.filter(role='student')
        leaderboard = []

        from django.db.models import Sum

        for student in students:
            assignment_points = StudentAssignment.objects.filter(
                student=student, status='approved'
            ).aggregate(Sum('marks_obtained'))['marks_obtained__sum'] or 0

            quiz_points = StudentQuiz.objects.filter(
                student=student, passed=True
            ).aggregate(Sum('score'))['score__sum'] or 0

            total_points = assignment_points + quiz_points
            completed_courses = Enrollment.objects.filter(user=student, is_completed=True).count()
            certificates_earned = Certificate.objects.filter(user=student).count()

            leaderboard.append({
                'id': student.id,
                'name': student.get_full_name() or student.username,
                'email': student.email,
                'total_points': total_points,
                'assignment_points': assignment_points,
                'quiz_points': quiz_points,
                'completed_courses': completed_courses,
                'certificates_earned': certificates_earned,
            })

        leaderboard.sort(key=lambda x: x['total_points'], reverse=True)

        for idx, item in enumerate(leaderboard):
            item['rank'] = idx + 1

        return Response(leaderboard[:20])


class AdminUserRoleView(APIView):
    """
    POST /api/admin/users/role/ — Update a user role ('student', 'teacher', 'admin').
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')

        if not user_id or new_role not in ['student', 'teacher', 'admin']:
            return Response({'error': 'Valid user_id and role (student, teacher, admin) required.'}, status=400)

        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        target_user.role = new_role
        if new_role == 'admin':
            target_user.is_staff = True
        target_user.save()

        return Response({
            'message': f"Role for {target_user.email} updated to '{new_role}'.",
            'user': UserProfileSerializer(target_user).data
        })


# ─── Admin: Course & Teacher Assignment ──────────────────────────────────────

class AdminCourseManageView(APIView):
    """
    GET  /api/admin/courses/  — List all courses with instructor info, price, and categories.
    POST /api/admin/courses/  — Create a new course.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        courses = Course.objects.select_related('instructor', 'category').all()
        data = []
        for c in courses:
            data.append({
                'id': c.id,
                'title': c.title,
                'slug': c.slug,
                'category': c.category.name if c.category else None,
                'category_id': c.category.id if c.category else None,
                'is_active': c.is_active,
                'price': str(c.price),
                'enrollment_count': c.enrollments.count(),
                'instructor': {
                    'id': c.instructor.id,
                    'name': c.instructor.get_full_name() or c.instructor.email,
                    'email': c.instructor.email,
                } if c.instructor else None,
            })
        # Return list of available teachers for the dropdown
        teachers = User.objects.filter(role='teacher').values('id', 'first_name', 'last_name', 'email')
        teachers_list = [
            {'id': t['id'], 'name': f"{t['first_name']} {t['last_name']}".strip() or t['email'], 'email': t['email']}
            for t in teachers
        ]
        # Return list of categories for new course form
        categories_list = list(Category.objects.values('id', 'name'))
        return Response({'courses': data, 'teachers': teachers_list, 'categories': categories_list})

    def post(self, request):
        """Create a new course from the admin panel."""
        import re
        title = request.data.get('title', '').strip()
        price = request.data.get('price', 0)
        category_id = request.data.get('category_id')
        teacher_id = request.data.get('teacher_id')
        description = request.data.get('description', '')
        duration_hours = request.data.get('duration_hours', 0)

        if not title:
            return Response({'error': 'Course title is required.'}, status=400)

        # Auto-generate unique slug
        base_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        slug = base_slug
        counter = 1
        while Course.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        category = None
        if category_id:
            try:
                category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                pass

        instructor = None
        if teacher_id:
            try:
                instructor = User.objects.get(pk=teacher_id, role='teacher')
            except User.DoesNotExist:
                pass

        course = Course.objects.create(
            title=title,
            slug=slug,
            price=price,
            category=category,
            instructor=instructor,
            description=description,
            duration_hours=duration_hours,
            is_active=True,
        )
        return Response({'message': f'Course "{course.title}" created successfully!', 'course_id': course.id, 'slug': course.slug}, status=201)




class AdminCourseAssignTeacherView(APIView):
    """
    POST /api/admin/courses/<id>/assign-teacher/
    Body: { "teacher_id": <int> }
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        teacher_id = request.data.get('teacher_id')
        if not teacher_id:
            return Response({'error': 'teacher_id is required.'}, status=400)
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=404)
        try:
            teacher = User.objects.get(pk=teacher_id, role='teacher')
        except User.DoesNotExist:
            return Response({'error': 'Teacher not found or user is not a teacher.'}, status=404)

        course.instructor = teacher
        course.save()
        return Response({
            'message': f"'{teacher.get_full_name() or teacher.email}' assigned to '{course.title}'.",
            'course_id': course.id,
            'instructor_id': teacher.id,
        })


# ─── Admin: Users List ────────────────────────────────────────────────────────

class AdminUsersListView(APIView):
    """
    GET  /api/admin/users/      — List all users with roles.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        data = []
        for u in users:
            data.append({
                'id': u.id,
                'name': u.get_full_name() or u.username,
                'email': u.email,
                'role': u.role,
                'date_joined': u.date_joined,
                'is_active': u.is_active,
            })
        return Response(data)


# ─── Teacher: Live Class Routine Management ───────────────────────────────────

class TeacherRoutineView(APIView):
    """
    GET  /api/teacher/routines/  — List all routines for teacher's courses.
    POST /api/teacher/routines/  — Create a new live class / routine event.
    Body: { course_id, title, event_type, day_of_week, date, start_time, end_time, description, live_link }
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request):
        if request.user.role == 'admin':
            courses = Course.objects.all()
        else:
            courses = Course.objects.filter(instructor=request.user)
        routines = CourseRoutine.objects.filter(course__in=courses).select_related('course').order_by('date', 'start_time')
        data = []
        for r in routines:
            data.append({
                'id': r.id,
                'course_id': r.course.id,
                'course_title': r.course.title,
                'title': r.title,
                'event_type': r.event_type,
                'event_type_display': r.get_event_type_display(),
                'day_of_week': r.day_of_week,
                'date': r.date,
                'start_time': r.start_time,
                'end_time': r.end_time,
                'description': r.description,
                'live_link': r.live_link,
            })
        return Response(data)

    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'course_id is required.'}, status=400)
        try:
            if request.user.role == 'admin':
                course = Course.objects.get(pk=course_id)
            else:
                course = Course.objects.get(pk=course_id, instructor=request.user)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found or you are not the instructor.'}, status=404)

        routine = CourseRoutine.objects.create(
            course=course,
            title=request.data.get('title', 'Live Class'),
            event_type=request.data.get('event_type', 'live_class'),
            day_of_week=request.data.get('day_of_week', ''),
            date=request.data.get('date') or None,
            start_time=request.data.get('start_time') or None,
            end_time=request.data.get('end_time') or None,
            description=request.data.get('description', ''),
            live_link=request.data.get('live_link', ''),
        )
        return Response({
            'message': 'Live class scheduled successfully!',
            'routine': {
                'id': routine.id,
                'course_title': routine.course.title,
                'title': routine.title,
                'event_type': routine.event_type,
                'date': routine.date,
                'start_time': routine.start_time,
                'live_link': routine.live_link,
            }
        }, status=201)

    def delete(self, request, pk=None):
        """DELETE /api/teacher/routines/<id>/ — Remove a routine."""
        try:
            if request.user.role == 'admin':
                routine = CourseRoutine.objects.get(pk=pk)
            else:
                routine = CourseRoutine.objects.get(pk=pk, course__instructor=request.user)
        except CourseRoutine.DoesNotExist:
            return Response({'error': 'Routine not found.'}, status=404)
        routine.delete()
        return Response({'message': 'Routine deleted.'})


# ─── Student: View Live Class Routines ────────────────────────────────────────

class StudentRoutineView(APIView):
    """
    GET /api/routines/  — Returns upcoming live classes for all enrolled courses.
    Query params: ?course_id=<id>  (optional — filter by course)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Students see routines for their enrolled courses; teachers/admins see all
        if request.user.role == 'student':
            enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
            qs = CourseRoutine.objects.filter(course_id__in=enrolled_courses)
        elif request.user.role == 'teacher':
            qs = CourseRoutine.objects.filter(course__instructor=request.user)
        else:
            qs = CourseRoutine.objects.all()

        course_id = request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)

        qs = qs.select_related('course').order_by('date', 'start_time')

        data = []
        for r in qs:
            data.append({
                'id': r.id,
                'course_id': r.course.id,
                'course_title': r.course.title,
                'title': r.title,
                'event_type': r.event_type,
                'event_type_display': r.get_event_type_display(),
                'day_of_week': r.day_of_week,
                'date': r.date,
                'start_time': r.start_time,
                'end_time': r.end_time,
                'description': r.description,
                'live_link': r.live_link,
            })
        return Response(data)


# ─── Notifications ────────────────────────────────────────────────────────────

class NotificationListView(APIView):
    """GET /api/notifications/ — List notifications for logged-in user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        unread_count = notifications.filter(is_read=False).count()
        serializer = NotificationSerializer(notifications[:50], many=True, context={'request': request})
        return Response({
            'unread_count': unread_count,
            'notifications': serializer.data
        })


class NotificationMarkReadView(APIView):
    """POST /api/notifications/read/ — Mark notifications as read."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        notification_id = request.data.get('notification_id')
        if notification_id:
            Notification.objects.filter(user=request.user, pk=notification_id).update(is_read=True)
        else:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'Notifications marked as read.'})

