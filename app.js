// Modern SaaS Website Interactive Features
document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Button click effects with ripple animation
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero-content');
        const gradientBg = document.querySelector('.gradient-bg');
        
        if (hero && scrolled < window.innerHeight) {
            hero.style.transform = `translateY(${scrolled * 0.3}px)`;
        }
        
        if (gradientBg && scrolled < window.innerHeight) {
            gradientBg.style.transform = `translateY(${scrolled * 0.1}px)`;
        }
    });

    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.feature-card, .cta-content, .features-header');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Counter animation for hero stats
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        
        function updateCounter() {
            start += increment;
            if (start < target) {
                element.textContent = Math.floor(start) + '+';
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target.toLocaleString() + '+';
            }
        }
        
        updateCounter();
    }

    // Animate hero stats when they come into view
    const heroStats = document.querySelector('.hero-stats');
    if (heroStats) {
        const statObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const statNumbers = entry.target.querySelectorAll('.stat-number');
                    statNumbers.forEach(stat => {
                        const text = stat.textContent;
                        const number = parseInt(text.replace(/[^\d]/g, ''));
                        if (number) {
                            animateCounter(stat, number);
                        }
                    });
                    statObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        statObserver.observe(heroStats);
    }

    // Dynamic gradient background
    function createGradientAnimation() {
        const gradients = [
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
        ];
        
        let currentIndex = 0;
        const gradientBg = document.querySelector('.gradient-bg');
        
        if (gradientBg) {
            setInterval(() => {
                currentIndex = (currentIndex + 1) % gradients.length;
                gradientBg.style.background = gradients[currentIndex];
            }, 10000);
        }
    }

    // Initialize gradient animation
    createGradientAnimation();

    // Typing effect for hero title
    function typeWriter(element, text, speed = 80) {
        let i = 0;
        element.innerHTML = '';
        
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }

    // Apply typing effect to hero title
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const originalText = heroTitle.textContent;
        setTimeout(() => {
            typeWriter(heroTitle, originalText, 80);
        }, 500);
    }

    // Mobile menu toggle (for future mobile optimization)
    const mobileMenuToggle = document.createElement('button');
    mobileMenuToggle.innerHTML = '☰';
    mobileMenuToggle.classList.add('mobile-menu-toggle');
    mobileMenuToggle.style.cssText = `
        display: none;
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.5rem;
    `;

    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.appendChild(mobileMenuToggle);
        
        mobileMenuToggle.addEventListener('click', function() {
            const navLinks = document.querySelector('.nav-links');
            const navButtons = document.querySelector('.nav-buttons');
            
            if (navLinks && navButtons) {
                const isVisible = navLinks.style.display === 'flex';
                navLinks.style.display = isVisible ? 'none' : 'flex';
                navButtons.style.display = isVisible ? 'none' : 'flex';
            }
        });
    }

    // Show/hide mobile menu based on screen size
    function handleMobileMenu() {
        const navLinks = document.querySelector('.nav-links');
        const navButtons = document.querySelector('.nav-buttons');
        
        if (window.innerWidth <= 768) {
            mobileMenuToggle.style.display = 'block';
            if (navLinks && navButtons) {
                navLinks.style.display = 'none';
                navButtons.style.display = 'none';
            }
        } else {
            mobileMenuToggle.style.display = 'none';
            if (navLinks && navButtons) {
                navLinks.style.display = 'flex';
                navButtons.style.display = 'flex';
            }
        }
    }

    // Handle resize events
    window.addEventListener('resize', handleMobileMenu);
    handleMobileMenu(); // Initial call

    // Add ripple effect styles
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .btn {
            position: relative;
            overflow: hidden;
        }
        
        .mobile-menu-toggle {
            display: none;
        }
        
        @media (max-width: 768px) {
            .mobile-menu-toggle {
                display: block !important;
            }
            
            .nav-links,
            .nav-buttons {
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: rgba(102, 126, 234, 0.95);
                backdrop-filter: blur(10px);
                flex-direction: column;
                padding: 1rem;
                border-radius: 10px;
                margin-top: 1rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            }
            
            .nav-links {
                gap: 1rem;
            }
            
            .nav-buttons {
                gap: 0.5rem;
            }
        }
    `;
    document.head.appendChild(style);

    // Form handling (if forms are added later)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Add loading state
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.textContent;
                submitButton.innerHTML = 'Loading...';
                submitButton.disabled = true;
                
                setTimeout(() => {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 2000);
            }
        });
    });

    console.log('🚀 Modern SaaS website initialized successfully!');
    console.log('✨ Features loaded: Smooth scrolling, parallax effects, counter animations, dynamic gradients');
});