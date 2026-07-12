
const API_BASE = 'https://tutor-bhaiya.onrender.com/api';

document.addEventListener('DOMContentLoaded', () => {
    const courseGrid = document.getElementById('course-grid');
    const buttons = document.querySelectorAll('.filter-btn');

    // Check auth state to customize header navbar
    const userStr = localStorage.getItem('user');
    const isLoggedIn = !!userStr;

    // Update navbars (desktop + mobile) to reflect auth state
    const navActions = document.querySelector('#navbar .hidden.md\\:flex.items-center.space-x-4');
    if (navActions) {
        const dashboardLink = navActions.querySelector('a[href="dashboard.html"]');
        const loginLink = navActions.querySelector('a[href="login.html"]');
        if (isLoggedIn) {
            if (dashboardLink) dashboardLink.style.display = 'inline-block';
            if (loginLink) loginLink.style.display = 'none';
        } else {
            if (dashboardLink) dashboardLink.style.display = 'none';
            if (loginLink) loginLink.style.display = 'inline-block';
        }
    }

    // Mobile menu logic
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            mobileMenu.classList.toggle('hidden');
        });
        document.addEventListener('click', () => {
            if (!mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.add('hidden');
            }
        });
        mobileMenu.addEventListener('click', (e) => e.stopPropagation());
    }

    // Sub-filter configuration mapping
    const SUB_FILTER_CONFIGS = {
        'ssc-hsc': [
            { label: 'All English Version', value: 'all-ev' },
            { label: 'Class 5', value: 'class-5' },
            { label: 'Class 6', value: 'class-6' },
            { label: 'Class 7', value: 'class-7' },
            { label: 'Class 8', value: 'class-8' },
            { label: 'Class 9', value: 'class-9' },
            { label: 'SSC Batch', value: 'ssc-batch' },
            { label: 'HSC Batch', value: 'hsc-batch' }
        ],
        'o-a-level': [
            { label: 'All English Medium', value: 'all-em' },
            { label: 'Standard 5', value: 'standard-5' },
            { label: 'Standard 6', value: 'standard-6' },
            { label: 'Standard 7', value: 'standard-7' },
            { label: 'Standard 8', value: 'standard-8' },
            { label: 'O Level', value: 'o-level' },
            { label: 'A Level', value: 'a-level' }
        ],
        'skills': [
            { label: 'All Skills', value: 'all-skills' },
            { label: 'Spoken English', value: 'spoken-english' },
            { label: 'English Foundation', value: 'english-foundation' }
        ]
    };

    const PARAM_MAPPING = {
        'class-5': { primary: 'ssc-hsc', sub: 'class-5', match: (badge) => badge.includes('CLASS 5') },
        'class-6': { primary: 'ssc-hsc', sub: 'class-6', match: (badge) => badge.includes('CLASS 6') },
        'class-7': { primary: 'ssc-hsc', sub: 'class-7', match: (badge) => badge.includes('CLASS 7') },
        'class-8': { primary: 'ssc-hsc', sub: 'class-8', match: (badge) => badge.includes('CLASS 8') },
        'class-9': { primary: 'ssc-hsc', sub: 'ssc-batch', match: (badge) => badge.includes('SSC BATCH') }, // default fallback to SSC
        'ssc-batch': { primary: 'ssc-hsc', sub: 'ssc-batch', match: (badge) => badge.includes('SSC BATCH') },
        'hsc-batch': { primary: 'ssc-hsc', sub: 'hsc-batch', match: (badge) => badge.includes('HSC BATCH') },
        'ssc-hsc': { primary: 'ssc-hsc', sub: 'all-ev', match: () => true },
        'all-ev': { primary: 'ssc-hsc', sub: 'all-ev', match: () => true },

        'standard-5': { primary: 'o-a-level', sub: 'standard-5', match: (badge) => badge.includes('STD 5') },
        'standard-6': { primary: 'o-a-level', sub: 'standard-6', match: (badge) => badge.includes('STD 6') },
        'standard-7': { primary: 'o-a-level', sub: 'standard-7', match: (badge) => badge.includes('STD 7') },
        'standard-8': { primary: 'o-a-level', sub: 'standard-8', match: (badge) => badge.includes('STD 8') },
        'o-level': { primary: 'o-a-level', sub: 'o-level', match: (badge) => badge.includes('O LEVEL') },
        'a-level': { primary: 'o-a-level', sub: 'a-level', match: (badge) => badge.includes('A LEVEL') },
        'o-a-level': { primary: 'o-a-level', sub: 'all-em', match: () => true },
        'all-em': { primary: 'o-a-level', sub: 'all-em', match: () => true },

        'spoken-english': { primary: 'skills', sub: 'spoken-english', match: (badge) => badge.includes('SPOKEN') },
        'english-foundation': { primary: 'skills', sub: 'english-foundation', match: (badge) => badge.includes('GRAMMAR') },
        'skills': { primary: 'skills', sub: 'all-skills', match: () => true },
        'all-skills': { primary: 'skills', sub: 'all-skills', match: () => true }
    };

    // Fetch and render courses
    async function fetchCourses(category = 'all', subCategoryVal = null) {
        courseGrid.innerHTML = `
                    <div class="col-span-full text-center py-12 text-gray-500">
                        Loading courses...
                    </div>
                `;

        try {
            let url = `${API_BASE}/courses/`;
            if (category !== 'all') {
                url += `?category=${category}`;
            }

            const res = await fetch(url);
            const courses = await res.json();

            // Apply local sub-filtering if applicable
            let filteredCourses = courses;
            if (subCategoryVal && PARAM_MAPPING[subCategoryVal]) {
                const matcher = PARAM_MAPPING[subCategoryVal].match;
                filteredCourses = courses.filter(course => matcher(course.badge_label || ''));
            }

            if (filteredCourses.length === 0) {
                courseGrid.innerHTML = `
                            <div class="col-span-full text-center py-12 text-gray-500">
                                No courses found matching this selection.
                            </div>
                        `;
                return;
            }

            courseGrid.innerHTML = '';
            filteredCourses.forEach(course => {
                const card = document.createElement('div');
                card.className = 'bg-white rounded-2xl overflow-hidden border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group course-card cursor-pointer';
                card.setAttribute('data-category', course.category_slug);
                card.onclick = () => showCourseDetails(course.slug);

                const thumbnail = course.thumbnail_url || 'assets/course1.jpg';

                card.innerHTML = `
                            <div class="h-48 relative overflow-hidden">
                                <img src="${thumbnail}" alt="${course.title}" class="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity group-hover:scale-105 duration-500">
                                <div class="absolute top-4 left-4 ${course.badge_color || 'bg-primary'} text-white text-xs font-bold px-3 py-1 rounded-full shadow-md">${course.badge_label || 'COURSE'}</div>
                            </div>
                            <div class="p-6">
                                <h3 class="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary transition-colors">${course.title}</h3>
                                <div class="flex items-center gap-3 text-gray-500 text-sm mb-6">
                                    <div class="flex items-center gap-1"><i class="ph ph-user"></i> ${course.instructor}</div>
                                    <div class="flex items-center gap-1"><i class="ph ph-clock"></i> ${course.duration_hours} Hrs</div>
                                </div>
                                <div class="flex items-center justify-between border-t border-gray-100 pt-4">
                                    <span class="text-lg font-bold text-gray-900">৳${parseInt(course.price)}</span>
                                    <button onclick="event.stopPropagation(); enrollInCourse(${course.id})" class="enroll-btn bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-primary transition-colors">
                                        Enroll Now
                                    </button>
                                </div>
                            </div>
                        `;
                courseGrid.appendChild(card);
            });
        } catch (err) {
            console.error(err);
            courseGrid.innerHTML = `
                        <div class="col-span-full text-center py-12 text-red-500">
                            Failed to connect to database server. Please ensure the backend is running.
                        </div>
                    `;
        }
    }

    // Render sub-filter badges row
    function renderSubFilters(primaryCategory, activeSubVal = null) {
        const subFilterRow = document.getElementById('sub-filter-buttons');
        subFilterRow.innerHTML = '';

        if (SUB_FILTER_CONFIGS[primaryCategory]) {
            subFilterRow.classList.remove('hidden');
            const configs = SUB_FILTER_CONFIGS[primaryCategory];

            configs.forEach(cfg => {
                const btn = document.createElement('button');
                btn.className = 'px-4 py-1.5 rounded-full text-xs font-semibold border transition-all duration-300';
                btn.textContent = cfg.label;

                const isActive = (activeSubVal === cfg.value) || (!activeSubVal && cfg.value.startsWith('all-'));
                if (isActive) {
                    btn.className += ' bg-primary text-white border-primary shadow-sm';
                } else {
                    btn.className += ' bg-white border-slate-200 text-slate-600 hover:bg-slate-50';
                }

                btn.onclick = () => {
                    // Update active state in URL
                    const url = new URL(window.location);
                    url.searchParams.set('filter', cfg.value);
                    window.history.pushState({}, '', url);

                    // Re-render sub filters highlight
                    renderSubFilters(primaryCategory, cfg.value);

                    // Load courses
                    fetchCourses(primaryCategory, cfg.value);
                };
                subFilterRow.appendChild(btn);
            });
        } else {
            subFilterRow.classList.add('hidden');
        }
    }

    // Show Course Details Modal
    window.showCourseDetails = async function (slug) {
        const modal = document.getElementById('course-modal');
        try {
            const res = await fetch(`${API_BASE}/courses/${slug}/`);
            const course = await res.json();

            if (!res.ok) throw new Error('Error loading course details');

            // Bind details to elements
            document.getElementById('modal-title').textContent = course.title;
            document.getElementById('modal-description').textContent = course.description || 'No description available.';
            document.getElementById('modal-instructor').textContent = course.instructor;
            document.getElementById('modal-duration').textContent = `${course.duration_hours} Hrs`;
            document.getElementById('modal-price').textContent = `৳${parseInt(course.price)}`;
            document.getElementById('modal-image').src = course.thumbnail_url || 'assets/course1.jpg';

            const badge = document.getElementById('modal-badge');
            badge.textContent = course.badge_label || 'COURSE';
            badge.className = `text-xs font-bold text-white px-2 py-1 rounded-md mb-2 inline-block ${course.badge_color || 'bg-primary'}`;

            // Update Assignments, Exams, Quizzes Counts
            document.getElementById('modal-assignments-count').textContent = course.assignments_count || 0;
            document.getElementById('modal-exams-count').textContent = course.exams_count || 0;
            document.getElementById('modal-quizzes-count').textContent = course.quizzes_count || 0;

            // Hydrate Outline List
            const outlineList = document.getElementById('modal-outline-list');
            outlineList.innerHTML = '';
            if (course.outline && course.outline.length > 0) {
                course.outline.forEach(item => {
                    const li = document.createElement('li');
                    li.className = 'flex items-start gap-2 py-1 border-b border-slate-50 last:border-b-0';
                    li.innerHTML = `<i class="ph ph-check-circle text-secondary mt-0.5 text-base"></i> <span>${item}</span>`;
                    outlineList.appendChild(li);
                });
            } else {
                outlineList.innerHTML = '<li class="text-slate-400 italic">No outline modules defined.</li>';
            }

            // Hydrate Roadmap Timeline
            const roadmapTimeline = document.getElementById('modal-roadmap-timeline');
            roadmapTimeline.innerHTML = '';
            if (course.roadmap && course.roadmap.length > 0) {
                course.roadmap.forEach((stage, idx) => {
                    const milestone = document.createElement('div');
                    milestone.className = 'relative pl-2';
                    milestone.innerHTML = `
                                <div class="absolute -left-[31px] top-1 w-4.5 h-4.5 rounded-full border-4 border-white bg-primary flex items-center justify-center text-[10px] text-white font-bold shadow-sm"></div>
                                <h5 class="font-bold text-slate-800">Stage ${idx + 1}</h5>
                                <p class="text-xs text-slate-500 mt-0.5">${stage}</p>
                            `;
                    roadmapTimeline.appendChild(milestone);
                });
            } else {
                roadmapTimeline.innerHTML = '<div class="text-slate-400 italic">No roadmap defined for this course.</div>';
            }

            // Bind Enroll Action to button inside modal
            const enrollBtn = document.getElementById('modal-enroll-btn');
            enrollBtn.onclick = () => enrollInCourse(course.id);

            // Show Modal
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        } catch (err) {
            console.error(err);
            alert('Error loading course details.');
        }
    };

    // Close Course Details Modal
    window.closeCourseModal = function () {
        const modal = document.getElementById('course-modal');
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    };

    // Close modal when clicking background
    document.getElementById('course-modal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('course-modal')) {
            closeCourseModal();
        }
    });

    let currentEnrollCourseId = null;

    // Enroll Functionality (Now opens bKash modal)
    window.enrollInCourse = async function (courseId) {
        if (!isLoggedIn) {
            window.location.href = 'login.html';
            return;
        }

        try {
            // Fetch course details to get the price
            const res = await fetch(`${API_BASE}/courses/`);
            const courses = await res.json();
            const course = courses.find(c => c.id === courseId) || (await (await fetch(`${API_BASE}/courses/${courseId}/`)).json()); // Fallback to details if not in grid

            if (!course) {
                alert('Course not found.');
                return;
            }

            currentEnrollCourseId = courseId;

            // Setup bKash Modal
            document.getElementById('bkash-amount').textContent = `৳${parseInt(course.price)}`;
            document.getElementById('bkash-account').value = '';
            document.getElementById('bkash-pin').value = '';

            const confirmBtn = document.getElementById('bkash-confirm-btn');
            confirmBtn.innerHTML = '<span>Confirm</span>';
            confirmBtn.disabled = false;
            confirmBtn.className = 'flex-1 py-3 rounded-xl bg-[#e2136e] hover:bg-[#c4105f] text-white font-bold text-sm transition-all shadow-lg shadow-[#e2136e]/30 hover:shadow-[#e2136e]/50 flex justify-center items-center gap-2';

            // Hide course details modal if open, but keep overflow hidden
            document.getElementById('course-modal').classList.add('hidden');

            const bkashModal = document.getElementById('bkash-modal');
            bkashModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        } catch (err) {
            console.error(err);
            alert('Error preparing payment gateway.');
        }
    };

    window.closeBkashModal = function () {
        document.getElementById('bkash-modal').classList.add('hidden');
        document.body.style.overflow = '';
    };

    // Handle bKash Confirmation
    document.getElementById('bkash-confirm-btn').addEventListener('click', async function () {
        const account = document.getElementById('bkash-account').value;
        const pin = document.getElementById('bkash-pin').value;

        if (!account || account.length < 11) {
            alert('Please enter a valid 11-digit bKash account number.');
            return;
        }
        if (!pin || pin.length < 4) {
            alert('Please enter a valid PIN.');
            return;
        }

        const btn = this;
        btn.disabled = true;
        btn.innerHTML = '<i class="ph ph-spinner animate-spin text-lg"></i> Processing...';

        // Simulate network payment delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Proceed to enroll user on backend
        try {
            const csrfRes = await fetch(`${API_BASE}/csrf/`);
            const { csrfToken } = await csrfRes.json();

            const res = await fetch(`${API_BASE}/enrollments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ course_id: currentEnrollCourseId }),
                credentials: 'include'
            });

            if (res.ok) {
                btn.innerHTML = '<i class="ph ph-check-circle text-lg"></i> Success!';
                btn.className = 'flex-1 py-3 rounded-xl bg-secondary hover:bg-emerald-600 text-white font-bold text-sm transition-all shadow-lg shadow-secondary/30 flex justify-center items-center gap-2';

                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1200);
            } else {
                const errData = await res.json();
                alert(errData.error || 'Payment succeeded but failed to enroll. Please contact support.');
                btn.disabled = false;
                btn.innerHTML = '<span>Confirm</span>';
            }
        } catch (err) {
            console.error(err);
            alert('Error communicating with the enrollment server.');
            btn.disabled = false;
            btn.innerHTML = '<span>Confirm</span>';
        }
    });

    // Filter button click events
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');

            // Update URL filter search param
            const url = new URL(window.location);
            url.searchParams.set('filter', target);
            window.history.pushState({}, '', url);

            // Update active button classes
            buttons.forEach(b => {
                if (b === btn) {
                    b.classList.add('bg-primary', 'text-white');
                    b.classList.remove('bg-white', 'text-gray-600');
                } else {
                    b.classList.remove('bg-primary', 'text-white');
                    b.classList.add('bg-white', 'text-gray-600');
                }
            });

            renderSubFilters(target, null);
            fetchCourses(target, null);
        });
    });

    // Initial load from URL search param
    const urlParams = new URLSearchParams(window.location.search);
    const filterParam = urlParams.get('filter') || 'all';

    // Resolve filters
    let activePrimary = 'all';
    let activeSub = null;
    if (PARAM_MAPPING[filterParam]) {
        activePrimary = PARAM_MAPPING[filterParam].primary;
        activeSub = PARAM_MAPPING[filterParam].sub;
    } else {
        activePrimary = filterParam;
    }

    // Highlighting the initial active filter button
    buttons.forEach(btn => {
        if (btn.getAttribute('data-target') === activePrimary) {
            btn.classList.add('bg-primary', 'text-white');
            btn.classList.remove('bg-white', 'text-gray-600');
        } else {
            btn.classList.remove('bg-primary', 'text-white');
            btn.classList.add('bg-white', 'text-gray-600');
        }
    });

    // Render sub-filters and fetch courses
    renderSubFilters(activePrimary, activeSub);
    fetchCourses(activePrimary, activeSub);
});
