"""
TutorBhaiya — API URL Routing
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── CSRF ──────────────────────────────────────────────────────────────────
    path('csrf/', views.get_csrf_token, name='csrf-token'),

    # ── Auth ──────────────────────────────────────────────────────────────────
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/',    views.LoginView.as_view(),    name='login'),
    path('auth/logout/',   views.LogoutView.as_view(),   name='logout'),
    path('auth/me/',       views.MeView.as_view(),       name='me'),

    # ── Categories ────────────────────────────────────────────────────────────
    path('categories/', views.CategoryListView.as_view(), name='categories'),

    # ── Courses ───────────────────────────────────────────────────────────────
    path('courses/',         views.CourseListView.as_view(),   name='courses'),
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:pk>/player/', views.CoursePlayerView.as_view(), name='course-player'),

    # ── Enrollments ───────────────────────────────────────────────────────────
    path('enrollments/',                   views.EnrollmentListCreateView.as_view(), name='enrollments'),
    path('enrollments/complete-video/',    views.MarkVideoCompleteView.as_view(),    name='mark-video-complete'),
    path('enrollments/<int:pk>/',          views.EnrollmentDetailView.as_view(),     name='enrollment-detail'),

    # ── Dashboard & Work Management ──────────────────────────────────────────
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('teacher/dashboard/', views.TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('teacher/courses/', views.TeacherCourseListView.as_view(), name='teacher-courses'),
    path('teacher/students/', views.TeacherStudentListView.as_view(), name='teacher-students'),
    path('teacher/assignments/submissions/', views.TeacherAssignmentGradingView.as_view(), name='teacher-submissions'),
    path('teacher/assignments/grade/', views.TeacherAssignmentGradingView.as_view(), name='teacher-grade'),
    path('teacher/content/<str:target_type>/', views.TeacherContentManageView.as_view(), name='teacher-content-manage'),
    path('teacher/content/<str:target_type>/<int:pk>/', views.TeacherContentItemManageView.as_view(), name='teacher-content-manage-item'),
    path('teacher/routines/', views.TeacherRoutineView.as_view(), name='teacher-routines'),
    path('teacher/routines/<int:pk>/', views.TeacherRoutineView.as_view(), name='teacher-routine-delete'),

    # ── Quizzes ───────────────────────────────────────────────────────────────
    path('quizzes/', views.QuizListCreateView.as_view(), name='quizzes'),
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:pk>/submit/', views.QuizSubmitView.as_view(), name='quiz-submit'),

    # ── Admin Oversight & Analytics ──────────────────────────────────────────
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/teachers/', views.AdminTeacherActivityView.as_view(), name='admin-teacher-activity'),
    path('admin/submissions/', views.AdminSubmissionsView.as_view(), name='admin-submissions'),
    path('admin/users/role/', views.AdminUserRoleView.as_view(), name='admin-user-role'),
    path('admin/users/', views.AdminUsersListView.as_view(), name='admin-users-list'),
    path('admin/courses/', views.AdminCourseManageView.as_view(), name='admin-courses'),
    path('admin/courses/<int:pk>/assign-teacher/', views.AdminCourseAssignTeacherView.as_view(), name='admin-assign-teacher'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),

    # ── Live Class Routines (Student View) ────────────────────────────────────
    path('routines/', views.StudentRoutineView.as_view(), name='routines'),

    # ── Contact ───────────────────────────────────────────────────────────────
    path('contact/', views.ContactView.as_view(), name='contact'),

    # ── Assignments ───────────────────────────────────────────────────────────
    path('assignments/<int:pk>/submit/', views.SubmitAssignmentView.as_view(), name='submit-assignment'),

    # ── Certificates ──────────────────────────────────────────────────────────
    path('certificates/', views.CertificateListView.as_view(), name='certificates'),
    path('certificates/<str:certificate_number>/', views.CertificateDetailView.as_view(), name='certificate-detail'),

    # ── Books ─────────────────────────────────────────────────────────────────
    path('books/', views.BookListView.as_view(), name='books'),

    # ── Careers ───────────────────────────────────────────────────────────────
    path('careers/', views.JobPostingListView.as_view(), name='careers'),
    path('careers/<int:pk>/apply/', views.JobApplicationCreateView.as_view(), name='career-apply'),

    # ── Admin Jobs ────────────────────────────────────────────────────────────
    path('admin/jobs/', views.AdminJobPostingView.as_view(), name='admin-jobs'),

    # ── Notifications ─────────────────────────────────────────────────────────
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/read/', views.NotificationMarkReadView.as_view(), name='notifications-read'),
]



