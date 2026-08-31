/**
 * TutorBhaiya — Global Script
 * Handles: Navbar scroll, mobile menu, FAQ, auth state, navbar UI
 */

const API_BASE = (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:'))
    ? 'http://127.0.0.1:8000/api'
    : 'https://tutor-bhaiya.onrender.com/api';

function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ─── Auth Helpers ─────────────────────────────────────────────────────────────

function getToken() {
    return localStorage.getItem('token') || null;
}

function getUser() {
    try {
        const u = localStorage.getItem('user');
        return u ? JSON.parse(u) : null;
    } catch (e) {
        return null;
    }
}

function isLoggedIn() {
    return !!(getToken() && getUser());
}

function clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    for (const cookie of cookies) {
        const [cookieName, ...rest] = cookie.split('=');
        if (cookieName === name) {
            return decodeURIComponent(rest.join('='));
        }
    }
    return '';
}

// ─── Fetch with Auth ──────────────────────────────────────────────────────────

async function authFetch(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(options.headers || {}),
    };
    if (token) headers['Authorization'] = `Token ${token}`;
    return fetch(url, { ...options, headers, credentials: 'include' });
}

// ─── Logout ───────────────────────────────────────────────────────────────────

async function logout() {
    try {
        const csrfRes = await fetch(`${API_BASE}/csrf/`);
        const { csrfToken } = await csrfRes.json();
        const token = getToken();
        const headers = { 'X-CSRFToken': csrfToken };
        if (token) headers['Authorization'] = `Token ${token}`;
        await fetch(`${API_BASE}/auth/logout/`, {
            method: 'POST',
            headers,
            credentials: 'include'
        });
    } catch (err) {
        console.warn('Logout API error (clearing local anyway):', err);
    }
    clearAuth();
    window.location.href = 'index.html';
}

// ─── Update Navbar for Auth State ─────────────────────────────────────────────

function updateNavbarAuth() {
    const user = getUser();
    const loggedIn = isLoggedIn();

    // Select the auth button (could be login.html link or profile.html button)
    const authBtn = document.getElementById('user-avatar-btn') || 
                    document.querySelector('a[href="login.html"].bg-secondary, a[href="login.html"].bg-primary');
    const dashboardLink = document.querySelector('a[href="dashboard.html"].nav-link');

    if (loggedIn && user) {
        const initial = user.avatar_initial || (user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U');
        const displayName = user.full_name ? user.full_name.split(' ')[0] : 'Profile';
        
        let avatarHtml = `<div class="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">${initial}</div>`;
        if (user.profile_picture) {
            avatarHtml = `<img src="${user.profile_picture}" class="w-6 h-6 rounded-full object-cover flex-shrink-0">`;
        }

        if (authBtn) {
            authBtn.id = 'user-avatar-btn';
            authBtn.href = 'profile.html';
            authBtn.innerHTML = `
                <div class="flex items-center gap-2">
                    ${avatarHtml}
                    <span>${displayName}</span>
                </div>`;
            authBtn.classList.remove('bg-secondary', 'hover:bg-emerald-600', 'shadow-secondary/30', 'hover:shadow-secondary/50');
            authBtn.classList.add('bg-primary', 'hover:bg-violet-700');
        }

        // Show Dashboard nav link
        if (dashboardLink) dashboardLink.style.display = '';

        // Wire all logout buttons on the page
        document.querySelectorAll('#logout-btn, .logout-trigger').forEach(btn => {
            btn.addEventListener('click', (e) => { e.preventDefault(); logout(); });
        });

        // Mobile menu: if Login link exists, turn it into Profile
        document.querySelectorAll('#mobile-menu a[href="login.html"]').forEach(el => {
            el.href = 'profile.html';
            el.textContent = 'My Profile';
        });

    } else {
        // Not logged in: hide Dashboard link
        if (dashboardLink) dashboardLink.style.display = 'none';
        
        // If we have an avatar button but are not logged in, reset to login
        if (authBtn && authBtn.id === 'user-avatar-btn') {
            authBtn.href = 'login.html';
            authBtn.innerHTML = `Login`;
            authBtn.classList.remove('bg-primary', 'hover:bg-violet-700');
            authBtn.classList.add('bg-secondary', 'hover:bg-emerald-600');
        }
    }
}

// ─── DOMContentLoaded ─────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {

    // 1. Navbar Scroll Effect & Mobile Menu Logic
    const navbar = document.getElementById('navbar');
    const logoText = document.getElementById('logo-text');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    const isTransparentNavbar = navbar && navbar.classList.contains('bg-transparent');

    if (isTransparentNavbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('bg-white/95', 'backdrop-blur-md', 'shadow-md', 'border-b', 'border-slate-200/50', 'text-slate-700');
                navbar.classList.remove('bg-transparent', 'text-gray-200');
                if (logoText) { logoText.classList.add('text-slate-900'); logoText.classList.remove('text-white'); }
                if (mobileMenuBtn) { mobileMenuBtn.classList.add('text-slate-700'); mobileMenuBtn.classList.remove('text-gray-200'); }
            } else {
                navbar.classList.remove('bg-white/95', 'backdrop-blur-md', 'shadow-md', 'border-b', 'border-slate-200/50', 'text-slate-700');
                navbar.classList.add('bg-transparent', 'text-gray-200');
                if (logoText) { logoText.classList.remove('text-slate-900'); logoText.classList.add('text-white'); }
                if (mobileMenuBtn) { mobileMenuBtn.classList.remove('text-slate-700'); mobileMenuBtn.classList.add('text-gray-200'); }
            }
        });
    }

    // Toggle Mobile Menu
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

    // 2. Swiper (Testimonials)
    if (typeof Swiper !== 'undefined' && document.querySelector('.testimonialSwiper')) {
        new Swiper('.testimonialSwiper', {
            slidesPerView: 1, spaceBetween: 30, loop: true,
            autoplay: { delay: 5000, disableOnInteraction: false },
            pagination: { el: '.swiper-pagination-custom', clickable: true },
            navigation: { nextEl: '.swiper-button-next-custom', prevEl: '.swiper-button-prev-custom' },
        });
    }

    // 3. FAQ Accordion
    document.querySelectorAll('.faq-item').forEach(item => {
        const button = item.querySelector('.faq-button');
        const content = item.querySelector('.faq-content');
        const icon = item.querySelector('.ph-plus');
        if (!button) return;
        button.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            document.querySelectorAll('.faq-item').forEach(other => {
                other.classList.remove('active');
                other.querySelector('.faq-content').style.maxHeight = null;
                other.querySelector('.ph-plus').style.transform = 'rotate(0deg)';
                other.classList.replace('border-primary', 'border-gray-200');
            });
            if (!isActive) {
                item.classList.add('active');
                content.style.maxHeight = content.scrollHeight + 'px';
                icon.style.transform = 'rotate(45deg)';
                item.classList.replace('border-gray-200', 'border-primary');
            }
        });
    });

    // 4. Update navbar auth state on every page
    updateNavbarAuth();

});

