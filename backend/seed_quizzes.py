import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorbhaiya.settings')
django.setup()

from api.models import (
    User, Course, Module, Video, Resource, Assignment, StudentAssignment,
    Quiz, QuizQuestion, StudentQuiz, Category, Enrollment, Certificate
)

def seed_quizzes_and_roles():
    print("Starting seeding process for Admin, Teacher, Quizzes, Assignments, and Submissions...")

    # 1. Create or update demo users
    admin_user, _ = User.objects.get_or_create(
        email='admin@tutorbhaiya.com',
        defaults={
            'username': 'admin_tutorbhaiya',
            'first_name': 'Super',
            'last_name': 'Admin',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    admin_user.set_password('admin123')
    admin_user.role = 'admin'
    admin_user.is_staff = True
    admin_user.save()

    teacher_user, _ = User.objects.get_or_create(
        email='teacher@tutorbhaiya.com',
        defaults={
            'username': 'teacher_sayed',
            'first_name': 'Sheikh',
            'last_name': 'Sayed (Instructor)',
            'role': 'teacher',
        }
    )
    teacher_user.set_password('teacher123')
    teacher_user.role = 'teacher'
    teacher_user.save()

    student_user, _ = User.objects.get_or_create(
        email='student@tutorbhaiya.com',
        defaults={
            'username': 'student_tanvir',
            'first_name': 'Tanvir',
            'last_name': 'Ahmed',
            'role': 'student',
        }
    )
    student_user.set_password('student123')
    student_user.role = 'student'
    student_user.save()

    print(f"Users setup: Admin ({admin_user.email}), Teacher ({teacher_user.email}), Student ({student_user.email})")

    # 2. Attach instructor to all courses
    courses = Course.objects.all()
    for course in courses:
        if not course.instructor:
            course.instructor = teacher_user
            course.save()

    target_course = courses.first()
    if not target_course:
        print("No course found to seed content.")
        return

    print(f"Targeting course for seed content: '{target_course.title}'")

    # Enroll student in course
    enrollment, _ = Enrollment.objects.get_or_create(user=student_user, course=target_course)

    # 3. Create Module, Video, Resource, Assignment for Target Course
    module, _ = Module.objects.get_or_create(
        course=target_course,
        title="Module 1: Fundamental Concepts & Problem Solving",
        defaults={'order': 1, 'description': 'Master core concepts and foundational equations.'}
    )

    v1, _ = Video.objects.get_or_create(
        module=module,
        title="1.1 Introduction & Core Principles",
        defaults={'video_url': 'https://www.w3schools.com/html/mov_bbb.mp4', 'duration_minutes': 15, 'order': 1}
    )

    v2, _ = Video.objects.get_or_create(
        module=module,
        title="1.2 Mathematical Derivations & Board Exam Problems",
        defaults={'video_url': 'https://www.w3schools.com/html/mov_bbb.mp4', 'duration_minutes': 22, 'order': 2}
    )

    resource, _ = Resource.objects.get_or_create(
        course=target_course,
        title="Chapter 1 Revision Handout PDF & Formula Sheet",
        defaults={'url': 'https://www.w3.org/W3C/DesignIssues/pdf/paper.pdf'}
    )

    assignment, _ = Assignment.objects.get_or_create(
        course=target_course,
        title="Assignment 1: Solving Kinetic Motion & Board Equations",
        defaults={
            'description': 'Explain the 3 main laws of motion, solve problem 4B from board exam 2024, and derive the velocity equation.',
            'total_marks': 50,
        }
    )

    # Create Student Assignment submission
    sub, _ = StudentAssignment.objects.get_or_create(
        assignment=assignment,
        student=student_user,
        defaults={
            'submission_text': 'Here is my complete solution:\n1. Newton 1st law: Inertia...\n2. Problem 4B solution: v = u + at => 25 m/s.\n3. Derivation steps attached.',
            'status': 'pending',
        }
    )

    # 4. Create Quiz & Questions
    quiz, _ = Quiz.objects.get_or_create(
        course=target_course,
        title="Quiz 1: Fundamentals & Board Exam Prep",
        defaults={
            'description': 'Test your understanding of Module 1 concepts before claiming your certificate.',
            'passing_percentage': 60,
        }
    )

    if quiz.questions.count() == 0:
        QuizQuestion.objects.create(
            quiz=quiz,
            question_text="What is the standard SI unit of acceleration?",
            option_a="m/s",
            option_b="m/s²",
            option_c="kg·m/s",
            option_d="Newton",
            correct_option="B",
            marks=5
        )
        QuizQuestion.objects.create(
            quiz=quiz,
            question_text="Which law of motion defines the quantitative force equation F = ma?",
            option_a="First Law",
            option_b="Second Law",
            option_c="Third Law",
            option_d="Law of Universal Gravitation",
            correct_option="B",
            marks=5
        )
        QuizQuestion.objects.create(
            quiz=quiz,
            question_text="If initial velocity u = 0, acceleration a = 2 m/s², and time t = 5s, what is final velocity v?",
            option_a="5 m/s",
            option_b="10 m/s",
            option_c="15 m/s",
            option_d="20 m/s",
            correct_option="B",
            marks=10
        )

    # Create Student Quiz Submission (Passed)
    StudentQuiz.objects.get_or_create(
        quiz=quiz,
        student=student_user,
        defaults={
            'score': 20,
            'total_marks': 20,
            'passed': True,
            'answers': {'1': 'B', '2': 'B', '3': 'B'}
        }
    )

    # Update course counts
    target_course.assignments_count = target_course.assignments.count()
    target_course.quizzes_count = target_course.quizzes.count()
    target_course.save()

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed_quizzes_and_roles()
