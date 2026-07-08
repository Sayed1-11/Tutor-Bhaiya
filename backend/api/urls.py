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

    # ── Enrollments ───────────────────────────────────────────────────────────
    path('enrollments/',         views.EnrollmentListCreateView.as_view(), name='enrollments'),
    path('enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(),    name='enrollment-detail'),

    # ── Dashboard ─────────────────────────────────────────────────────────────
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # ── Contact ───────────────────────────────────────────────────────────────
    path('contact/', views.ContactView.as_view(), name='contact'),
]
