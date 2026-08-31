from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Course, Enrollment, Module, Assignment, StudentAssignment, Quiz, QuizQuestion, StudentQuiz, Payment

User = get_user_model()


class TutorBhaiyaAPITests(APITestCase):

    def setUp(self):
        # Create Teacher
        self.teacher = User.objects.create_user(
            username='test_teacher',
            email='teacher@example.com',
            password='teacherpassword123',
            role='teacher'
        )

        # Create Category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            icon='ph-books'
        )

        # Create Course
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            instructor=self.teacher,
            price=1000.00,
            duration_hours=10,
            category=self.category,
            is_active=True
        )

        # Create Demo Student User
        self.user_data = {
            'full_name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'phone': '01712345678'
        }

    def test_category_list(self):
        """Test categories listing API endpoint."""
        url = reverse('categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Category')

    def test_course_list(self):
        """Test courses listing and filtering API endpoint."""
        url = reverse('courses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Course')

        # Test filtering by category
        url_filter = f"{url}?category=test-category"
        response_filter = self.client.get(url_filter)
        self.assertEqual(response_filter.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_filter.data), 1)

    def test_user_registration_and_login(self):
        """Test user signup, login, and profile fetching."""
        # Register User
        reg_url = reverse('register')
        reg_response = self.client.post(reg_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', reg_response.data)
        self.assertEqual(reg_response.data['user']['email'], 'testuser@example.com')

        # Check me endpoint is authenticated
        me_url = reverse('me')
        me_response = self.client.get(me_url)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertTrue(me_response.data['authenticated'])

        # Logout
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        # Check me endpoint is now unauthenticated
        me_response_after = self.client.get(me_url)
        self.assertEqual(me_response_after.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_quiz_creation_and_submission(self):
        """Test creating a quiz and student submission evaluation."""
        student = User.objects.create_user(username='student1', email='student1@test.com', password='pass', role='student')
        self.client.force_authenticate(user=self.teacher)

        # Create Quiz
        quiz_url = reverse('quizzes')
        quiz_payload = {
            'course': self.course.id,
            'title': 'Unit Test Quiz',
            'passing_percentage': 50,
            'questions': [
                {
                    'question_text': 'What is 2+2?',
                    'option_a': '3', 'option_b': '4', 'option_c': '5', 'option_d': '6',
                    'correct_option': 'B', 'marks': 10
                }
            ]
        }
        res = self.client.post(quiz_url, quiz_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        quiz_id = res.data['id']

        # Student submits quiz
        self.client.force_authenticate(user=student)
        submit_url = reverse('quiz-submit', kwargs={'pk': quiz_id})
        q_id = QuizQuestion.objects.get(quiz_id=quiz_id).id
        sub_res = self.client.post(submit_url, {'answers': {str(q_id): 'B'}}, format='json')
        self.assertEqual(sub_res.status_code, status.HTTP_200_OK)
        self.assertTrue(sub_res.data['passed'])
        self.assertEqual(sub_res.data['score'], 10)

    def test_leaderboard_endpoint(self):
        """Test leaderboard API returns student scores."""
        url = reverse('leaderboard')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_enrollment_creates_payment(self):
        """Test that enrolling in a course creates a payment record and updates admin dashboard revenue."""
        student = User.objects.create_user(
            username='student_test',
            email='student_test@example.com',
            password='studentpassword123',
            role='student'
        )
        self.client.force_authenticate(user=student)

        # Post to enrollment endpoint
        enroll_url = reverse('enrollments')
        response = self.client.post(enroll_url, {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify payment was created
        self.assertEqual(Payment.objects.filter(user=student, course=self.course).count(), 1)
        payment = Payment.objects.get(user=student, course=self.course)
        self.assertEqual(float(payment.amount), float(self.course.price))

        # Verify admin dashboard shows the revenue
        admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin_test@example.com',
            password='adminpassword123'
        )
        self.client.force_authenticate(user=admin_user)
        dashboard_url = reverse('admin-dashboard')
        dash_response = self.client.get(dashboard_url)
        self.assertEqual(dash_response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(dash_response.data['stats']['total_revenue']), float(self.course.price))

    def test_admin_dashboard_extended_data(self):
        """Test that AdminDashboardView returns recent payments and top courses."""
        admin_user = User.objects.create_superuser(
            username='admin_test_ext',
            email='admin_ext@example.com',
            password='adminpassword123'
        )
        self.client.force_authenticate(user=admin_user)
        
        # Enrolling a user creates payment
        student = User.objects.create_user(
            username='stud_ext',
            email='stud_ext@example.com',
            password='password123',
            role='student'
        )
        Payment.objects.create(
            user=student,
            course=self.course,
            amount=self.course.price,
            status='completed',
            payment_method='bkash',
            transaction_id='TXN12345'
        )

        url = reverse('admin-dashboard')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('recent_payments', res.data)
        self.assertIn('top_courses', res.data)
        self.assertEqual(len(res.data['recent_payments']), 1)
        self.assertEqual(len(res.data['top_courses']), 1)
        self.assertEqual(res.data['recent_payments'][0]['transaction_id'], 'TXN12345')
        self.assertEqual(float(res.data['top_courses'][0]['revenue']), float(self.course.price))

    def test_admin_create_course(self):
        """Test that AdminCourseManageView POST creates a new course."""
        admin_user = User.objects.create_superuser(
            username='admin_test_create',
            email='admin_create@example.com',
            password='adminpassword123'
        )
        self.client.force_authenticate(user=admin_user)

        url = reverse('admin-courses')
        payload = {
            'title': 'New Test Course from Admin',
            'price': 4500,
            'duration_hours': 50,
            'description': 'A fantastic new course'
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('course_id', res.data)
        
        # Verify it exists in db
        from api.models import Course
        course_obj = Course.objects.get(id=res.data['course_id'])
        self.assertEqual(course_obj.title, 'New Test Course from Admin')
        self.assertEqual(float(course_obj.price), 4500.0)
        self.assertEqual(course_obj.slug, 'new-test-course-from-admin')

    def test_course_player_returns_absolute_assignment_attachment_url(self):
        """Test assignment attachment URLs are absolute in the course-player payload."""
        student = User.objects.create_user(username='student_courseplayer', email='student_courseplayer@example.com', password='password123', role='student')
        module = Module.objects.create(course=self.course, title='Module 1')
        assignment = Assignment.objects.create(
            course=self.course,
            module=module,
            title='Assignment 1',
            description='Read and solve the document.',
            total_marks=50,
        )
        assignment.attachment_file.save('play-fair.txt', SimpleUploadedFile('play-fair.txt', b'hello world'))

        self.client.force_authenticate(user=student)
        self.client.post(reverse('enrollments'), {'course_id': self.course.id}, format='json')

        url = reverse('course-player', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        assignment_payload = next(
            item for item in response.data['course']['modules']
            if item['id'] == module.id
        )['assignments'][0]
        self.assertIn('http://testserver/media/assignment_attachments/', assignment_payload['attachment_file_url'])

    def test_assignment_submission_and_teacher_evaluation_with_notifications(self):
        """Test student assignment submission and teacher evaluation triggering notifications."""
        student = User.objects.create_user(username='student_sub', email='student_sub@example.com', password='password123', role='student')
        assignment = Assignment.objects.create(
            course=self.course,
            title='Homework 1',
            description='Complete exercise 1 to 5',
            total_marks=100
        )

        # 1. Student submits assignment
        self.client.force_authenticate(user=student)
        submit_url = reverse('submit-assignment', kwargs={'pk': assignment.pk})
        res = self.client.post(submit_url, {'submission_text': 'Here is my solution...'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Verify teacher notification created
        from api.models import Notification, StudentAssignment
        notif = Notification.objects.filter(user=self.teacher, notification_type='assignment_submitted').first()
        self.assertIsNotNone(notif)
        self.assertIn('Homework 1', notif.title)

        # 2. Teacher views submissions and grades it
        self.client.force_authenticate(user=self.teacher)
        grading_url = reverse('teacher-submissions')
        get_res = self.client.get(grading_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_res.data), 1)

        sub_id = get_res.data[0]['id']
        grade_url = reverse('teacher-grade')
        grade_res = self.client.post(grade_url, {
            'submission_id': sub_id,
            'marks_obtained': 95,
            'feedback': 'Excellent work!',
            'status': 'approved'
        }, format='json')
        self.assertEqual(grade_res.status_code, status.HTTP_200_OK)

        # Verify student submission updated
        sub_obj = StudentAssignment.objects.get(pk=sub_id)
        self.assertEqual(sub_obj.marks_obtained, 95)
        self.assertEqual(sub_obj.status, 'approved')

        # Verify student notification created
        student_notif = Notification.objects.filter(user=student, notification_type='assignment_graded').first()
        self.assertIsNotNone(student_notif)
        self.assertIn('Excellent work!', student_notif.message)

    def test_teacher_assignment_attachment_and_student_submission_file_visibility(self):
        """Teachers can attach files to assignments and graders can view the student's uploaded file."""
        student = User.objects.create_user(username='student_file', email='student_file@example.com', password='password123', role='student')

        self.client.force_authenticate(user=self.teacher)
        create_url = reverse('teacher-content-manage', kwargs={'target_type': 'assignment'})
        attachment = SimpleUploadedFile('teacher-brief.pdf', b'pdf-content', content_type='application/pdf')
        create_response = self.client.post(create_url, {
            'course': self.course.id,
            'title': 'Upload File Assignment',
            'description': 'Read the attached file and answer.',
            'total_marks': 100,
            'attachment_file': attachment,
        }, format='multipart')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        assignment = Assignment.objects.get(id=create_response.data['data']['id'])
        self.assertTrue(bool(assignment.attachment_file))

        self.client.force_authenticate(user=student)
        submit_url = reverse('submit-assignment', kwargs={'pk': assignment.pk})
        student_file = SimpleUploadedFile('student-solution.pdf', b'student-solution', content_type='application/pdf')
        submit_response = self.client.post(submit_url, {
            'submission_text': 'Attached solution',
            'submission_file': student_file,
        }, format='multipart')
        self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.teacher)
        grading_response = self.client.get(reverse('teacher-submissions'))
        self.assertEqual(grading_response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(grading_response.data) >= 1)
        self.assertIn('submission_file_url', grading_response.data[0])
        self.assertTrue(bool(grading_response.data[0]['submission_file_url']))

    def test_teacher_can_edit_and_delete_assignment(self):
        """Teachers can edit and delete their own assignments."""
        self.client.force_authenticate(user=self.teacher)
        create_url = reverse('teacher-content-manage', kwargs={'target_type': 'assignment'})
        create_resp = self.client.post(create_url, {
            'course': self.course.id,
            'title': 'Draft Assignment',
            'description': 'Initial instructions',
            'total_marks': 25,
        }, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        assignment_id = create_resp.data['data']['id']

        edit_url = reverse('teacher-content-manage-item', kwargs={'target_type': 'assignment', 'pk': assignment_id})
        edit_resp = self.client.patch(edit_url, {
            'title': 'Updated Assignment',
            'description': 'Revised instructions',
            'total_marks': 35,
        }, format='json')
        self.assertEqual(edit_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(edit_resp.data['title'], 'Updated Assignment')

        delete_resp = self.client.delete(edit_url)
        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Assignment.objects.filter(pk=assignment_id).exists())

    def test_teacher_course_player_access(self):
        """Test that teachers can access CoursePlayerView without prior enrollment."""
        self.client.force_authenticate(user=self.teacher)
        player_url = reverse('course-player', kwargs={'pk': self.course.pk})
        res = self.client.get(player_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['course']['title'], 'Test Course')



