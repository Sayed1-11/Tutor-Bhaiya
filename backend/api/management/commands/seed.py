"""
Management command: python manage.py seed
Populates the database with categories, courses, and a demo user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Category, Course

User = get_user_model()

CATEGORIES = [
    {
        'name': 'English Version (Class 5 - HSC)',
        'slug': 'ssc-hsc',
        'icon': 'ph-exam',
        'description': 'Classes for English Version school and board exams',
        'order': 1,
    },
    {
        'name': 'English Medium (Std 5 - A Level)',
        'slug': 'o-a-level',
        'icon': 'ph-certificate',
        'description': 'Classes for English Medium Cambridge and Edexcel syllabus',
        'order': 2,
    },
    {
        'name': 'Skills & Development',
        'slug': 'skills',
        'icon': 'ph-code',
        'description': 'Spoken English, programming, and technical skills',
        'order': 3,
    },
]

COURSES = [
    # ── ENGLISH VERSION: CLASS 5 - 8 ──────────────────────────────────────────
    {
        'title': 'EV Class 5 Math & Science Foundation',
        'slug': 'ev-class-5-math-science',
        'instructor': 'Muntasir Tasnim',
        'price': 1000,
        'duration_hours': 30,
        'badge_label': 'CLASS 5 (EV)',
        'badge_color': 'bg-primary',
        'category_slug': 'ssc-hsc',
        'is_featured': False,
        'description': 'Comprehensive foundational course covering the Class 5 primary curriculum for Mathematics and Science in English Version.',
        'assignments_count': 12,
        'exams_count': 3,
        'quizzes_count': 15,
        'outline': [
            'Chapter 1: Multiplications & Divisions (5 Lectures)',
            'Chapter 2: Mathematical Symbols & Fractions (6 Lectures)',
            'Chapter 3: Average & Percentages (5 Lectures)',
            'Chapter 4: Basic Geometry & Measurement (6 Lectures)',
            'Chapter 5: Matter, Energy & Environmental Science (8 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Mastering numbers and calculations',
            'Stage 2: Understanding fractions and decimals',
            'Stage 3: Exploring physical sciences and nature',
            'Stage 4: Final revision and mock assessments'
        ]
    },
    {
        'title': 'EV Class 6 Mathematics & Science',
        'slug': 'ev-class-6-math-science',
        'instructor': 'Samiha Chowdhury',
        'price': 1200,
        'duration_hours': 35,
        'badge_label': 'CLASS 6 (EV)',
        'badge_color': 'bg-primary',
        'category_slug': 'ssc-hsc',
        'is_featured': False,
        'description': 'Advanced guidance for Class 6 mathematics and science topics with simple visual explanations.',
        'assignments_count': 15,
        'exams_count': 4,
        'quizzes_count': 20,
        'outline': [
            'Chapter 1: Arithmetic & Rational Numbers (8 Lectures)',
            'Chapter 2: Algebra Basics - Variables & Coeffs (6 Lectures)',
            'Chapter 3: Geometry Fundamentals (5 Lectures)',
            'Chapter 4: Cell Structure & Living World (8 Lectures)',
            'Chapter 5: Matter & Mixtures (8 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Transitioning to algebraic math',
            'Stage 2: Understanding basic geometry concepts',
            'Stage 3: Deep dive into living plant & animal cells',
            'Stage 4: Experimental projects and exams'
        ]
    },
    {
        'title': 'EV Class 7 General Science & ICT',
        'slug': 'ev-class-7-science-ict',
        'instructor': 'Rezwan Ahmed',
        'price': 1300,
        'duration_hours': 40,
        'badge_label': 'CLASS 7 (EV)',
        'badge_color': 'bg-primary',
        'category_slug': 'ssc-hsc',
        'is_featured': False,
        'description': 'Interactive lessons for Class 7 General Science along with practical guidance on ICT topics.',
        'assignments_count': 18,
        'exams_count': 4,
        'quizzes_count': 22,
        'outline': [
            'Chapter 1: Lower Organisms - Virus, Bacteria (8 Lectures)',
            'Chapter 2: Internal Structure of Plants (6 Lectures)',
            'Chapter 3: Heat, Temperature & Energy (7 Lectures)',
            'Chapter 4: Introduction to ICT & Internet (8 Lectures)',
            'Chapter 5: Digital Safety & Operations (6 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Microbial organisms and bio-science',
            'Stage 2: Energy, heat, and basic physics equations',
            'Stage 3: Practical usage of computer applications',
            'Stage 4: Interactive term-end evaluation'
        ]
    },
    {
        'title': 'EV Class 8 Science & Mathematics Masterclass',
        'slug': 'ev-class-8-science-math-masterclass',
        'instructor': 'Nafis Imran',
        'price': 1500,
        'duration_hours': 45,
        'badge_label': 'CLASS 8 (EV)',
        'badge_color': 'bg-primary',
        'category_slug': 'ssc-hsc',
        'is_featured': False,
        'description': 'Strong base course for JSC/Class 8 math and science. Prepares students for SSC-level physics and chemistry.',
        'assignments_count': 20,
        'exams_count': 5,
        'quizzes_count': 25,
        'outline': [
            'Chapter 1: Pattern & Arithmetic (6 Lectures)',
            'Chapter 2: Sets, Algebraic Formulae & Equations (10 Lectures)',
            'Chapter 3: Animal Classification & Evolution (8 Lectures)',
            'Chapter 4: Acids, Bases & Salts (8 Lectures)',
            'Chapter 5: Light & Basic Electricity (8 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Solidifying advanced algebra and sets',
            'Stage 2: Chemistry basics - acids, bases, chemical reactions',
            'Stage 3: Physics basics - understanding light refraction',
            'Stage 4: Full board-style test series'
        ]
    },

    # ── ENGLISH VERSION: SSC (CLASS 9 - 10) ──────────────────────────────────
    {
        'title': 'SSC Higher Mathematics Masterclass',
        'slug': 'ssc-higher-math-masterclass',
        'instructor': 'Faria Rahman',
        'price': 2000,
        'duration_hours': 50,
        'badge_label': 'SSC BATCH',
        'badge_color': 'bg-accent1',
        'category_slug': 'ssc-hsc',
        'is_featured': True,
        'description': 'Master SSC Higher Math curriculum. Includes set theory, algebraic expressions, coordinate geometry, and trigonometry.',
        'assignments_count': 25,
        'exams_count': 6,
        'quizzes_count': 30,
        'outline': [
            'Chapter 1: Infinite Series & Sets (8 Lectures)',
            'Chapter 2: Algebraic Expressions (10 Lectures)',
            'Chapter 3: Geometry & Vector (10 Lectures)',
            'Chapter 4: Trigonometry & Coordinates (12 Lectures)',
            'Chapter 5: Probability (6 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Mastering set algebra and series expansions',
            'Stage 2: In-depth Coordinate Geometry graphing',
            'Stage 3: Visualizing vector geometry problems',
            'Stage 4: Live problem solving and 5 board standard mocks'
        ]
    },
    {
        'title': 'SSC Physics Intensive course',
        'slug': 'ssc-physics-intensive',
        'instructor': 'Tanvir Hossain',
        'price': 1800,
        'duration_hours': 48,
        'badge_label': 'SSC BATCH',
        'badge_color': 'bg-accent1',
        'category_slug': 'ssc-hsc',
        'is_featured': True,
        'description': 'Clear your conceptual gaps in mechanics, wave optics, electricity, and modern physics for SSC exam.',
        'assignments_count': 22,
        'exams_count': 5,
        'quizzes_count': 28,
        'outline': [
            'Chapter 1: Physical Quantities & Measurement (5 Lectures)',
            'Chapter 2: Motion, Force, Work, Power & Energy (12 Lectures)',
            'Chapter 3: State of Matter & Pressure (6 Lectures)',
            'Chapter 4: Waves & Sound, Refraction of Light (10 Lectures)',
            'Chapter 5: Current & Static Electricity (10 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Mechanics, velocity, acceleration, and Newton\'s laws',
            'Stage 2: Work, power, and wave energy mechanics',
            'Stage 3: Light refraction, mirrors, and electricity circuits',
            'Stage 4: Practical lab experiment setups and test papers'
        ]
    },
    {
        'title': 'SSC Chemistry Ultimate Prep',
        'slug': 'ssc-chemistry-prep',
        'instructor': 'Sadia Afrin',
        'price': 1800,
        'duration_hours': 46,
        'badge_label': 'SSC BATCH',
        'badge_color': 'bg-accent1',
        'category_slug': 'ssc-hsc',
        'is_featured': False,
        'description': 'Periodic table, chemical bonds, mineral resources, and organic chemistry simplified with practice sheets.',
        'assignments_count': 20,
        'exams_count': 5,
        'quizzes_count': 26,
        'outline': [
            'Chapter 1: Structure of Matter & Periodic Table (10 Lectures)',
            'Chapter 2: Chemical Bonds & Reactions (10 Lectures)',
            'Chapter 3: Concept of Mole & Chemical Calculations (8 Lectures)',
            'Chapter 4: Acid, Base & Salt balance (6 Lectures)',
            'Chapter 5: Organic Chemistry & Hydrocarbons (12 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Understanding atoms, elements, and atomic shells',
            'Stage 2: Balancing reactions and solving molarity calculations',
            'Stage 3: Hydrocarbon naming, reactions, and polymerizations',
            'Stage 4: MCQ tips and creative question solving'
        ]
    },

    # ── ENGLISH VERSION: HSC (CLASS 11 - 12) ──────────────────────────────────
    {
        'title': 'HSC Physics 1st Paper Complete',
        'slug': 'hsc-physics-1st-paper',
        'instructor': 'Kamrul Hasan',
        'price': 2500,
        'duration_hours': 60,
        'badge_label': 'HSC BATCH',
        'badge_color': 'bg-violet-600',
        'category_slug': 'ssc-hsc',
        'is_featured': True,
        'description': 'HSC Physics 1st Paper: Vectors, mechanics, projectile motion, gravitation, periodic motion, and thermodynamics.',
        'assignments_count': 30,
        'exams_count': 8,
        'quizzes_count': 40,
        'outline': [
            'Chapter 1: Vector Analysis (8 Lectures)',
            'Chapter 2: Newtonian Mechanics (12 Lectures)',
            'Chapter 3: Work, Energy & Power (8 Lectures)',
            'Chapter 4: Gravity & Gravitation (8 Lectures)',
            'Chapter 5: Ideal Gas & Kinetic Theory (10 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Mastering vector multiplication and application',
            'Stage 2: Newtonian mechanics - torque, rotational inertia',
            'Stage 3: Mechanical properties of matter and gas laws',
            'Stage 4: Solving past 10 years board questions and test paper preparation'
        ]
    },
    {
        'title': 'HSC Higher Mathematics (Paper 1 & 2)',
        'slug': 'hsc-higher-math',
        'instructor': 'Tahmid Ahmed',
        'price': 3000,
        'duration_hours': 75,
        'badge_label': 'HSC BATCH',
        'badge_color': 'bg-violet-600',
        'category_slug': 'ssc-hsc',
        'is_featured': True,
        'description': 'Mastering Matrix, Calculus (differentiation & integration), Conics, Complex Numbers, and Statics for HSC Board Exams.',
        'assignments_count': 35,
        'exams_count': 10,
        'quizzes_count': 45,
        'outline': [
            'Chapter 1: Matrices & Determinants (10 Lectures)',
            'Chapter 2: Calculus - Limit, Differentiation (15 Lectures)',
            'Chapter 3: Calculus - Integration & Areas (15 Lectures)',
            'Chapter 4: Complex Numbers & Conics (15 Lectures)',
            'Chapter 5: Statics & Dynamics (10 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Foundation of matrices and algebraic calculus limits',
            'Stage 2: Advanced derivatives and practical physics applications',
            'Stage 3: Definite integrals, conics equations, and complex geometry',
            'Stage 4: Statics/Dynamics forces resolution and final review mocks'
        ]
    },

    # ── ENGLISH MEDIUM: STANDARD 5 - 8 ───────────────────────────────────────
    {
        'title': 'EM Standard 5 Mathematics & Science',
        'slug': 'em-std-5-math-science',
        'instructor': 'Fabiha Bushra',
        'price': 1500,
        'duration_hours': 32,
        'badge_label': 'STD 5 (EM)',
        'badge_color': 'bg-secondary',
        'category_slug': 'o-a-level',
        'is_featured': False,
        'description': 'Core Cambridge curriculum preparation for Standard 5 students covering primary mathematics, biology, and chemistry basics.',
        'assignments_count': 15,
        'exams_count': 4,
        'quizzes_count': 18,
        'outline': [
            'Chapter 1: Number Systems & Place Value (6 Lectures)',
            'Chapter 2: Decimals, Fractions & Percentages (8 Lectures)',
            'Chapter 3: Animal Kingdoms & Habitats (6 Lectures)',
            'Chapter 4: States of Matter & Phase Changes (6 Lectures)',
            'Chapter 5: Light Reflection & Shadows (6 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Advanced decimal calculations',
            'Stage 2: Investigating habitats and food chains',
            'Stage 3: Investigating physical states and density properties',
            'Stage 4: Final standard term evaluations'
        ]
    },
    {
        'title': 'EM Standard 8 Science & Mathematics Masterclass',
        'slug': 'em-std-8-math-science',
        'instructor': 'Rezaul Karim',
        'price': 1800,
        'duration_hours': 42,
        'badge_label': 'STD 8 (EM)',
        'badge_color': 'bg-secondary',
        'category_slug': 'o-a-level',
        'is_featured': False,
        'description': 'Advanced course for Standard 8 Checkpoint exam preparation. Focuses on Cambridge Checkpoint past paper analysis.',
        'assignments_count': 22,
        'exams_count': 6,
        'quizzes_count': 24,
        'outline': [
            'Chapter 1: Linear Equations & Graphs (8 Lectures)',
            'Chapter 2: Ratios, Proportions & Pythagoras Theorem (8 Lectures)',
            'Chapter 3: Plants Photosynthesis & Transport (6 Lectures)',
            'Chapter 4: Chemical Periodic Table & Reactions (10 Lectures)',
            'Chapter 5: Speed, Force & Pressure Mechanics (8 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Mastering linear algebra coordinates and ratios',
            'Stage 2: Studying basic chemical element behaviors and periodic groups',
            'Stage 3: Energy, pressure, forces formulas',
            'Stage 4: Solve full Cambridge Checkpoint sample tests'
        ]
    },

    # ── ENGLISH MEDIUM: O LEVEL ──────────────────────────────────────────────
    {
        'title': 'O Level Mathematics (D)',
        'slug': 'o-level-math-d',
        'instructor': 'Sadman Sakib',
        'price': 4000,
        'duration_hours': 64,
        'badge_label': 'O LEVEL',
        'badge_color': 'bg-emerald-600',
        'category_slug': 'o-a-level',
        'is_featured': True,
        'description': 'Syllabus coverage of Cambridge O Level Mathematics D (4024). Includes algebra, mensuration, matrices, probability, and geometry.',
        'assignments_count': 28,
        'exams_count': 7,
        'quizzes_count': 32,
        'outline': [
            'Chapter 1: Number properties & Algebra (12 Lectures)',
            'Chapter 2: Trigonometry & Bearing (10 Lectures)',
            'Chapter 3: Vectors & Transformation Geometry (12 Lectures)',
            'Chapter 4: Probability & Statistics (8 Lectures)',
            'Chapter 5: Functions, Graphs & Calculus Intro (10 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Building a foundation in algebra and geometry properties',
            'Stage 2: Complex trigonometry heights, bearings, and non-right angles',
            'Stage 3: Vector matrices and transformation matrices rules',
            'Stage 4: Past paper 1 & 2 full solution sprint'
        ]
    },
    {
        'title': 'O Level Chemistry CIE',
        'slug': 'o-level-chemistry-cie',
        'instructor': 'Dr. Zafar Iqbal',
        'price': 4000,
        'duration_hours': 56,
        'badge_label': 'O LEVEL',
        'badge_color': 'bg-emerald-600',
        'category_slug': 'o-a-level',
        'is_featured': True,
        'description': 'Comprehensive O Level Chemistry (5070/0971) coverage. Stoichiometry, electrolysis, organic chemistry, and chemical analysis.',
        'assignments_count': 25,
        'exams_count': 6,
        'quizzes_count': 30,
        'outline': [
            'Chapter 1: Kinetic Particle Theory & Separation (6 Lectures)',
            'Chapter 2: Atoms, Elements, Compounds & Bondings (10 Lectures)',
            'Chapter 3: Stoichiometry & Electrolysis (10 Lectures)',
            'Chapter 4: Energy Changes & Reaction Kinetics (8 Lectures)',
            'Chapter 5: Organic Chemistry & Polymers (12 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Mastery of atomic structures and electronic bonding rules',
            'Stage 2: Advanced moles, calculations, gas laws and equations',
            'Stage 3: Alkanes, alkenes, alcohols, carboxylic acids, esters, and polycondensations',
            'Stage 4: Practical ATP (Alternative to Practical) prep and full mock papers'
        ]
    },
    {
        'title': 'O Level Physics Intensive',
        'slug': 'o-level-physics-intensive',
        'instructor': 'Ahsan Habib',
        'price': 4000,
        'duration_hours': 58,
        'badge_label': 'O LEVEL',
        'badge_color': 'bg-emerald-600',
        'category_slug': 'o-a-level',
        'is_featured': False,
        'description': 'Complete revision of Mechanics, Thermal Physics, Light & Waves, Magnetism, Electricity, and Space Physics.',
        'assignments_count': 26,
        'exams_count': 6,
        'quizzes_count': 28,
        'outline': [
            'Chapter 1: General Mechanics & Forces (12 Lectures)',
            'Chapter 2: Thermal Physics & Gas laws (8 Lectures)',
            'Chapter 3: Wave Properties & Sound/Light optics (10 Lectures)',
            'Chapter 4: Magnetism, Static & Current Electricity (12 Lectures)',
            'Chapter 5: Space Physics & Radioactivity (6 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Mastering forces, moments, momentum, and mechanics equations',
            'Stage 2: Understanding electromagnetic spectrum, mirrors, and logic gates',
            'Stage 3: Radioactivity half-lives and space physics models',
            'Stage 4: Solving paper 1, 2, and 4 (ATP) papers'
        ]
    },

    # ── ENGLISH MEDIUM: A LEVEL ──────────────────────────────────────────────
    {
        'title': 'A Level Pure Mathematics (P1–P4)',
        'slug': 'a-level-pure-math',
        'instructor': 'Tahmid Ahmed',
        'price': 6000,
        'duration_hours': 80,
        'badge_label': 'A LEVEL',
        'badge_color': 'bg-pink-500',
        'category_slug': 'o-a-level',
        'is_featured': True,
        'description': 'Comprehensive AS & A2 Pure Mathematics modules (9709). Vectors, parametric equations, integrations by parts/substitution, complex numbers.',
        'assignments_count': 40,
        'exams_count': 10,
        'quizzes_count': 50,
        'outline': [
            'Chapter 1: P1 Quadratic, Functions & Coordinate geometry (15 Lectures)',
            'Chapter 2: P1 Differentiation, Integration & Trigonometry (15 Lectures)',
            'Chapter 3: P3 Parametric, Exponential & Numerical (15 Lectures)',
            'Chapter 4: P3 Advanced Calculus & Differential Equations (20 Lectures)',
            'Chapter 5: P3 Complex Numbers & Vectors (15 Lectures)'
        ],
        'roadmap': [
            'Stage 1: solidifying quadratic functions and coordinate systems',
            'Stage 2: Mastering chain, product, and quotient rules of derivatives',
            'Stage 3: Advanced double-angle integrations and vectors in 3D',
            'Stage 4: Final AS + A2 exam drills and test sprints'
        ]
    },
    {
        'title': 'A Level Physics Complete',
        'slug': 'a-level-physics',
        'instructor': 'Dr. S. M. Kabir',
        'price': 6000,
        'duration_hours': 75,
        'badge_label': 'A LEVEL',
        'badge_color': 'bg-pink-500',
        'category_slug': 'o-a-level',
        'is_featured': True,
        'description': 'Advanced physics covering mechanics, materials, waves, fields, quantum physics, medical physics, and nuclear structures.',
        'assignments_count': 35,
        'exams_count': 8,
        'quizzes_count': 45,
        'outline': [
            'Chapter 1: AS Physical Quantities, Kinematics & Forces (15 Lectures)',
            'Chapter 2: AS Wave mechanics & Superposition (10 Lectures)',
            'Chapter 3: A2 Circular Motion & Gravitational Fields (12 Lectures)',
            'Chapter 4: A2 Charged Fields, Capacitance & Induction (15 Lectures)',
            'Chapter 5: A2 Quantum, Nuclear & Astrophysics (15 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Particle mechanics, momentum vectors and projectile calculus',
            'Stage 2: Wave interference patterns and AS theory exams',
            'Stage 3: Circular motion dynamics, magnetic flux density equations',
            'Stage 4: Solving A2 paper 4 structure and paper 5 analysis data'
        ]
    },

    # ── SKILL DEVELOPMENT ────────────────────────────────────────────────────
    {
        'title': 'Fullstack Web Development (React & Django)',
        'slug': 'fullstack-web-development-react-django',
        'instructor': 'Anika Rahman',
        'price': 5000,
        'duration_hours': 65,
        'badge_label': 'SKILLS',
        'badge_color': 'bg-accent2',
        'category_slug': 'skills',
        'is_featured': True,
        'description': 'Complete roadmap from HTML/CSS to React frontends and Django REST Framework backends. Build production apps.',
        'assignments_count': 25,
        'exams_count': 5,
        'quizzes_count': 30,
        'outline': [
            'Chapter 1: Modern HTML5, CSS3 & Tailwind CSS (10 Lectures)',
            'Chapter 2: JS ES6+ Fundamentals & DOM Manipulation (12 Lectures)',
            'Chapter 3: React Router, State Management & Tailwind UI (15 Lectures)',
            'Chapter 4: Python OOP & Django REST API Architecture (15 Lectures)',
            'Chapter 5: Database migrations, deployment, and testing (8 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Styling responsive modern static user interfaces',
            'Stage 2: Writing logic in ES6 Javascript and DOM elements',
            'Stage 3: Building complex component frameworks in React',
            'Stage 4: Connecting React to Django REST endpoint sessions and launching'
        ]
    },
    {
        'title': 'Spoken English Pro Masterclass',
        'slug': 'spoken-english-pro-masterclass',
        'instructor': 'Sabrina Khan',
        'price': 1500,
        'duration_hours': 30,
        'badge_label': 'SPOKEN',
        'badge_color': 'bg-amber-500',
        'category_slug': 'skills',
        'is_featured': False,
        'description': 'Fast-track spoken fluency course. Covers pronunciation, formal vs informal speech, vocabulary lists, and situational conversations.',
        'assignments_count': 15,
        'exams_count': 3,
        'quizzes_count': 20,
        'outline': [
            'Chapter 1: IPA Symbols & Basic Pronunciation (6 Lectures)',
            'Chapter 2: Essential Vocabulary & Daily Phrases (6 Lectures)',
            'Chapter 3: Grammar rules for active speaking (6 Lectures)',
            'Chapter 4: Professional communication & Interview etiquette (6 Lectures)',
            'Chapter 5: Group discussions & interactive peer speaks (6 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Removing pronunciation hesitation',
            'Stage 2: Building confidence in casual speaking scenarios',
            'Stage 3: Mastering formal and corporate dialogue presentation',
            'Stage 4: Continuous feedback and mock speaking tests'
        ]
    },
    {
        'title': 'English Foundation & Grammar Core',
        'slug': 'english-foundation-grammar',
        'instructor': 'Mirza Nabil',
        'price': 1200,
        'duration_hours': 28,
        'badge_label': 'GRAMMAR',
        'badge_color': 'bg-amber-500',
        'category_slug': 'skills',
        'is_featured': False,
        'description': 'Develop a strong grasp of basic English grammar, sentence structures, parts of speech, and writing styles for academic or corporate environments.',
        'assignments_count': 12,
        'exams_count': 4,
        'quizzes_count': 25,
        'outline': [
            'Chapter 1: Nouns, Pronouns & Verbs in Context (6 Lectures)',
            'Chapter 2: Tenses & Sentence structures (8 Lectures)',
            'Chapter 3: Direct vs Indirect Speech & Voices (6 Lectures)',
            'Chapter 4: Paragraph & Letter writing (5 Lectures)',
            'Chapter 5: Sentence correction practice (5 Lectures)'
        ],
        'roadmap': [
            'Stage 1: Tense rules absolute alignment',
            'Stage 2: Voice changes and sentence modification rules',
            'Stage 3: Advanced spelling and error correction systems',
            'Stage 4: Writing essays and scoring check exams'
        ]
    }
]

class Command(BaseCommand):
    help = 'Seed the database with sample categories, courses, and a demo user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Course.objects.all().delete()
            Category.objects.all().delete()

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding TutorBhaiya database...'))

        # ── Categories ────────────────────────────────────────────────────────
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            cat_map[cat.slug] = cat
            action = 'Created' if created else 'Exists'
            self.stdout.write(f'  {action} category: {cat.name}')

        # ── Courses ───────────────────────────────────────────────────────────
        for course_data in COURSES:
            cat_slug = course_data.pop('category_slug')
            category = cat_map.get(cat_slug)
            
            # Ensure outline and roadmap are list types (JSON)
            course, created = Course.objects.get_or_create(
                slug=course_data['slug'],
                defaults={**course_data, 'category': category}
            )
            action = 'Created' if created else 'Exists'
            self.stdout.write(f'  {action} course: {course.title}')

        # ── Demo User ─────────────────────────────────────────────────────────
        demo_email = 'demo@tutorbhaiya.com'
        if not User.objects.filter(email=demo_email).exists():
            User.objects.create_user(
                username='demo',
                email=demo_email,
                password='demo1234',
                first_name='Demo',
                last_name='Student',
            )
            self.stdout.write(f'  Created demo user: {demo_email} / demo1234')
        else:
            self.stdout.write(f'  Demo user already exists: {demo_email}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed complete!'))
