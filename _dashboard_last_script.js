
        if (!isLoggedIn()) {
            window.location.href = 'login.html';
        }

        let currentUser = getUser();
        let currentQuizId = null;

        // ── 1. SIDEBAR BUILDER ACCORDING TO ROLE ───────────────────────────────
        function buildSidebarNav(role) {
            const container = document.getElementById('sidebar-nav-links');
            let links = [];

            if (role === 'admin') {
                links = [
                    { id: 'dashboard', icon: 'ph-shield-check', label: 'Admin Overview' },
                    { id: 'notifications', icon: 'ph-bell', label: 'Notifications' },
                    { id: 'admin-courses', icon: 'ph-books', label: 'Courses & Teachers' },
                    { id: 'admin-teachers', icon: 'ph-user-list', label: 'Teacher Activity Monitor' },
                    { id: 'admin-submissions', icon: 'ph-file-text', label: 'Platform Submissions' },
                    { id: 'admin-users-list', icon: 'ph-users-three', label: 'User Management' },
                    { id: 'leaderboard', icon: 'ph-trophy', label: 'Leaderboard' }
                ];
            } else if (role === 'teacher') {
                links = [
                    { id: 'dashboard', icon: 'ph-chart-line-up', label: 'Teacher Overview' },
                    { id: 'notifications', icon: 'ph-bell', label: 'Notifications' },
                    { id: 'teacher-uploads', icon: 'ph-upload-simple', label: 'Work & Content Uploads' },
                    { id: 'teacher-grading', icon: 'ph-checks', label: 'Student Submissions' },
                    { id: 'quiz-builder', icon: 'ph-question', label: 'Quiz Builder' },
                    { id: 'teacher-live', icon: 'ph-video-camera', label: 'Live Classes' },
                    { id: 'my-courses', icon: 'ph-play-circle', label: 'My Taught Courses' },
                    { id: 'leaderboard', icon: 'ph-trophy', label: 'Leaderboard' }
                ];
            } else {
                // Student
                links = [
                    { id: 'dashboard', icon: 'ph-squares-four', label: 'Dashboard' },
                    { id: 'notifications', icon: 'ph-bell', label: 'Notifications' },
                    { id: 'my-courses', icon: 'ph-play-circle', label: 'My Courses' },
                    { id: 'exams', icon: 'ph-exam', label: 'Exams & Quizzes' },
                    { id: 'student-live', icon: 'ph-video-camera', label: 'Live Classes' },
                    { id: 'certificates', icon: 'ph-certificate', label: 'Certificates' },
                    { id: 'leaderboard', icon: 'ph-trophy', label: 'Leaderboard' }
                ];
            }

            container.innerHTML = links.map((link, idx) => `
                <a href="#" class="sidebar-link ${idx === 0 ? 'active bg-white/10 text-primary' : 'text-gray-400 hover:bg-white/5 hover:text-white'} flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors" data-target="${link.id}">
                    <i class="ph ${link.icon} text-xl"></i> ${link.label}
                </a>
            `).join('');

            // Attach click listeners to newly rendered sidebar links
            document.querySelectorAll('.sidebar-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    document.querySelectorAll('.sidebar-link').forEach(l => {
                        l.classList.remove('bg-white/10', 'text-primary');
                        l.classList.add('text-gray-400', 'hover:bg-white/5', 'hover:text-white');
                    });
                    document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));

                    link.classList.add('bg-white/10', 'text-primary');
                    link.classList.remove('text-gray-400', 'hover:bg-white/5', 'hover:text-white');

                    const target = link.getAttribute('data-target');
                    const targetSec = document.getElementById(`section-${target}`);
                    if (targetSec) targetSec.classList.remove('hidden');

                    // Trigger section loader
                    if (target === 'notifications') loadNotifications();
                    if (target === 'my-courses') loadMyCourses();
                    if (target === 'exams') loadQuizzes();
                    if (target === 'certificates') loadCertificates();
                    if (target === 'leaderboard') loadLeaderboard();
                    if (target === 'teacher-uploads') populateCourseSelects();
                    if (target === 'teacher-grading') loadTeacherSubmissions();
                    if (target === 'quiz-builder') populateCourseSelects();
                    if (target === 'admin-teachers') loadAdminTeacherActivity();
                    if (target === 'admin-submissions') loadAdminSubmissions();
                    if (target === 'teacher-live') loadTeacherLive();
                    if (target === 'student-live') loadStudentLive();
                    if (target === 'admin-courses') loadAdminCourses();
                    if (target === 'admin-users-list') loadAdminUsersList();
                });
            });
        }

        // ── 2. DASHBOARD DATA LOADER ───────────────────────────────────────────
        async function loadDashboard() {
            try {
                const res = await authFetch(`${API_BASE}/auth/me/`);
                if (res.status === 401) { 
                    clearAuth(); 
                    window.location.href = 'login.html'; 
                    return; 
                }
                if (!res.ok) {
                    throw new Error(`Failed to fetch user: ${res.status} ${res.statusText}`);
                }
                const meData = await res.json();
                if (!meData.user) {
                    throw new Error('Invalid response: missing user data');
                }
                currentUser = meData.user;
                localStorage.setItem('user', JSON.stringify(currentUser));

                // Update Header
                const role = currentUser.role || 'student';
                document.getElementById('welcome-msg').textContent = `Welcome back, ${currentUser.full_name}!`;
                document.getElementById('user-email-subtitle').textContent = `${currentUser.email} • ${role.toUpperCase()} Account`;
                const badge = document.getElementById('role-badge');
                badge.textContent = role.toUpperCase();
                if (role === 'admin') badge.className = 'badge-role bg-red-100 text-red-800 px-2.5 py-0.5 rounded-full';
                else if (role === 'teacher') badge.className = 'badge-role bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full';
                else badge.className = 'badge-role bg-violet-100 text-violet-800 px-2.5 py-0.5 rounded-full';

                const avatarEl = document.getElementById('avatar-placeholder');
                avatarEl.textContent = currentUser.avatar_initial || (currentUser.full_name ? currentUser.full_name[0] : 'U');

                buildSidebarNav(role);
                try { loadNotifications(); } catch (e) { console.error('Notification load error:', e); }

                // Render Overview stats based on role
                if (role === 'admin') {
                    loadAdminOverviewStats();
                } else if (role === 'teacher') {
                    loadTeacherOverviewStats();
                } else {
                    loadStudentOverviewStats();
                }

            } catch (err) {
                console.error('Dashboard initialization error:', err);
                const grid = document.getElementById('overview-stats-grid');
                if (grid) {
                    grid.innerHTML = `
                        <div class="col-span-full bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
                            <p class="text-red-600 font-semibold text-sm">Failed to load dashboard</p>
                            <p class="text-red-500 text-xs mt-1">${err.message}</p>
                            <p class="text-red-400 text-xs mt-2">Check browser console (F12) for more details</p>
                            <button onclick="location.reload()" class="mt-3 bg-red-500 hover:bg-red-600 text-white text-xs font-bold px-4 py-2 rounded-lg">Reload Page</button>
                        </div>`;
                }
            }
        }

        // ── STUDENT OVERVIEW ──────────────────────────────────────────────────
        async function loadStudentOverviewStats() {
            const grid = document.getElementById('overview-stats-grid');
            try {
                const res = await authFetch(`${API_BASE}/dashboard/`);
                if (!res.ok) {
                    throw new Error(`API error: ${res.status}`);
                }
                const data = await res.json();

                if (!data.stats) {
                    throw new Error('Invalid response format: missing stats');
                }

                grid.innerHTML = `
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-500 text-xl"><i class="ph-fill ph-book-open"></i></div>
                        <div><p class="text-xs text-gray-500 font-medium">Active Courses</p><h3 class="text-xl font-bold text-gray-900">${data.stats.active_courses || 0}</h3></div>
                    </div>
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-500 text-xl"><i class="ph-fill ph-check-circle"></i></div>
                        <div><p class="text-xs text-gray-500 font-medium">Completed Courses</p><h3 class="text-xl font-bold text-gray-900">${data.stats.completed_courses || 0}</h3></div>
                    </div>
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-500 text-xl"><i class="ph-fill ph-trophy"></i></div>
                        <div><p class="text-xs text-gray-500 font-medium">Average Progress</p><h3 class="text-xl font-bold text-gray-900">${data.stats.average_progress || 0}%</h3></div>
                    </div>
                `;

                const container = document.getElementById('continue-learning-section');
                if (data.continue_learning && data.continue_learning.course) {
                    const c = data.continue_learning;
                    const course = c.course;
                    container.innerHTML = `
                        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col md:flex-row items-center gap-6">
                            <img src="${course.thumbnail_url || 'assets/course1.jpg'}" class="w-full md:w-48 h-32 object-cover rounded-xl" alt="${course.title}">
                            <div class="flex-1 w-full">
                                <span class="text-xs font-bold text-white ${course.badge_color || 'bg-primary'} px-2 py-1 rounded-md mb-2 inline-block">${course.badge_label || 'COURSE'}</span>
                                <h4 class="text-xl font-bold text-gray-900 mb-2">${course.title}</h4>
                                <div class="w-full bg-gray-100 rounded-full h-2.5 mb-2"><div class="bg-primary h-2.5 rounded-full" style="width: ${c.progress || 0}%"></div></div>
                                <p class="text-xs text-gray-500">${c.progress || 0}% Completed</p>
                            </div>
                            <a href="course-player.html?course=${course.id}" class="bg-gray-900 text-white px-6 py-3 rounded-xl font-semibold hover:bg-primary transition-colors whitespace-nowrap">Resume Class</a>
                        </div>`;
                } else {
                    container.innerHTML = `
                        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 text-center">
                            <p class="text-gray-500 mb-4 text-sm">You are not currently enrolled in active courses.</p>
                            <a href="courses.html" class="inline-block bg-primary text-white font-semibold px-6 py-2.5 rounded-xl text-sm">Browse Courses</a>
                        </div>`;
                }
            } catch (err) {
                console.error('Error loading student dashboard:', err);
                document.getElementById('overview-stats-grid').innerHTML = `
                    <div class="col-span-full bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
                        <p class="text-red-600 font-semibold text-sm">Error loading dashboard</p>
                        <p class="text-red-500 text-xs mt-1">${err.message}</p>
                        <button onclick="location.reload()" class="mt-3 bg-red-500 hover:bg-red-600 text-white text-xs font-bold px-4 py-2 rounded-lg">Reload Page</button>
                    </div>`;
            }
        }

        // ── TEACHER OVERVIEW ──────────────────────────────────────────────────
        async function loadTeacherOverviewStats() {
            const grid = document.getElementById('overview-stats-grid');
            try {
                const res = await authFetch(`${API_BASE}/teacher/dashboard/`);
                if (!res.ok) {
                    throw new Error(`API error: ${res.status}`);
                }
                const data = await res.json();

                if (!data.stats) {
                    throw new Error('Invalid response format: missing stats');
                }

                grid.innerHTML = `
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-violet-50 flex items-center justify-center text-primary text-xl"><i class="ph-fill ph-chalkboard-teacher"></i></div>
                        <div><p class="text-xs text-gray-500 font-medium">Courses Taught</p><h3 class="text-xl font-bold text-gray-900">${data.stats.total_courses || 0}</h3></div>
                    </div>
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-500 text-xl"><i class="ph-fill ph-users"></i></div>
                        <div><p class="text-xs text-gray-500 font-medium">Students Enrolled</p><h3 class="text-xl font-bold text-gray-900">${data.stats.total_students || 0}</h3></div>
                    </div>
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-500 text-xl"><i class="ph-fill ph-clock"></i></div>
                        <div><p class="text-xs text-gray-500 font-medium">Pending Grading</p><h3 class="text-xl font-bold text-amber-600">${data.stats.pending_grading || 0}</h3></div>
                    </div>
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-500 text-xl"><i class="ph-fill ph-question"></i></div>
                        <div><p class="text-xs text-gray-500 font-medium">Published Quizzes</p><h3 class="text-xl font-bold text-gray-900">${data.stats.total_quizzes || 0}</h3></div>
                    </div>
                `;

                document.getElementById('continue-learning-section').innerHTML = `
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <h4 class="font-bold text-gray-900 mb-3 text-sm">Quick Teacher Actions</h4>
                        <div class="flex flex-wrap gap-3">
                            <button onclick="document.querySelector('[data-target=teacher-uploads]').click()" class="bg-primary text-white text-xs font-bold px-4 py-2.5 rounded-xl hover:bg-violet-700">Add Video / Resource</button>
                            <button onclick="document.querySelector('[data-target=teacher-grading]').click()" class="bg-amber-500 text-white text-xs font-bold px-4 py-2.5 rounded-xl hover:bg-amber-600">Grade Student Submissions (${data.stats.pending_grading || 0})</button>
                            <button onclick="document.querySelector('[data-target=quiz-builder]').click()" class="bg-secondary text-white text-xs font-bold px-4 py-2.5 rounded-xl hover:bg-emerald-600">Create New Quiz</button>
                        </div>
                    </div>`;
            } catch (err) {
                console.error('Error loading teacher dashboard:', err);
                const overviewGrid = document.getElementById('overview-stats-grid');
                if (overviewGrid) {
                    overviewGrid.innerHTML = `
                        <div class="col-span-full bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
                            <p class="text-red-600 font-semibold text-sm">Error loading teacher dashboard</p>
                            <p class="text-red-500 text-xs mt-1">${err.message}</p>
                            <button onclick="location.reload()" class="mt-3 bg-red-500 hover:bg-red-600 text-white text-xs font-bold px-4 py-2 rounded-lg">Reload Page</button>
                        </div>`;
                }
            }
        }

        // ── ADMIN OVERVIEW ────────────────────────────────────────────────────
        async function loadAdminOverviewStats() {
            const grid = document.getElementById('overview-stats-grid');
            try {
                const res = await authFetch(`${API_BASE}/admin/dashboard/`);
                if (!res.ok) {
                    throw new Error(`API error: ${res.status}`);
                }
                const data = await res.json();
                const stats = data.stats || data;
                const recentPayments = data.recent_payments || [];
                const topCourses = data.top_courses || [];

                grid.innerHTML = `
                    <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 p-6 rounded-2xl shadow-sm flex items-center gap-4 text-white">
                        <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center text-2xl"><i class="ph-fill ph-currency-dollar"></i></div>
                        <div><p class="text-xs text-emerald-100 font-medium">Total Platform Revenue</p><h3 class="text-2xl font-black">৳${Number(stats.total_revenue || 0).toLocaleString()}</h3></div>
                    </div>
                    <div class="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-2xl shadow-sm flex items-center gap-4 text-white">
                        <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center text-2xl"><i class="ph-fill ph-student"></i></div>
                        <div><p class="text-xs text-blue-100 font-medium">Total Students</p><h3 class="text-2xl font-black">${stats.total_students || 0}</h3></div>
                    </div>
                    <div class="bg-gradient-to-br from-violet-500 to-violet-600 p-6 rounded-2xl shadow-sm flex items-center gap-4 text-white">
                        <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center text-2xl"><i class="ph-fill ph-chalkboard-teacher"></i></div>
                        <div><p class="text-xs text-violet-100 font-medium">Total Teachers</p><h3 class="text-2xl font-black">${stats.total_teachers || 0}</h3></div>
                    </div>
                    <div class="bg-gradient-to-br from-amber-500 to-orange-500 p-6 rounded-2xl shadow-sm flex items-center gap-4 text-white">
                        <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center text-2xl"><i class="ph-fill ph-book-open"></i></div>
                        <div><p class="text-xs text-amber-100 font-medium">Active Courses</p><h3 class="text-2xl font-black">${stats.total_courses || 0}</h3></div>
                    </div>
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center text-gray-600 text-xl"><i class="ph-fill ph-users-three"></i></div>
                        <div><p class="text-xs text-gray-500 font-medium">Total Enrollments</p><h3 class="text-xl font-bold text-gray-900">${stats.total_enrollments || 0}</h3></div>
                    </div>
                `;

                const recentHtml = recentPayments.length ? `
                    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                        <div class="p-4 border-b border-gray-100 flex items-center justify-between">
                            <h4 class="font-bold text-gray-900 text-sm flex items-center gap-2"><i class="ph ph-receipt text-emerald-500"></i> Recent Transactions</h4>
                            <span class="text-xs text-gray-400">${recentPayments.length} latest</span>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead><tr class="bg-gray-50 text-gray-400 uppercase font-bold">
                                    <th class="p-3">Student</th>
                                    <th class="p-3">Course</th>
                                    <th class="p-3">Amount</th>
                                    <th class="p-3">Date</th>
                                    <th class="p-3 text-center">Status</th>
                                </tr></thead>
                                <tbody class="divide-y divide-gray-100">
                                    ${recentPayments.map(p => `<tr class="hover:bg-gray-50">
                                        <td class="p-3 font-semibold text-gray-900">${p.student_name}<br><span class="text-gray-400 font-normal">${p.student_email}</span></td>
                                        <td class="p-3 text-gray-700">${p.course_title}</td>
                                        <td class="p-3 font-bold text-emerald-600">৳${Number(p.amount).toLocaleString()}</td>
                                        <td class="p-3 text-gray-500">${p.date}</td>
                                        <td class="p-3 text-center"><span class="px-2 py-0.5 rounded-full text-xs font-bold ${p.status === 'completed' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}">${p.status}</span></td>
                                    </tr>`).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>` : '';

                const topRevenueMax = topCourses.length ? Math.max(...topCourses.map(c => Number(c.revenue))) : 1;
                const topCoursesHtml = topCourses.length ? `
                    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
                        <h4 class="font-bold text-gray-900 text-sm mb-4 flex items-center gap-2"><i class="ph ph-trend-up text-violet-500"></i> Top Courses by Revenue</h4>
                        <div class="space-y-3">
                            ${topCourses.map((c, i) => {
                                const pct = Math.round((Number(c.revenue) / topRevenueMax) * 100);
                                return `<div>
                                    <div class="flex items-center justify-between text-xs mb-1">
                                        <span class="font-semibold text-gray-800 truncate max-w-[65%]">${c.course_title}</span>
                                        <span class="font-bold text-emerald-600">৳${Number(c.revenue).toLocaleString()}</span>
                                    </div>
                                    <div class="h-2 rounded-full bg-gray-100 overflow-hidden">
                                        <div class="h-full rounded-full ${i === 0 ? 'bg-emerald-500' : i === 1 ? 'bg-violet-500' : i === 2 ? 'bg-blue-500' : 'bg-amber-400'}" style="width:${pct}%"></div>
                                    </div>
                                    <p class="text-xs text-gray-400 mt-0.5">${c.enrollments} enrollment${c.enrollments !== 1 ? 's' : ''}</p>
                                </div>`;
                            }).join('')}
                        </div>
                    </div>` : '';

                document.getElementById('continue-learning-section').innerHTML = `
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        ${recentHtml}
                        <div class="space-y-4">
                            ${topCoursesHtml}
                            <div class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                                <h4 class="font-bold text-gray-900 mb-3 text-sm">Quick Actions</h4>
                                <div class="flex flex-wrap gap-2">
                                    <button onclick="document.querySelector('[data-target=admin-courses]').click()" class="bg-primary text-white text-xs font-bold px-3.5 py-2 rounded-xl hover:bg-violet-700">Manage Courses</button>
                                    <button onclick="document.querySelector('[data-target=admin-teachers]').click()" class="bg-gray-900 text-white text-xs font-bold px-3.5 py-2 rounded-xl hover:bg-primary">Teachers</button>
                                    <button onclick="document.querySelector('[data-target=admin-submissions]').click()" class="bg-blue-600 text-white text-xs font-bold px-3.5 py-2 rounded-xl hover:bg-blue-700">Submissions</button>
                                    <button onclick="document.querySelector('[data-target=admin-users-list]').click()" class="bg-emerald-600 text-white text-xs font-bold px-3.5 py-2 rounded-xl hover:bg-emerald-700">Users</button>
                                </div>
                            </div>
                        </div>
                    </div>`;
            } catch (err) {
                console.error('Error loading admin dashboard:', err);
                const overviewGrid = document.getElementById('overview-stats-grid');
                if (overviewGrid) {
                    overviewGrid.innerHTML = `
                        <div class="col-span-full bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
                            <p class="text-red-600 font-semibold text-sm">Error loading admin dashboard</p>
                            <p class="text-red-500 text-xs mt-1">${err.message}</p>
                            <button onclick="location.reload()" class="mt-3 bg-red-500 hover:bg-red-600 text-white text-xs font-bold px-4 py-2 rounded-lg">Reload Page</button>
                        </div>`;
                }
            }
        }

        // ── 3. MY COURSES LOADER ──────────────────────────────────────────────
        async function loadMyCourses() {
            const container = document.getElementById('my-courses-list');
            container.innerHTML = `<div class="col-span-full text-center text-gray-400 py-8">Loading courses...</div>`;
            try {
                const endpoint = currentUser.role === 'teacher' ? `${API_BASE}/teacher/courses/` : `${API_BASE}/enrollments/`;
                const res = await authFetch(endpoint);
                const data = await res.json();

                if (!data || data.length === 0) {
                    container.innerHTML = `<div class="bg-white rounded-2xl p-8 text-center text-gray-500 col-span-full">No courses found.</div>`;
                    return;
                }

                container.innerHTML = data.map(item => {
                    const course = item.course || item;
                    const progress = item.progress || 0;
                    return `
                    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden flex flex-col hover:shadow-md transition-all">
                        <img src="${course.thumbnail_url || 'assets/course1.jpg'}" class="w-full h-36 object-cover" alt="${course.title}">
                        <div class="p-5 flex-1 flex flex-col">
                            <h4 class="text-base font-bold text-gray-900 mb-2 line-clamp-2">${course.title}</h4>
                            <div class="w-full bg-gray-100 rounded-full h-2 mb-4 mt-auto">
                                <div class="bg-primary h-2 rounded-full" style="width: ${progress}%"></div>
                            </div>
                            <a href="course-player.html?course=${course.id}" class="w-full bg-gray-900 hover:bg-primary text-white py-2 rounded-xl text-xs font-bold text-center block transition-colors">
                                Enter Course Player
                            </a>
                        </div>
                    </div>`;
                }).join('');
            } catch (err) {
                console.error(err);
                container.innerHTML = `<div class="col-span-full text-center text-red-400 py-8">Failed to load courses.</div>`;
            }
        }

        // ── 4. EXAMS & QUIZZES LOADER ──────────────────────────────────────────
        async function loadQuizzes() {
            const container = document.getElementById('quizzes-container');
            container.innerHTML = `<div class="col-span-full text-center text-gray-400 py-8">Loading course quizzes...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/quizzes/`);
                const quizzes = await res.json();

                if (!quizzes || quizzes.length === 0) {
                    container.innerHTML = `<div class="bg-white rounded-2xl p-8 text-center text-gray-500 col-span-full">No quizzes published yet.</div>`;
                    return;
                }

                container.innerHTML = quizzes.map(q => {
                    const statusBadge = q.is_submitted
                        ? (q.student_passed ? `<span class="bg-emerald-50 text-emerald-600 border border-emerald-200 text-xs font-bold px-2.5 py-1 rounded-md">PASSED (${q.student_score}/${q.total_marks})</span>`
                                            : `<span class="bg-red-50 text-red-600 border border-red-200 text-xs font-bold px-2.5 py-1 rounded-md">FAILED (${q.student_score}/${q.total_marks})</span>`)
                        : `<span class="bg-amber-50 text-amber-600 border border-amber-200 text-xs font-bold px-2.5 py-1 rounded-md">NOT ATTEMPTED</span>`;

                    return `
                    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between gap-2 mb-2">
                                <span class="text-xs text-gray-400 font-bold uppercase">${q.course_title}</span>
                                ${statusBadge}
                            </div>
                            <h4 class="font-bold text-gray-900 text-lg mb-1">${q.title}</h4>
                            <p class="text-xs text-gray-500 mb-4">${q.description || 'Test your module knowledge and score points for the leaderboard.'}</p>
                            <div class="flex items-center gap-4 text-xs text-gray-500 mb-4">
                                <span><i class="ph ph-question text-primary mr-1"></i>${q.total_questions} Questions</span>
                                <span><i class="ph ph-star text-amber-500 mr-1"></i>${q.total_marks} Total Marks</span>
                                <span><i class="ph ph-check-circle text-emerald-500 mr-1"></i>Pass: ${q.passing_percentage}%</span>
                            </div>
                        </div>
                        <button onclick="openQuizModal(${q.id}, '${q.title.replace(/'/g, "\\'")}')" class="w-full bg-primary hover:bg-violet-700 text-white font-bold py-2.5 rounded-xl text-xs transition-colors flex items-center justify-center gap-2">
                            <i class="ph ph-play text-sm"></i> ${q.is_submitted ? 'Retake Quiz' : 'Start Quiz'}
                        </button>
                    </div>`;
                }).join('');
            } catch (err) {
                console.error(err);
            }
        }

        // ── 5. QUIZ ATTEMPT MODAL LOGIC ───────────────────────────────────────
        async function openQuizModal(quizId, title) {
            currentQuizId = quizId;
            document.getElementById('quiz-modal-title').textContent = title;
            const modal = document.getElementById('quiz-attempt-modal');
            const body = document.getElementById('quiz-modal-body');
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            body.innerHTML = `<div class="text-center py-8 text-gray-400">Loading questions...</div>`;

            try {
                const res = await authFetch(`${API_BASE}/quizzes/${quizId}/`);
                const data = await res.json();
                const questions = data.questions || [];

                if (questions.length === 0) {
                    body.innerHTML = `<div class="text-center py-8 text-gray-500">No questions available in this quiz.</div>`;
                    return;
                }

                body.innerHTML = questions.map((q, idx) => `
                    <div class="bg-gray-50 border border-gray-200 p-4 rounded-xl space-y-2">
                        <p class="font-bold text-sm text-gray-900">${idx + 1}. ${q.question_text}</p>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 pt-1 text-xs">
                            <label class="flex items-center gap-2 bg-white p-2.5 rounded-lg border border-gray-200 cursor-pointer hover:border-primary">
                                <input type="radio" name="q_${q.id}" value="A" class="accent-primary"> <span>A) ${q.option_a}</span>
                            </label>
                            <label class="flex items-center gap-2 bg-white p-2.5 rounded-lg border border-gray-200 cursor-pointer hover:border-primary">
                                <input type="radio" name="q_${q.id}" value="B" class="accent-primary"> <span>B) ${q.option_b}</span>
                            </label>
                            <label class="flex items-center gap-2 bg-white p-2.5 rounded-lg border border-gray-200 cursor-pointer hover:border-primary">
                                <input type="radio" name="q_${q.id}" value="C" class="accent-primary"> <span>C) ${q.option_c}</span>
                            </label>
                            <label class="flex items-center gap-2 bg-white p-2.5 rounded-lg border border-gray-200 cursor-pointer hover:border-primary">
                                <input type="radio" name="q_${q.id}" value="D" class="accent-primary"> <span>D) ${q.option_d}</span>
                            </label>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error(err);
            }
        }

        function closeQuizModal() {
            const modal = document.getElementById('quiz-attempt-modal');
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }

        async function submitQuizAnswers() {
            if (!currentQuizId) return;
            const answers = {};
            document.querySelectorAll('input[type=radio]:checked').forEach(radio => {
                const qId = radio.name.replace('q_', '');
                answers[qId] = radio.value;
            });

            try {
                const res = await authFetch(`${API_BASE}/quizzes/${currentQuizId}/submit/`, {
                    method: 'POST',
                    body: JSON.stringify({ answers })
                });
                const result = await res.json();
                closeQuizModal();
                alert(`Quiz Results:\nScore: ${result.score}/${result.total_marks} (${result.percentage}%)\nStatus: ${result.passed ? 'PASSED 🎉' : 'FAILED'}\n${result.certificate_reason}`);
                loadQuizzes();
            } catch (err) {
                console.error(err);
            }
        }

        // ── 6. CERTIFICATES LOADER ─────────────────────────────────────────────
        async function loadCertificates() {
            const container = document.getElementById('user-certificates-list');
            container.innerHTML = `<div class="col-span-full text-center text-gray-400 py-8">Loading certificates...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/certificates/`);
                const certs = await res.json();

                if (!certs || certs.length === 0) {
                    container.innerHTML = `
                        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 text-center text-gray-500 col-span-full">
                            <i class="ph ph-lock-key text-4xl text-amber-500 mb-2"></i>
                            <h4 class="font-bold text-gray-900 text-base mb-1">Certificates Locked</h4>
                            <p class="text-xs text-gray-500">You must watch 100% of video lessons, get teacher approval on all assignments, and pass all quizzes to unlock your certificate.</p>
                        </div>`;
                    return;
                }

                container.innerHTML = certs.map(c => `
                    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-all">
                        <div class="flex items-start justify-between gap-4 mb-4">
                            <div>
                                <span class="bg-amber-50 text-amber-600 border border-amber-200 text-xs font-bold px-2.5 py-1 rounded-md mb-2 inline-block">
                                    <i class="ph-fill ph-seal-check mr-1"></i> VERIFIED CERTIFICATE
                                </span>
                                <h4 class="text-lg font-bold text-gray-900 leading-snug">${c.course_title}</h4>
                                <p class="text-xs text-gray-500 mt-1">Instructor: ${c.instructor_name || 'TutorBhaiya Lead'}</p>
                            </div>
                            <span class="text-xs font-mono font-bold text-primary bg-violet-50 px-2.5 py-1 rounded-lg shrink-0">${c.certificate_number}</span>
                        </div>
                        <div class="flex items-center justify-between pt-4 border-t border-gray-100 mt-2">
                            <span class="text-xs text-gray-400">Issued: ${new Date(c.issued_at).toLocaleDateString()}</span>
                            <a href="certificate.html?id=${c.certificate_number}" target="_blank" class="bg-primary hover:bg-violet-700 text-white px-4 py-2 rounded-xl text-xs font-bold transition-colors inline-flex items-center gap-1">
                                <i class="ph ph-eye text-sm"></i> View & Print
                            </a>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error(err);
            }
        }

        // ── 7. LEADERBOARD LOADER ──────────────────────────────────────────────
        async function loadLeaderboard() {
            const container = document.getElementById('leaderboard-container');
            container.innerHTML = `<div class="p-8 text-center text-gray-400">Loading student rankings...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/leaderboard/`);
                const list = await res.json();

                if (!list || list.length === 0) {
                    container.innerHTML = `<div class="p-8 text-center text-gray-500">No student activity recorded yet.</div>`;
                    return;
                }

                container.innerHTML = `
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-gray-50 border-b border-gray-100 text-xs text-gray-400 font-bold uppercase">
                                <th class="p-4">Rank</th>
                                <th class="p-4">Student</th>
                                <th class="p-4 text-center">Assignment Marks</th>
                                <th class="p-4 text-center">Quiz Score</th>
                                <th class="p-4 text-center">Certificates</th>
                                <th class="p-4 text-right">Total Points</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-sm">
                            ${list.map(s => {
                                let badge = `<span class="font-bold text-gray-500">#${s.rank}</span>`;
                                if (s.rank === 1) badge = `<span class="bg-amber-100 text-amber-800 font-extrabold px-2.5 py-1 rounded-full text-xs">🥇 1st</span>`;
                                if (s.rank === 2) badge = `<span class="bg-slate-100 text-slate-700 font-extrabold px-2.5 py-1 rounded-full text-xs">🥈 2nd</span>`;
                                if (s.rank === 3) badge = `<span class="bg-orange-100 text-amber-900 font-extrabold px-2.5 py-1 rounded-full text-xs">🥉 3rd</span>`;

                                return `
                                <tr class="hover:bg-gray-50">
                                    <td class="p-4">${badge}</td>
                                    <td class="p-4 font-semibold text-gray-900">${s.name} <span class="text-xs text-gray-400 font-normal">(${s.email})</span></td>
                                    <td class="p-4 text-center font-mono">${s.assignment_points}</td>
                                    <td class="p-4 text-center font-mono">${s.quiz_points}</td>
                                    <td class="p-4 text-center font-bold text-amber-500">${s.certificates_earned}</td>
                                    <td class="p-4 text-right font-extrabold text-primary">${s.total_points} pts</td>
                                </tr>`;
                            }).join('')}
                        </tbody>
                    </table>`;
            } catch (err) {
                console.error(err);
            }
        }

        // ── 8. TEACHER SUBMISSIONS & GRADING LOADER ────────────────────────────
        window._teacherSubmissionsMap = {};

        async function loadTeacherSubmissions() {
            const container = document.getElementById('teacher-submissions-container');
            container.innerHTML = `<div class="p-8 text-center text-gray-400">Loading student submissions...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/teacher/assignments/submissions/`);
                const submissions = await res.json();

                if (!submissions || submissions.length === 0) {
                    container.innerHTML = `<div class="p-8 text-center text-gray-500">No student assignment submissions yet.</div>`;
                    return;
                }

                window._teacherSubmissionsMap = {};
                submissions.forEach(s => { window._teacherSubmissionsMap[s.id] = s; });

                container.innerHTML = `
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-gray-50 border-b border-gray-100 text-xs text-gray-400 font-bold uppercase">
                                <th class="p-4">Student</th>
                                <th class="p-4">Course & Assignment</th>
                                <th class="p-4 text-center">Status</th>
                                <th class="p-4 text-center">Marks</th>
                                <th class="p-4 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-sm">
                            ${submissions.map(s => {
                                let stBadge = `<span class="bg-amber-50 text-amber-600 text-xs font-bold px-2 py-0.5 rounded-md">PENDING REVIEW</span>`;
                                if (s.status === 'approved') stBadge = `<span class="bg-emerald-50 text-emerald-600 text-xs font-bold px-2 py-0.5 rounded-md">APPROVED</span>`;
                                if (s.status === 'rejected') stBadge = `<span class="bg-red-50 text-red-600 text-xs font-bold px-2 py-0.5 rounded-md">REJECTED</span>`;

                                return `
                                <tr>
                                    <td class="p-4"><p class="font-semibold text-gray-900">${s.student_name}</p><p class="text-xs text-gray-400">${s.student_email}</p></td>
                                    <td class="p-4"><p class="font-semibold text-gray-900 text-xs">${s.course_title}</p><p class="text-xs text-gray-500">${s.assignment_title}</p></td>
                                    <td class="p-4 text-center">${stBadge}</td>
                                    <td class="p-4 text-center font-bold">${s.marks_obtained !== null ? `${s.marks_obtained}/${s.total_marks}` : '—'}</td>
                                    <td class="p-4 text-right">
                                        <button onclick="openGradeModal(${s.id})" class="bg-primary hover:bg-violet-700 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition-colors">
                                            Evaluate & Grade
                                        </button>
                                    </td>
                                </tr>`;
                            }).join('')}
                        </tbody>
                    </table>`;
            } catch (err) {
                console.error(err);
            }
        }

        function openGradeModal(subId) {
            const s = window._teacherSubmissionsMap[subId];
            if (!s) return;

            document.getElementById('grade-submission-id').value = s.id;
            document.getElementById('grade-modal-student').textContent = `${s.student_name} (${s.course_title})`;
            document.getElementById('grade-submission-text').textContent = s.submission_text || 'No text answer provided.';
            document.getElementById('grade-total-marks').textContent = s.total_marks;
            document.getElementById('grade-marks-input').value = s.marks_obtained !== null ? s.marks_obtained : s.total_marks;
            document.getElementById('grade-feedback-input').value = s.feedback || '';
            document.getElementById('grade-status-select').value = s.status || 'approved';

            const fileContainer = document.getElementById('grade-file-container');
            const fileLink = document.getElementById('grade-file-link');
            if (s.submission_file_url) {
                fileLink.href = s.submission_file_url;
                fileContainer.classList.remove('hidden');
            } else {
                fileContainer.classList.add('hidden');
            }

            const modal = document.getElementById('grade-modal');
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }

        function closeGradeModal() {
            const modal = document.getElementById('grade-modal');
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }

        document.getElementById('form-grade-submission').addEventListener('submit', async (e) => {
            e.preventDefault();
            const subId = document.getElementById('grade-submission-id').value;
            const marks = document.getElementById('grade-marks-input').value;
            const feedback = document.getElementById('grade-feedback-input').value;
            const statusVal = document.getElementById('grade-status-select').value;

            try {
                const res = await authFetch(`${API_BASE}/teacher/assignments/grade/`, {
                    method: 'POST',
                    body: JSON.stringify({ submission_id: subId, marks_obtained: marks, feedback, status: statusVal })
                });
                const data = await res.json();
                closeGradeModal();
                alert(data.message);
                loadTeacherSubmissions();
            } catch (err) {
                console.error(err);
            }
        });

        // ── 9. ADMIN TEACHER ACTIVITY LOADER ─────────────────────────────────
        async function loadAdminTeacherActivity() {
            const container = document.getElementById('admin-teachers-container');
            container.innerHTML = `<div class="p-8 text-center text-gray-400">Loading teacher activity matrix...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/admin/teachers/`);
                const teachers = await res.json();

                if (!teachers || teachers.length === 0) {
                    container.innerHTML = `<div class="p-8 text-center text-gray-500">No teachers found in system.</div>`;
                    return;
                }

                container.innerHTML = `
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-gray-50 border-b border-gray-100 text-xs text-gray-400 font-bold uppercase">
                                <th class="p-4">Teacher</th>
                                <th class="p-4 text-center">Courses</th>
                                <th class="p-4 text-center">Videos Uploaded</th>
                                <th class="p-4 text-center">Resources / Links</th>
                                <th class="p-4 text-center">Assignments</th>
                                <th class="p-4 text-center">Quizzes</th>
                                <th class="p-4 text-center">Students</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-sm">
                            ${teachers.map(t => `
                                <tr>
                                    <td class="p-4 font-semibold text-gray-900">${t.name} <p class="text-xs text-gray-400 font-normal">${t.email}</p></td>
                                    <td class="p-4 text-center font-bold">${t.courses_count}</td>
                                    <td class="p-4 text-center font-mono">${t.videos_count}</td>
                                    <td class="p-4 text-center font-mono">${t.resources_count}</td>
                                    <td class="p-4 text-center font-mono">${t.assignments_count}</td>
                                    <td class="p-4 text-center font-mono">${t.quizzes_count}</td>
                                    <td class="p-4 text-center font-bold text-primary">${t.students_count}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>`;
            } catch (err) {
                console.error(err);
            }
        }

        // ── 10. ADMIN SUBMISSIONS FEED ─────────────────────────────────────────
        async function loadAdminSubmissions() {
            const container = document.getElementById('admin-submissions-container');
            container.innerHTML = `<div class="p-8 text-center text-gray-400">Loading submissions feed...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/admin/submissions/`);
                const data = await res.json();
                const assigns = data.assignment_submissions || [];
                const quizzes = data.quiz_submissions || [];

                container.innerHTML = `
                    <div class="p-4 bg-gray-50 border-b border-gray-100 font-bold text-sm text-gray-900">Assignment Submissions (${assigns.length})</div>
                    <table class="w-full text-left border-collapse border-b border-gray-200 mb-6">
                        <thead><tr class="bg-gray-50 text-xs text-gray-400 uppercase"><th class="p-3">Student</th><th class="p-3">Course / Task</th><th class="p-3 text-center">Status</th><th class="p-3 text-right">Marks</th></tr></thead>
                        <tbody class="divide-y divide-gray-100 text-xs">
                            ${assigns.map(a => `<tr><td class="p-3 font-semibold">${a.student_name}</td><td class="p-3">${a.course_title} - ${a.assignment_title}</td><td class="p-3 text-center">${a.status}</td><td class="p-3 text-right font-bold">${a.marks_obtained !== null ? a.marks_obtained : '—'}</td></tr>`).join('')}
                        </tbody>
                    </table>
                    <div class="p-4 bg-gray-50 border-b border-gray-100 font-bold text-sm text-gray-900">Quiz Submissions (${quizzes.length})</div>
                    <table class="w-full text-left border-collapse">
                        <thead><tr class="bg-gray-50 text-xs text-gray-400 uppercase"><th class="p-3">Student</th><th class="p-3">Course / Quiz</th><th class="p-3 text-center">Result</th><th class="p-3 text-right">Score</th></tr></thead>
                        <tbody class="divide-y divide-gray-100 text-xs">
                            ${quizzes.map(q => `<tr><td class="p-3 font-semibold">${q.student_name}</td><td class="p-3">${q.course_title} - ${q.quiz_title}</td><td class="p-3 text-center font-bold ${q.passed ? 'text-emerald-600' : 'text-red-500'}">${q.passed ? 'PASSED' : 'FAILED'}</td><td class="p-3 text-right font-bold">${q.score}/${q.total_marks}</td></tr>`).join('')}
                        </tbody>
                    </table>`;
            } catch (err) {
                console.error(err);
            }
        }

        // ── 11. FORM HELPERS FOR CONTENT CREATION ─────────────────────────────
        let _teacherCourses = []; // cache teacher's courses

        async function populateCourseSelects() {
            try {
                // Use teacher's own courses only
                const res = await authFetch(`${API_BASE}/teacher/courses/`);
                const data = await res.json();
                _teacherCourses = data.results || data;

                const defaultOpt = '<option value="">-- Select Your Course --</option>';
                const options = defaultOpt + _teacherCourses.map(c => `<option value="${c.id}" data-slug="${c.slug}">${c.title}</option>`).join('');

                ['video-course-select', 'module-course-select', 'resource-course-select', 'assign-course-select', 'quiz-course-select'].forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.innerHTML = options;
                });

                // Attach module loaders on course change
                const vcSel = document.getElementById('video-course-select');
                if (vcSel) vcSel.onchange = () => loadModulesForCourse(vcSel.value, 'video-module-select');

                const rcSel = document.getElementById('resource-course-select');
                if (rcSel) rcSel.onchange = () => loadModulesForCourse(rcSel.value, 'resource-module-select');

                const acSel = document.getElementById('assign-course-select');
                if (acSel) acSel.onchange = () => loadModulesForCourse(acSel.value, 'assign-module-select');
            } catch (err) {
                console.error(err);
            }
        }

        async function loadModulesForCourse(courseId, targetSelectId) {
            const modSel = document.getElementById(targetSelectId);
            if (!modSel || !courseId) {
                if (modSel) modSel.innerHTML = '<option value="">-- Select a Course First --</option>';
                return;
            }
            modSel.innerHTML = '<option value="">Loading modules...</option>';
            try {
                // Find slug from cached list
                const course = _teacherCourses.find(c => String(c.id) === String(courseId));
                if (!course) return;
                const res = await authFetch(`${API_BASE}/courses/${course.slug}/`);
                const data = await res.json();
                const modules = data.modules || [];
                if (!modules.length) {
                    modSel.innerHTML = '<option value="">No modules yet — create one first</option>';
                } else {
                    modSel.innerHTML = '<option value="">-- Select Module --</option>' + modules.map(m => `<option value="${m.id}">${m.title}</option>`).join('');
                }
            } catch (err) {
                modSel.innerHTML = '<option value="">Failed to load modules</option>';
            }
        }

        // Create Module Form Submit
        document.getElementById('form-add-module')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const courseId = document.getElementById('module-course-select').value;
            const title = document.getElementById('module-title-input').value;
            const order = document.getElementById('module-order-input').value;
            if (!courseId) { alert('Please select a course first.'); return; }
            try {
                const res = await authFetch(`${API_BASE}/teacher/content/module/`, {
                    method: 'POST',
                    body: JSON.stringify({ course: courseId, title, order })
                });
                const data = await res.json();
                alert(data.message || 'Module created successfully!');
                document.getElementById('form-add-module').reset();
            } catch (err) { console.error(err); }
        });

        // Add Video Form Submit
        document.getElementById('form-add-video').addEventListener('submit', async (e) => {
            e.preventDefault();
            const courseId = document.getElementById('video-course-select').value;
            const modId = document.getElementById('video-module-select').value;
            const title = document.getElementById('video-title-input').value;
            const url = document.getElementById('video-url-input').value;
            const duration = document.getElementById('video-duration-input').value;
            if (!courseId) { alert('Please select a course.'); return; }
            if (!modId) { alert('Please select a module. Create a module first if none exist.'); return; }

            try {
                const res = await authFetch(`${API_BASE}/teacher/content/video/`, {
                    method: 'POST',
                    body: JSON.stringify({ module: modId, title, video_url: url, duration_minutes: duration })
                });
                const data = await res.json();
                alert(data.message || 'Video added successfully!');
                document.getElementById('form-add-video').reset();
            } catch (err) { console.error(err); }
        });

        // Add Resource Form Submit
        document.getElementById('form-add-resource').addEventListener('submit', async (e) => {
            e.preventDefault();
            const courseId = document.getElementById('resource-course-select').value;
            const modId = document.getElementById('resource-module-select')?.value;
            const title = document.getElementById('resource-title-input').value;
            const url = document.getElementById('resource-url-input').value;

            try {
                const res = await authFetch(`${API_BASE}/teacher/content/resource/`, {
                    method: 'POST',
                    body: JSON.stringify({ course: courseId, module: modId || null, title, url })
                });
                const data = await res.json();
                alert(data.message || 'Resource added successfully!');
                document.getElementById('form-add-resource').reset();
            } catch (err) { console.error(err); }
        });

        // Add Assignment Form Submit
        document.getElementById('form-add-assignment').addEventListener('submit', async (e) => {
            e.preventDefault();
            const courseId = document.getElementById('assign-course-select').value;
            const modId = document.getElementById('assign-module-select')?.value;
            const title = document.getElementById('assign-title-input').value;
            const marks = document.getElementById('assign-marks-input').value;
            const desc = document.getElementById('assign-desc-input').value;
            const fileInput = document.getElementById('assign-attachment-input');
            const attachment = fileInput && fileInput.files[0] ? fileInput.files[0] : null;

            try {
                const formData = new FormData();
                formData.append('course', courseId);
                if (modId) formData.append('module', modId);
                formData.append('title', title);
                formData.append('total_marks', marks);
                formData.append('description', desc);
                if (attachment) formData.append('attachment_file', attachment);

                const token = localStorage.getItem('token');
                const headers = { 'X-CSRFToken': getCookie('csrftoken') || '' };
                if (token) headers['Authorization'] = `Token ${token}`;

                const res = await fetch(`${API_BASE}/teacher/content/assignment/`, {
                    method: 'POST',
                    headers,
                    credentials: 'include',
                    body: formData
                });
                const data = await res.json();
                if (!res.ok) {
                    alert(data.error || 'Failed to create assignment');
                    return;
                }
                alert(data.message || 'Assignment created successfully!');
                document.getElementById('form-add-assignment').reset();
            } catch (err) { console.error(err); }
        });

        // ── 15. NOTIFICATIONS SYSTEM LOADER ──────────────────────────────────
        async function loadNotifications() {
            try {
                const res = await authFetch(`${API_BASE}/notifications/`);
                if (!res.ok) return;
                const data = await res.json();
                const unreadCount = data.unread_count || 0;
                const list = data.notifications || [];

                const badge = document.getElementById('notif-badge-count');
                if (badge) {
                    if (unreadCount > 0) {
                        badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                        badge.classList.remove('hidden');
                    } else {
                        badge.classList.add('hidden');
                    }
                }

                const dropList = document.getElementById('notif-dropdown-list');
                if (dropList) {
                    if (!list.length) {
                        dropList.innerHTML = `<div class="p-6 text-center text-xs text-gray-400">No notifications yet.</div>`;
                    } else {
                        dropList.innerHTML = list.slice(0, 10).map(n => `
                            <div class="p-3.5 hover:bg-gray-50 transition-colors ${n.is_read ? 'opacity-75' : 'bg-violet-50/40'}">
                                <div class="flex items-start justify-between gap-2">
                                    <h5 class="text-xs font-bold ${n.is_read ? 'text-gray-700' : 'text-primary'}">${escapeHTML(n.title)}</h5>
                                    <span class="text-[10px] text-gray-400 shrink-0">${new Date(n.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                                </div>
                                <p class="text-xs text-gray-600 mt-1 leading-relaxed">${escapeHTML(n.message)}</p>
                                ${n.resource_url ? `
                                <div class="mt-2">
                                    <a href="${n.resource_url}" target="_blank" class="inline-flex items-center gap-1 text-[11px] font-bold text-primary hover:underline">
                                        <i class="ph ph-link-simple"></i> Open Attached Resource
                                    </a>
                                </div>` : ''}
                            </div>
                        `).join('');
                    }
                }

                const fullContainer = document.getElementById('full-notifications-container');
                if (fullContainer) {
                    if (!list.length) {
                        fullContainer.innerHTML = `<div class="p-8 text-center text-gray-500 text-sm">No notifications recorded yet.</div>`;
                    } else {
                        fullContainer.innerHTML = `
                            <div class="divide-y divide-gray-100">
                                ${list.map(n => `
                                    <div class="p-5 flex items-start justify-between gap-4 ${n.is_read ? 'bg-white' : 'bg-violet-50/40'}">
                                        <div class="space-y-1">
                                            <div class="flex items-center gap-2">
                                                <span class="font-bold text-sm text-gray-900">${escapeHTML(n.title)}</span>
                                                ${!n.is_read ? `<span class="bg-primary text-white text-[9px] font-extrabold px-2 py-0.5 rounded-full">NEW</span>` : ''}
                                            </div>
                                            <p class="text-xs text-gray-600 leading-relaxed">${escapeHTML(n.message)}</p>
                                            ${n.resource_url ? `
                                            <div class="pt-1">
                                                <a href="${n.resource_url}" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-violet-100 text-primary font-bold text-xs rounded-lg hover:bg-violet-200 transition-colors">
                                                    <i class="ph ph-arrow-square-out text-sm"></i> Access Attached Resource / File
                                                </a>
                                            </div>` : ''}
                                        </div>
                                        <span class="text-xs text-gray-400 shrink-0 font-medium">${new Date(n.created_at).toLocaleDateString()} ${new Date(n.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                    }
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function markAllNotificationsRead() {
            try {
                await authFetch(`${API_BASE}/notifications/read/`, { method: 'POST' });
                loadNotifications();
            } catch (err) { console.error(err); }
        }

        function toggleNotifDropdown() {
            const drop = document.getElementById('notif-dropdown');
            if (drop) drop.classList.toggle('hidden');
        }
                alert(data.message || 'Assignment created successfully!');
                document.getElementById('form-add-assignment').reset();
            } catch (err) { console.error(err); }
        });

        // Question Builder logic for Quiz Builder
        let questionCount = 0;
        function addQuestionField() {
            questionCount++;
            const container = document.getElementById('questions-builder-list');
            const div = document.createElement('div');
            div.className = 'p-4 bg-gray-50 border border-gray-200 rounded-xl space-y-3';
            div.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-bold text-xs text-primary">Question ${questionCount}</span>
                    <button type="button" onclick="this.parentElement.parentElement.remove()" class="text-xs text-red-500 hover:underline">Remove</button>
                </div>
                <input type="text" name="q_text" placeholder="Question prompt..." required class="w-full border border-gray-200 rounded-lg p-2 text-xs">
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <input type="text" name="opt_a" placeholder="Option A" required class="border border-gray-200 rounded-lg p-2">
                    <input type="text" name="opt_b" placeholder="Option B" required class="border border-gray-200 rounded-lg p-2">
                    <input type="text" name="opt_c" placeholder="Option C" required class="border border-gray-200 rounded-lg p-2">
                    <input type="text" name="opt_d" placeholder="Option D" required class="border border-gray-200 rounded-lg p-2">
                </div>
                <div class="flex items-center gap-3 text-xs">
                    <label class="font-semibold text-gray-700">Correct Option Key:</label>
                    <select name="correct_opt" class="border border-gray-200 rounded-lg p-1.5">
                        <option value="A">A</option>
                        <option value="B">B</option>
                        <option value="C">C</option>
                        <option value="D">D</option>
                    </select>
                </div>`;
            container.appendChild(div);
        }

        // Initialize with 1 question
        addQuestionField();

        // Create Quiz Form Submit
        document.getElementById('form-create-quiz').addEventListener('submit', async (e) => {
            e.preventDefault();
            const courseId = document.getElementById('quiz-course-select').value;
            const title = document.getElementById('quiz-title-input').value;
            const passPct = document.getElementById('quiz-pass-input').value;

            const questions = [];
            document.querySelectorAll('#questions-builder-list > div').forEach(div => {
                questions.push({
                    question_text: div.querySelector('[name=q_text]').value,
                    option_a: div.querySelector('[name=opt_a]').value,
                    option_b: div.querySelector('[name=opt_b]').value,
                    option_c: div.querySelector('[name=opt_c]').value,
                    option_d: div.querySelector('[name=opt_d]').value,
                    correct_option: div.querySelector('[name=correct_opt]').value,
                    marks: 5
                });
            });

            try {
                const res = await authFetch(`${API_BASE}/quizzes/`, {
                    method: 'POST',
                    body: JSON.stringify({ course: courseId, title, passing_percentage: passPct, questions })
                });
                const data = await res.json();
                alert('Quiz created successfully!');
                document.getElementById('form-create-quiz').reset();
            } catch (err) { console.error(err); }
        });

        // User Role Update Submit
        document.getElementById('form-user-role').addEventListener('submit', async (e) => {
            e.preventDefault();
            const userId = document.getElementById('role-user-id').value;
            const role = document.getElementById('role-select').value;

            try {
                const res = await authFetch(`${API_BASE}/admin/users/role/`, {
                    method: 'POST',
                    body: JSON.stringify({ user_id: userId, role })
                });
                const data = await res.json();
                alert(data.message || 'User role updated!');
            } catch (err) { console.error(err); }
        });


        // ── TEACHER LIVE CLASS SCHEDULER ──────────────────────────────────────
        async function loadTeacherLive() {
            // Populate course select for the form
            const courseSelect = document.getElementById('live-course-select');
            try {
                const res = await authFetch(`${API_BASE}/teacher/courses/`);
                const courses = await res.json();
                courseSelect.innerHTML = courses.map(c => `<option value="${c.id}">${c.title}</option>`).join('') || '<option>No courses assigned</option>';
            } catch (e) { courseSelect.innerHTML = '<option>Error loading courses</option>'; }

            // Load scheduled routines
            const list = document.getElementById('teacher-routines-list');
            list.innerHTML = `<div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 text-center text-gray-400">Loading...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/teacher/routines/`);
                const routines = await res.json();
                if (!routines.length) {
                    list.innerHTML = `<div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 text-center text-gray-400 text-sm">No classes scheduled yet. Use the form to add one.</div>`;
                    return;
                }
                list.innerHTML = routines.map(r => {
                    const typeColors = { live_class: 'bg-primary text-white', exam: 'bg-red-500 text-white', off_day: 'bg-gray-400 text-white' };
                    const color = typeColors[r.event_type] || 'bg-gray-200 text-gray-700';
                    return `
                    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 flex items-start justify-between gap-3">
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-xs font-bold px-2 py-0.5 rounded-md ${color}">${r.event_type_display}</span>
                                <span class="text-xs text-gray-400 font-medium truncate">${r.course_title}</span>
                            </div>
                            <p class="font-semibold text-gray-900 text-sm">${r.title}</p>
                            <p class="text-xs text-gray-500 mt-0.5">${r.date || r.day_of_week || ''} ${r.start_time ? '· ' + r.start_time : ''} ${r.end_time ? '– ' + r.end_time : ''}</p>
                            ${r.live_link ? `<a href="${r.live_link}" target="_blank" class="inline-flex items-center gap-1 mt-1 text-xs text-primary font-semibold hover:underline"><i class="ph ph-video-camera"></i> Join Link</a>` : ''}
                        </div>
                        <button onclick="deleteRoutine(${r.id})" class="text-gray-300 hover:text-red-400 transition-colors shrink-0 mt-1"><i class="ph ph-trash text-lg"></i></button>
                    </div>`;
                }).join('');
            } catch (e) { list.innerHTML = `<div class="p-4 text-red-400 text-sm">Failed to load routines.</div>`; }
        }

        async function deleteRoutine(id) {
            if (!confirm('Delete this scheduled event?')) return;
            try {
                await authFetch(`${API_BASE}/teacher/routines/${id}/`, { method: 'DELETE' });
                loadTeacherLive();
            } catch (e) { alert('Failed to delete.'); }
        }

        document.getElementById('form-schedule-live').addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = document.getElementById('live-form-msg');
            msg.className = 'text-xs font-medium text-center py-2 rounded-xl bg-gray-100 text-gray-600';
            msg.textContent = 'Scheduling...';
            msg.classList.remove('hidden');
            try {
                const res = await authFetch(`${API_BASE}/teacher/routines/`, {
                    method: 'POST',
                    body: JSON.stringify({
                        course_id: document.getElementById('live-course-select').value,
                        title: document.getElementById('live-title-input').value,
                        event_type: document.getElementById('live-type-select').value,
                        date: document.getElementById('live-date-input').value || null,
                        day_of_week: document.getElementById('live-day-input').value,
                        start_time: document.getElementById('live-start-input').value || null,
                        end_time: document.getElementById('live-end-input').value || null,
                        live_link: document.getElementById('live-link-input').value,
                        description: document.getElementById('live-desc-input').value,
                    })
                });
                const data = await res.json();
                if (res.ok) {
                    msg.className = 'text-xs font-medium text-center py-2 rounded-xl bg-emerald-50 text-emerald-600';
                    msg.textContent = data.message || 'Live class scheduled!';
                    e.target.reset();
                    loadTeacherLive();
                } else {
                    msg.className = 'text-xs font-medium text-center py-2 rounded-xl bg-red-50 text-red-600';
                    msg.textContent = JSON.stringify(data);
                }
            } catch (err) {
                msg.className = 'text-xs font-medium text-center py-2 rounded-xl bg-red-50 text-red-600';
                msg.textContent = 'Server error. Try again.';
            }
        });

        // ── STUDENT LIVE CLASSES ──────────────────────────────────────────────
        async function loadStudentLive() {
            const container = document.getElementById('student-live-container');
            container.innerHTML = `<div class="col-span-full text-center text-gray-400 py-8">Loading live classes...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/routines/`);
                const routines = await res.json();
                if (!routines.length) {
                    container.innerHTML = `<div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 text-center text-gray-500 col-span-full"><i class="ph ph-video-camera text-4xl text-gray-200 block mb-2"></i>No live classes scheduled yet for your courses.</div>`;
                    return;
                }
                const typeConfig = {
                    live_class: { color: 'bg-primary', icon: 'ph-video-camera', label: 'LIVE CLASS' },
                    exam: { color: 'bg-red-500', icon: 'ph-exam', label: 'EXAM' },
                    off_day: { color: 'bg-gray-400', icon: 'ph-calendar-x', label: 'OFF DAY' },
                };
                container.innerHTML = routines.map(r => {
                    const cfg = typeConfig[r.event_type] || typeConfig.live_class;
                    return `
                    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col gap-3">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-white ${cfg.color} px-2.5 py-1 rounded-lg flex items-center gap-1">
                                <i class="ph ${cfg.icon}"></i> ${cfg.label}
                            </span>
                            <span class="text-xs text-gray-400 font-medium">${r.course_title}</span>
                        </div>
                        <div>
                            <h4 class="font-bold text-gray-900">${r.title}</h4>
                            <p class="text-xs text-gray-500 mt-1">${r.date || r.day_of_week || 'TBD'} ${r.start_time ? '· ' + r.start_time : ''} ${r.end_time ? '– ' + r.end_time : ''}</p>
                            ${r.description ? `<p class="text-xs text-gray-600 mt-1">${r.description}</p>` : ''}
                        </div>
                        ${r.live_link && r.event_type === 'live_class'
                            ? `<a href="${r.live_link}" target="_blank" rel="noopener" class="mt-auto w-full bg-primary hover:bg-violet-700 text-white font-bold py-2.5 rounded-xl text-xs text-center flex items-center justify-center gap-2 transition-colors">
                                <i class="ph ph-video-camera"></i> Join Live Class
                               </a>`
                            : `<div class="mt-auto w-full bg-gray-100 text-gray-400 font-bold py-2.5 rounded-xl text-xs text-center">${r.event_type === 'off_day' ? 'No Class Today' : 'Link not available yet'}</div>`
                        }
                    </div>`;
                }).join('');
            } catch (err) {
                container.innerHTML = `<div class="col-span-full text-center text-red-400 py-8">Failed to load live classes.</div>`;
            }
        }

        // ── ADMIN COURSES & TEACHER ASSIGNMENT ────────────────────────────────
        let _adminTeachersList = [];
        async function loadAdminCourses() {
            const container = document.getElementById('admin-courses-container');
            container.innerHTML = `<div class="p-8 text-center text-gray-400">Loading courses...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/admin/courses/`);
                const data = await res.json();
                _adminTeachersList = data.teachers || [];
                const courses = data.courses || [];
                const categories = data.categories || [];

                // Populate create-course form dropdowns
                const catSel = document.getElementById('admin-course-category');
                if (catSel) {
                    catSel.innerHTML = '<option value="">-- Select Category --</option>' + categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
                }
                const teacherSel = document.getElementById('admin-course-teacher');
                if (teacherSel) {
                    teacherSel.innerHTML = '<option value="">-- Select Teacher --</option>' + _adminTeachersList.map(t => `<option value="${t.id}">${t.name} (${t.email})</option>`).join('');
                }

                if (!courses.length) {
                    container.innerHTML = `<div class="p-8 text-center text-gray-500">No courses found.</div>`;
                    return;
                }
                const teacherOptions = _adminTeachersList.map(t => `<option value="${t.id}">${t.name} (${t.email})</option>`).join('');
                container.innerHTML = `
                    <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-gray-50 border-b border-gray-100 text-xs text-gray-400 font-bold uppercase">
                                <th class="p-4">Course</th>
                                <th class="p-4">Category</th>
                                <th class="p-4 text-right">Price</th>
                                <th class="p-4 text-center">Students</th>
                                <th class="p-4">Instructor</th>
                                <th class="p-4">Assign Teacher</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-sm">
                            ${courses.map(c => `
                            <tr class="hover:bg-gray-50">
                                <td class="p-4 min-w-[160px]">
                                    <p class="font-semibold text-gray-900">${c.title}</p>
                                    <span class="text-xs ${c.is_active ? 'text-emerald-500' : 'text-red-400'}">${c.is_active ? '● Active' : '● Inactive'}</span>
                                </td>
                                <td class="p-4 text-xs text-gray-500">${c.category || '—'}</td>
                                <td class="p-4 text-right font-bold text-emerald-600">৳${Number(c.price || 0).toLocaleString()}</td>
                                <td class="p-4 text-center font-bold text-gray-900">${c.enrollment_count}</td>
                                <td class="p-4 text-xs text-gray-700">${c.instructor ? `${c.instructor.name}<br><span class="text-gray-400">${c.instructor.email}</span>` : '<span class="text-gray-400">Unassigned</span>'}</td>
                                <td class="p-4 min-w-[200px]">
                                    <div class="flex items-center gap-2">
                                        <select id="course-teacher-select-${c.id}" class="border border-gray-200 rounded-xl p-2 text-xs focus:outline-none focus:ring-2 focus:ring-primary flex-1">
                                            <option value="">-- Select Teacher --</option>
                                            ${teacherOptions}
                                        </select>
                                        <button onclick="assignTeacher(${c.id})" class="bg-primary hover:bg-violet-700 text-white text-xs font-bold px-3 py-2 rounded-xl transition-colors shrink-0">Assign</button>
                                    </div>
                                </td>
                            </tr>`).join('')}
                        </tbody>
                    </table>
                    </div>`;
            } catch (err) {
                container.innerHTML = `<div class="p-8 text-center text-red-400">Failed to load courses.</div>`;
            }
        }

        // Create Course form submit (admin)
        document.getElementById('form-admin-create-course')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msgEl = document.getElementById('admin-create-course-msg');
            const title = document.getElementById('admin-course-title').value.trim();
            const price = document.getElementById('admin-course-price').value;
            const categoryId = document.getElementById('admin-course-category').value;
            const teacherId = document.getElementById('admin-course-teacher').value;
            const duration = document.getElementById('admin-course-duration').value;
            const desc = document.getElementById('admin-course-desc').value;

            msgEl.className = 'mb-3 text-xs font-medium text-center py-2 rounded-xl bg-blue-50 text-blue-700';
            msgEl.textContent = 'Creating course...';
            msgEl.classList.remove('hidden');

            try {
                const res = await authFetch(`${API_BASE}/admin/courses/`, {
                    method: 'POST',
                    body: JSON.stringify({ title, price, category_id: categoryId || null, teacher_id: teacherId || null, duration_hours: duration, description: desc })
                });
                const data = await res.json();
                if (res.ok) {
                    msgEl.className = 'mb-3 text-xs font-medium text-center py-2 rounded-xl bg-emerald-50 text-emerald-700';
                    msgEl.textContent = data.message || 'Course created successfully!';
                    document.getElementById('form-admin-create-course').reset();
                    loadAdminCourses(); // refresh the list
                } else {
                    msgEl.className = 'mb-3 text-xs font-medium text-center py-2 rounded-xl bg-red-50 text-red-600';
                    msgEl.textContent = data.error || 'Failed to create course.';
                }
            } catch (err) {
                msgEl.className = 'mb-3 text-xs font-medium text-center py-2 rounded-xl bg-red-50 text-red-600';
                msgEl.textContent = 'Network error.';
            }
        });

        async function assignTeacher(courseId) {
            const select = document.getElementById(`course-teacher-select-${courseId}`);
            const teacherId = select.value;
            if (!teacherId) { alert('Please select a teacher first.'); return; }
            const msg = document.getElementById('admin-courses-msg');
            try {
                const res = await authFetch(`${API_BASE}/admin/courses/${courseId}/assign-teacher/`, {
                    method: 'POST',
                    body: JSON.stringify({ teacher_id: teacherId })
                });
                const data = await res.json();
                msg.className = `mb-4 text-xs font-medium text-center py-2 rounded-xl ${res.ok ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`;
                msg.textContent = data.message || data.error;
                msg.classList.remove('hidden');
                if (res.ok) loadAdminCourses();
                setTimeout(() => msg.classList.add('hidden'), 4000);
            } catch (e) { alert('Assignment failed.'); }
        }

        // ── ADMIN USERS LIST ──────────────────────────────────────────────────
        async function loadAdminUsersList() {
            const container = document.getElementById('admin-users-list-container');
            container.innerHTML = `<div class="p-8 text-center text-gray-400">Loading users...</div>`;
            try {
                const res = await authFetch(`${API_BASE}/admin/users/`);
                const users = await res.json();
                if (!users.length) {
                    container.innerHTML = `<div class="p-8 text-center text-gray-500">No users found.</div>`;
                    return;
                }
                const roleBadge = (role) => {
                    if (role === 'admin') return '<span class="bg-red-100 text-red-700 text-xs font-bold px-2.5 py-0.5 rounded-full">ADMIN</span>';
                    if (role === 'teacher') return '<span class="bg-emerald-100 text-emerald-700 text-xs font-bold px-2.5 py-0.5 rounded-full">TEACHER</span>';
                    return '<span class="bg-violet-100 text-violet-700 text-xs font-bold px-2.5 py-0.5 rounded-full">STUDENT</span>';
                };
                container.innerHTML = `
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-gray-50 border-b border-gray-100 text-xs text-gray-400 font-bold uppercase">
                                <th class="p-4">User</th>
                                <th class="p-4 text-center">Role</th>
                                <th class="p-4">Joined</th>
                                <th class="p-4">Change Role</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-sm">
                            ${users.map(u => `
                            <tr class="hover:bg-gray-50">
                                <td class="p-4">
                                    <p class="font-semibold text-gray-900">${u.name}</p>
                                    <p class="text-xs text-gray-400">${u.email}</p>
                                </td>
                                <td class="p-4 text-center">${roleBadge(u.role)}</td>
                                <td class="p-4 text-xs text-gray-500">${new Date(u.date_joined).toLocaleDateString()}</td>
                                <td class="p-4">
                                    <div class="flex items-center gap-2">
                                        <select id="user-role-select-${u.id}" class="border border-gray-200 rounded-xl p-2 text-xs focus:outline-none focus:ring-2 focus:ring-primary">
                                            <option value="student" ${u.role === 'student' ? 'selected' : ''}>Student</option>
                                            <option value="teacher" ${u.role === 'teacher' ? 'selected' : ''}>Teacher</option>
                                            <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
                                        </select>
                                        <button onclick="updateUserRole(${u.id})" class="bg-gray-900 hover:bg-primary text-white text-xs font-bold px-3 py-2 rounded-xl transition-colors shrink-0">Update</button>
                                    </div>
                                </td>
                            </tr>`).join('')}
                        </tbody>
                    </table>`;
            } catch (err) {
                container.innerHTML = `<div class="p-8 text-center text-red-400">Failed to load users.</div>`;
            }
        }

        async function updateUserRole(userId) {
            const select = document.getElementById(`user-role-select-${userId}`);
            const role = select.value;
            const msg = document.getElementById('admin-users-msg');
            try {
                const res = await authFetch(`${API_BASE}/admin/users/role/`, {
                    method: 'POST',
                    body: JSON.stringify({ user_id: userId, role })
                });
                const data = await res.json();
                msg.className = `mb-4 text-xs font-medium text-center py-2 rounded-xl ${res.ok ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`;
                msg.textContent = data.message || data.error;
                msg.classList.remove('hidden');
                if (res.ok) loadAdminUsersList();
                setTimeout(() => msg.classList.add('hidden'), 4000);
            } catch (e) { alert('Role update failed.'); }
        }

        // Load dashboard data on ready
        loadDashboard();
    