import os
import django
import sys
from datetime import time, date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorbhaiya.settings')
django.setup()

from api.models import Course, Category, Book, JobPosting, CourseRoutine, User, Enrollment, Certificate

def seed():
    print("Starting seeding process...")

    # 1. Seed Books
    cat_books = Category.objects.filter(slug='books').first() or Category.objects.first()
    
    books_data = [
        {
            "title": "SSC Physics Formula & Problem Solver",
            "slug": "ssc-physics-formula-problem-solver",
            "author": "Sheikh Sayed",
            "price": 350.00,
            "cover_url": "assets/course1.jpg",
            "description": "Complete chapter-by-chapter formula sheet, mathematical problem breakdowns, and board exam solutions for SSC Physics.",
            "sample_pdf_url": "https://www.w3.org/W3C/DesignIssues/pdf/paper.pdf",
            "is_featured": True,
        },
        {
            "title": "Class 9-10 Higher Math Practice Companion",
            "slug": "class-9-10-higher-math-companion",
            "author": "Rashedul Islam",
            "price": 420.00,
            "cover_url": "assets/course2.jpg",
            "description": "Step-by-step solved geometry, trigonometry, and calculus basics for Class 9 and 10 students.",
            "sample_pdf_url": "https://www.w3.org/W3C/DesignIssues/pdf/paper.pdf",
            "is_featured": True,
        },
        {
            "title": "HSC Organic Chemistry Quick Revision",
            "slug": "hsc-organic-chemistry-quick-revision",
            "author": "Rohima Khanom",
            "price": 480.00,
            "cover_url": "assets/course3.jpg",
            "description": "Reaction mechanisms, named reactions, and mind maps for HSC Chemistry Paper 2.",
            "sample_pdf_url": "https://www.w3.org/W3C/DesignIssues/pdf/paper.pdf",
            "is_featured": True,
        },
        {
            "title": "Spoken English Master Guide & Handbook",
            "slug": "spoken-english-master-guide",
            "author": "Saif Islam",
            "price": 300.00,
            "cover_url": "assets/course4.jpg",
            "description": "Practical conversational templates, vocabulary list, and daily practice dialogues for students and job seekers.",
            "sample_pdf_url": "https://www.w3.org/W3C/DesignIssues/pdf/paper.pdf",
            "is_featured": True,
        },
        {
            "title": "O-Level Physics Revision Essentials",
            "slug": "o-level-physics-revision-essentials",
            "author": "Arifur Rahman",
            "price": 550.00,
            "cover_url": "assets/course5.jpg",
            "description": "Cambridge IGCSE & O-Level Physics topical questions with detailed mark scheme analysis.",
            "sample_pdf_url": "https://www.w3.org/W3C/DesignIssues/pdf/paper.pdf",
            "is_featured": False,
        },
        {
            "title": "Biology Diagram & Conceptual Review",
            "slug": "biology-diagram-conceptual-review",
            "author": "Arifur Rahman",
            "price": 390.00,
            "cover_url": "assets/course6.jpg",
            "description": "Hand-drawn anatomical diagrams, quick charts, and key definitions for SSC & HSC Biology.",
            "sample_pdf_url": "https://www.w3.org/W3C/DesignIssues/pdf/paper.pdf",
            "is_featured": False,
        }
    ]

    for b in books_data:
        Book.objects.update_or_create(
            slug=b["slug"],
            defaults={**b, "category": cat_books}
        )
    print(f"Seeded {len(books_data)} books.")

    # 2. Seed Job Postings
    jobs_data = [
        {
            "title": "Senior Mathematics Educator (SSC & HSC)",
            "department": "Academics",
            "location": "Dhaka, Bangladesh (Hybrid)",
            "job_type": "Full-Time",
            "experience_level": "2+ years teaching experience",
            "description": "We are seeking a passionate Mathematics educator to create engaging lecture video modules, conduct interactive live problem-solving classes, and author problem sets for SSC & HSC students.",
            "requirements": [
                "Bachelor's or Master's degree in Mathematics, Applied Math, Engineering, or related field.",
                "Minimum 2 years of classroom or online teaching experience.",
                "Fluent in explaining complex mathematical concepts clearly.",
                "Proficiency with digital pen tablets and teaching tools."
            ],
            "benefits": [
                "Competitive monthly salary package (BDT 40,000 - 65,000).",
                "Performance bonus per batch.",
                "Flexible work schedule & hybrid workspace.",
                "Career growth to Lead Department Specialist."
            ],
            "is_active": True,
        },
        {
            "title": "Physics Content Developer & Live Tutor",
            "department": "Academics",
            "location": "Dhaka, Bangladesh",
            "job_type": "Full-Time",
            "experience_level": "1-3 years",
            "description": "Lead live physics interactive classes, prepare visual lecture slides, and build experimental demonstration videos.",
            "requirements": [
                "Degree in Physics, Applied Physics, or Electrical Engineering.",
                "Strong background in NCTB and Cambridge Physics syllabus.",
                "Great communication skills on camera."
            ],
            "benefits": [
                "Salary: BDT 35,000 - 55,000 per month.",
                "Health insurance & festive bonuses."
            ],
            "is_active": True,
        },
        {
            "title": "Full Stack Web Developer (Python & JavaScript)",
            "department": "Engineering",
            "location": "Remote / Dhaka",
            "job_type": "Full-Time",
            "experience_level": "2+ years",
            "description": "Develop and maintain the TutorBhaiya web learning platform, video streaming integrations, and interactive student dashboards.",
            "requirements": [
                "Solid expertise in Django REST Framework and modern JavaScript (HTML5/Tailwind/React).",
                "Experience with REST APIs, SQL databases (SQLite/PostgreSQL), and authentication flow.",
                "Understanding of responsive design and web security best practices."
            ],
            "benefits": [
                "Competitive salary (BDT 50,000 - 80,000).",
                "100% remote option available.",
                "Annual learning stipend."
            ],
            "is_active": True,
        },
        {
            "title": "Academic Counselor & Student Success Lead",
            "department": "Student Success",
            "location": "Dhaka, Bangladesh",
            "job_type": "Full-Time",
            "experience_level": "1+ year",
            "description": "Guide prospective students, answer course queries, assist with enrollments, and help students maintain consistent learning progress.",
            "requirements": [
                "Strong interpersonal and empathetic communication skills.",
                "Fluency in Bengali and conversational English.",
                "Ability to work in shifts and manage CRM inquiries."
            ],
            "benefits": [
                "Base salary + enrollment performance incentives.",
                "Friendly work culture and career mentorship."
            ],
            "is_active": True,
        }
    ]

    for j in jobs_data:
        JobPosting.objects.update_or_create(
            title=j["title"],
            defaults=j
        )
    print(f"Seeded {len(jobs_data)} job postings.")

    # 3. Seed Course Routines
    courses = Course.objects.all()
    routine_templates = [
        {"title": "Live Masterclass: Concept & Problem Solving", "event_type": "live_class", "day_of_week": "Sunday", "start_time": time(19, 0), "end_time": time(20, 30), "description": "Interactive problem solving session on Chapter 1 & 2.", "live_link": "https://zoom.us/j/demo123456"},
        {"title": "Live Doubts Solving & Board Questions", "event_type": "live_class", "day_of_week": "Tuesday", "start_time": time(19, 0), "end_time": time(20, 30), "description": "Solving top 10 tricky board questions live with teacher.", "live_link": "https://zoom.us/j/demo123456"},
        {"title": "Weekly Online Quiz & Model Test", "event_type": "exam", "day_of_week": "Thursday", "start_time": time(20, 0), "end_time": time(21, 0), "description": "Online MCQ & written assessment. Total marks: 50."},
        {"title": "Weekly Study Break / Off Day", "event_type": "off_day", "day_of_week": "Friday", "description": "No live classes scheduled. Revise lecture notes and complete pending assignments."}
    ]

    routine_count = 0
    for course in courses:
        for rt in routine_templates:
            CourseRoutine.objects.get_or_create(
                course=course,
                title=rt["title"],
                event_type=rt["event_type"],
                defaults=rt
            )
            routine_count += 1
    print(f"Seeded {routine_count} course routine items across {courses.count()} courses.")

    # 4. Ensure demo certificates exist for completed enrollments
    completed_enrollments = Enrollment.objects.filter(is_completed=True)
    if completed_enrollments.exists():
        for e in completed_enrollments:
            import uuid
            cnum = f"TB-{e.course.id:03d}-{uuid.uuid4().hex[:6].upper()}"
            Certificate.objects.get_or_create(
                enrollment=e,
                defaults={"user": e.user, "course": e.course, "certificate_number": cnum}
            )
        print("Ensured certificates for completed enrollments.")

    # If any user exists, create at least 1 completed enrollment and certificate so certificate page has demo data!
    student = User.objects.filter(role='student').first() or User.objects.first()
    first_course = Course.objects.first()
    if student and first_course:
        enrollment, _ = Enrollment.objects.get_or_create(user=student, course=first_course)
        enrollment.progress = 100
        enrollment.is_completed = True
        enrollment.save()
        Certificate.objects.get_or_create(
            enrollment=enrollment,
            defaults={"user": student, "course": first_course, "certificate_number": f"TB-{first_course.id:03d}-DEMO77"}
        )
        print(f"Created demo certificate for student '{student.email}' in course '{first_course.title}'.")

    print("Seeding finished successfully.")

if __name__ == '__main__':
    seed()
