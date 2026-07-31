        // Toggle Sidebar Logic
        function toggleSidebar(forceOpen) {
            const sidebar = document.getElementById('filterSidebar');
            const overlay = document.getElementById('overlay');
            const toggle = document.getElementById('evaluationFilterToggle');
            const shouldOpen = typeof forceOpen === 'boolean'
                ? forceOpen
                : sidebar.classList.contains('sidebar-closed');
            
            if (shouldOpen) {
                // Open Sidebar
                sidebar.classList.remove('sidebar-closed');
                sidebar.classList.add('sidebar-open');
                sidebar.setAttribute('aria-hidden', 'false');
                if (toggle) toggle.setAttribute('aria-expanded', 'true');
                
                // Show Overlay
                overlay.classList.remove('hidden');
                setTimeout(() => {
                    overlay.classList.remove('opacity-0');
                    overlay.classList.add('opacity-100');
                }, 10);
            } else {
                // Close Sidebar
                sidebar.classList.remove('sidebar-open');
                sidebar.classList.add('sidebar-closed');
                sidebar.setAttribute('aria-hidden', 'true');
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
                
                // Hide Overlay
                overlay.classList.remove('opacity-100');
                overlay.classList.add('opacity-0');
                setTimeout(() => {
                    overlay.classList.add('hidden');
                }, 300);
            }
        }

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') toggleSidebar(false);
        });

        document.addEventListener('DOMContentLoaded', function() {
            const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (!window.gsap || reducedMotion) return;

            window.gsap.from('.evaluation-list-header__left > *, .evaluation-list-header__actions > *', {
                autoAlpha: 0,
                y: -8,
                duration: 0.48,
                stagger: 0.045,
                ease: 'power2.out',
                clearProps: 'opacity,transform,visibility'
            });

            window.gsap.from('.evaluation-data-card', {
                autoAlpha: 0,
                y: 14,
                duration: 0.58,
                ease: 'power3.out',
                clearProps: 'opacity,transform,visibility'
            });

            window.gsap.from('.evaluation-data-row', {
                autoAlpha: 0,
                y: 8,
                duration: 0.42,
                stagger: 0.025,
                delay: 0.12,
                ease: 'power2.out',
                clearProps: 'opacity,transform,visibility'
            });

            window.gsap.to('.evaluation-list-header__aurora--one', {
                xPercent: -8,
                duration: 8,
                repeat: -1,
                yoyo: true,
                ease: 'sine.inOut'
            });
        });
