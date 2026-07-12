document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Navbar Scroll Effect & Mobile Menu Logic
    const navbar = document.getElementById('navbar');
    const logoText = document.getElementById('logo-text');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Check if the current page has a transparent/dark navbar by default (e.g. index.html)
    const isTransparentNavbar = navbar && navbar.classList.contains('bg-transparent');
    
    if (isTransparentNavbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('bg-white/95', 'backdrop-blur-md', 'shadow-md', 'border-b', 'border-slate-200/50', 'text-slate-700');
                navbar.classList.remove('bg-transparent', 'text-gray-200');
                if (logoText) {
                    logoText.classList.add('text-slate-900');
                    logoText.classList.remove('text-white');
                }
                if (mobileMenuBtn) {
                    mobileMenuBtn.classList.add('text-slate-700');
                    mobileMenuBtn.classList.remove('text-gray-200');
                }
            } else {
                navbar.classList.remove('bg-white/95', 'backdrop-blur-md', 'shadow-md', 'border-b', 'border-slate-200/50', 'text-slate-700');
                navbar.classList.add('bg-transparent', 'text-gray-200');
                if (logoText) {
                    logoText.classList.remove('text-slate-900');
                    logoText.classList.add('text-white');
                }
                if (mobileMenuBtn) {
                    mobileMenuBtn.classList.remove('text-slate-700');
                    mobileMenuBtn.classList.add('text-gray-200');
                }
            }
        });
    }

    // Toggle Mobile Menu
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            mobileMenu.classList.toggle('hidden');
        });
        
        // Close mobile menu on clicking anywhere else
        document.addEventListener('click', () => {
            if (!mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.add('hidden');
            }
        });

        mobileMenu.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // 2. Swiper Initialization (Testimonials)
    if (typeof Swiper !== 'undefined' && document.querySelector('.testimonialSwiper')) {
        const swiper = new Swiper('.testimonialSwiper', {
            slidesPerView: 1,
            spaceBetween: 30,
            loop: true,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination-custom',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next-custom',
                prevEl: '.swiper-button-prev-custom',
            },
        });
    }

    // 3. FAQ Accordion Logic
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const button = item.querySelector('.faq-button');
        const content = item.querySelector('.faq-content');
        const icon = item.querySelector('.ph-plus');

        if (button) {
            button.addEventListener('click', () => {
                const isActive = item.classList.contains('active');

                // Close all items
                faqItems.forEach(otherItem => {
                    otherItem.classList.remove('active');
                    otherItem.querySelector('.faq-content').style.maxHeight = null;
                    otherItem.querySelector('.ph-plus').style.transform = 'rotate(0deg)';
                    otherItem.classList.replace('border-primary', 'border-gray-200');
                });

                // Open clicked item if it wasn't active
                if (!isActive) {
                    item.classList.add('active');
                    content.style.maxHeight = content.scrollHeight + "px";
                    icon.style.transform = 'rotate(45deg)';
                    item.classList.replace('border-gray-200', 'border-primary');
                }
            });
        }
    });

    // 4. Global Auth Check for Navbar
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            const loginBtns = document.querySelectorAll('a[href="login.html"]');
            
            loginBtns.forEach(btn => {
                // Desktop button
                if (btn.classList.contains('px-6') || btn.classList.contains('px-5')) {
                    btn.href = 'dashboard.html';
                    btn.innerHTML = `<div class="flex items-center gap-2"><div class="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center text-white text-xs font-bold">${user.avatar_initial || user.full_name.charAt(0).toUpperCase()}</div><span>Dashboard</span></div>`;
                    btn.classList.replace('bg-secondary', 'bg-primary');
                    btn.classList.replace('hover:bg-emerald-600', 'hover:bg-violet-700');
                } 
                // Mobile menu button
                else if (btn.closest('#mobile-menu')) {
                     btn.href = 'dashboard.html';
                     btn.textContent = 'Dashboard';
                }
            });

            // Hide the extra "Dashboard" text link if the login button turned into a Dashboard button
            const navActions = document.querySelector('.hidden.md\\:flex.items-center.space-x-4');
            if (navActions) {
                 const dashboardLink = navActions.querySelector('a[href="dashboard.html"].nav-link');
                 if(dashboardLink) dashboardLink.style.display = 'none';
            }
        } catch(e) {
            console.error("Error parsing user data for navbar", e);
        }
    }

});
