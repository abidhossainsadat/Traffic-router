// RoadPulse - Landing Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            this.classList.toggle('active');
        });
    }

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // Close mobile menu if open
                if (navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    mobileMenuBtn.classList.remove('active');
                }
            }
        });
    });

    // Navbar background on scroll
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.boxShadow = 'none';
        }
        
        lastScroll = currentScroll;
    });

    // Demo Add Route Button Interaction
    const addRouteBtn = document.getElementById('addRouteBtn');
    const routesList = document.getElementById('routesList');
    
    if (addRouteBtn && routesList) {
        addRouteBtn.addEventListener('click', function() {
            // Create a new route card
            const newRoute = document.createElement('div');
            newRoute.className = 'demo-route-card';
            newRoute.style.animation = 'fadeIn 0.3s ease';
            
            const routes = [
                {
                    label: 'Home → Gym',
                    badge: 'Good',
                    badgeClass: 'badge-good',
                    address: '123 Main St → 321 Fitness Ave',
                    threshold: '5 min delay',
                    updated: 'Just now'
                },
                {
                    label: 'Work → Home',
                    badge: 'Heavy',
                    badgeClass: 'badge-heavy',
                    address: '456 Office Blvd → 123 Main St',
                    threshold: '15 min delay',
                    updated: '1 min ago'
                },
                {
                    label: 'School Run',
                    badge: 'Moderate',
                    badgeClass: 'badge-moderate',
                    address: '789 School Lane → 123 Main St',
                    threshold: '8 min delay',
                    updated: '3 mins ago'
                }
            ];
            
            const randomRoute = routes[Math.floor(Math.random() * routes.length)];
            
            newRoute.innerHTML = `
                <div class="route-header">
                    <span class="route-label">${randomRoute.label}</span>
                    <span class="route-badge ${randomRoute.badgeClass}">${randomRoute.badge}</span>
                </div>
                <p class="route-address">${randomRoute.address}</p>
                <div class="route-footer">
                    <span>Alert at: ${randomRoute.threshold}</span>
                    <span>Updated: ${randomRoute.updated}</span>
                </div>
            `;
            
            // Insert after the first route
            routesList.insertBefore(newRoute, routesList.firstChild);
            
            // Limit to 4 routes
            while (routesList.children.length > 4) {
                routesList.removeChild(routesList.lastChild);
            }
            
            // Add animation style if not exists
            if (!document.getElementById('demo-animations')) {
                const style = document.createElement('style');
                style.id = 'demo-animations';
                style.textContent = `
                    @keyframes fadeIn {
                        from {
                            opacity: 0;
                            transform: translateY(-10px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                `;
                document.head.appendChild(style);
            }
        });
    }

    // Intersection Observer for fade-in animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe feature cards and steps
    document.querySelectorAll('.feature-card, .step').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add CSS for fade-in animation
    const fadeStyle = document.createElement('style');
    fadeStyle.textContent = `
        .fade-in-visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(fadeStyle);

    // Dynamic stats counter animation
    const statValues = document.querySelectorAll('.stat-value');
    
    const animateValue = (element, start, end, duration) => {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            
            if (element.textContent.includes('%')) {
                element.textContent = Math.floor(progress * end) + '%';
            } else if (element.textContent.includes('+')) {
                element.textContent = Math.floor(progress * end) + '+';
            } else {
                element.textContent = element.textContent.replace(/\d+/g, Math.floor(progress * end));
            }
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };

    // Trigger animation when stats are visible
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statValue = entry.target;
                const text = statValue.textContent;
                
                if (text.includes('%')) {
                    const endValue = parseInt(text.replace('%', ''));
                    animateValue(statValue, 0, endValue, 2000);
                } else if (text.includes('+')) {
                    const endValue = parseInt(text.replace('+', ''));
                    animateValue(statValue, 0, endValue, 2000);
                }
                
                statsObserver.unobserve(statValue);
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(stat => statsObserver.observe(stat));

    // Add hover effect to demo phone
    const demoPhone = document.querySelector('.demo-phone');
    if (demoPhone) {
        demoPhone.addEventListener('mousemove', (e) => {
            const rect = demoPhone.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            demoPhone.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            demoPhone.style.transition = 'transform 0.1s ease';
        });
        
        demoPhone.addEventListener('mouseleave', () => {
            demoPhone.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
            demoPhone.style.transition = 'transform 0.3s ease';
        });
    }

    console.log('RoadPulse landing page loaded successfully! 🚦');
});
