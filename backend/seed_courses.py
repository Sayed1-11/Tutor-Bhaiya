import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorbhaiya.settings')
django.setup()

from api.models import Category, Course, User, Module, Video

def seed_modules_for_course(course):
    # Module 1
    m1 = Module.objects.create(course=course, title="1. Introduction & Basics", order=1)
    Video.objects.create(module=m1, title="1.1 Getting Started", video_url="https://www.w3schools.com/html/mov_bbb.mp4", duration_minutes=15, order=1)
    Video.objects.create(module=m1, title="1.2 Core Concepts", video_url="https://www.w3schools.com/html/mov_bbb.mp4", duration_minutes=25, order=2)
    
    # Module 2
    m2 = Module.objects.create(course=course, title="2. Advanced Topics", order=2)
    Video.objects.create(module=m2, title="2.1 Deep Dive", video_url="https://www.w3schools.com/html/mov_bbb.mp4", duration_minutes=35, order=1)
    Video.objects.create(module=m2, title="2.2 Project Setup", video_url="https://www.w3schools.com/html/mov_bbb.mp4", duration_minutes=40, order=2)

def run_seed():
    print("Clearing existing Categories and Courses to avoid duplicates...")
    Course.objects.all().delete()
    Category.objects.all().delete()

    print("Ensuring a teacher user exists...")
    teacher, created = User.objects.get_or_create(
        email='teacher@tutorbhaiya.com',
        defaults={
            'username': 'master_teacher',
            'first_name': 'Master',
            'last_name': 'Teacher',
            'role': 'teacher'
        }
    )
    if created:
        teacher.set_password('teacher123')
        teacher.save()
        print("Created new teacher user: teacher@tutorbhaiya.com / teacher123")
    else:
        # ensure role is teacher
        teacher.role = 'teacher'
        teacher.save()
        print("Using existing teacher user.")

    # 1. Create Categories
    print("Creating categories...")
    cat_ev = Category.objects.create(
        name="English Version (SSC & HSC)", slug="ssc-hsc", icon="ph-graduation-cap", order=1
    )
    cat_em = Category.objects.create(
        name="English Medium (O & A Level)", slug="o-a-level", icon="ph-globe", order=2
    )
    cat_skills = Category.objects.create(
        name="Skills & More", slug="skills", icon="ph-rocket", order=3
    )

    # 2. English Version Courses
    print("Creating English Version Courses...")
    ev_courses = [
        {"title": "Class 5 - Complete Syllabus (English Version)", "badge": "CLASS 5", "price": 1000},
        {"title": "Class 6 - Complete Syllabus (English Version)", "badge": "CLASS 6", "price": 1200},
        {"title": "Class 7 - Complete Syllabus (English Version)", "badge": "CLASS 7", "price": 1500},
        {"title": "Class 8 - JSC Preparation (English Version)", "badge": "CLASS 8", "price": 2000},
        {"title": "Class 9 - Foundation Course (English Version)", "badge": "CLASS 9", "price": 2500},
        {"title": "SSC Batch - Final Preparation (EV)", "badge": "SSC BATCH", "price": 3000},
        {"title": "HSC Batch - Physics & Math (EV)", "badge": "HSC BATCH", "price": 4000},
    ]

    for c in ev_courses:
        c_obj = Course.objects.create(
            title=c["title"],
            category=cat_ev,
            instructor=teacher,
            price=c["price"],
            duration_hours=40,
            badge_label=c["badge"],
            badge_color="bg-primary",
            description=f"Comprehensive course for {c['title']} covering all core subjects.",
            is_active=True
        )
        seed_modules_for_course(c_obj)

    # 3. English Medium Courses
    print("Creating English Medium Courses...")
    em_courses = [
        {"title": "Standard 5 - Edexcel/Cambridge", "badge": "STD 5", "price": 1500},
        {"title": "Standard 6 - Complete Science & Math", "badge": "STD 6", "price": 1800},
        {"title": "Standard 7 - Core Subjects", "badge": "STD 7", "price": 2000},
        {"title": "Standard 8 - Pre-O Level Foundation", "badge": "STD 8", "price": 2500},
        {"title": "O Level - Physics, Chem, Math", "badge": "O LEVEL", "price": 5000},
        {"title": "A Level - Advanced Sciences", "badge": "A LEVEL", "price": 6000},
    ]

    for c in em_courses:
        c_obj = Course.objects.create(
            title=c["title"],
            category=cat_em,
            instructor=teacher,
            price=c["price"],
            duration_hours=50,
            badge_label=c["badge"],
            badge_color="bg-accent2",
            description=f"Expertly designed course for {c['title']}.",
            is_active=True
        )
        seed_modules_for_course(c_obj)

    # 4. Skills Courses
    print("Creating Skills & More Courses...")
    skill_courses = [
        {"title": "Spoken English Masterclass", "badge": "SPOKEN", "price": 1500, "color": "bg-secondary"},
        {"title": "English Foundation & Grammar", "badge": "GRAMMAR", "price": 1000, "color": "bg-emerald-600"},
        {"title": "Full Stack Web Development (MERN)", "badge": "WEB DEV", "price": 8000, "color": "bg-violet-600"},
        {"title": "Graphic Design & UI/UX", "badge": "DESIGN", "price": 5000, "color": "bg-pink-500"},
        {"title": "Data Science & AI with Python", "badge": "AI/ML", "price": 10000, "color": "bg-amber-500"},
    ]

    for c in skill_courses:
        c_obj = Course.objects.create(
            title=c["title"],
            category=cat_skills,
            instructor=teacher,
            price=c["price"],
            duration_hours=60,
            badge_label=c["badge"],
            badge_color=c["color"],
            description=f"Learn in-demand skills with our {c['title']} course.",
            is_active=True,
            is_featured=True
        )
        seed_modules_for_course(c_obj)

    print("Done seeding courses!")

if __name__ == '__main__':
    run_seed()
