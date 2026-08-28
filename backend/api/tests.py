from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Course, Enrollment, Assignment, StudentAssignment, Quiz, QuizQuestion, StudentQuiz

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

