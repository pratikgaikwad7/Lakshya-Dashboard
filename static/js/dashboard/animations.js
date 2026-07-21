(function () {
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    let scrollTriggerRegistered = false;
    let sidebarResizeTimer = null;

    function hasGsap() {
        return Boolean(window.gsap);
    }

    function prepareGsap() {
        if (!hasGsap() || scrollTriggerRegistered) return;
        if (window.ScrollTrigger) {
            window.gsap.registerPlugin(window.ScrollTrigger);
        }
        scrollTriggerRegistered = true;
    }

    function formatAnimatedValue(value, decimals, prefix, suffix) {
        const formatted = decimals > 0
            ? value.toLocaleString(undefined, {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            })
            : Math.round(value).toLocaleString();
        return `${prefix}${formatted}${suffix}`;
    }

    function animateNumber(element, fromValue) {
        if (!element || element.dataset.counting === 'true') return;
        const raw = element.textContent.trim();
        const match = raw.match(/^([^\d-]*)(-?[\d,]+(?:\.\d+)?)(.*)$/);
        if (!match) return;

        const target = Number(match[2].replace(/,/g, ''));
        if (!Number.isFinite(target)) return;
        const decimals = (match[2].split('.')[1] || '').length;
        const prefix = match[1];
        const suffix = match[3];
        const start = Number.isFinite(fromValue) ? fromValue : 0;

        if (start === target) {
            element.textContent = raw;
            return;
        }

        if (reducedMotionQuery.matches || !hasGsap()) {
            element.textContent = formatAnimatedValue(target, decimals, prefix, suffix);
            return;
        }

        element.dataset.counting = 'true';
        const state = { value: start };
        window.gsap.to(state, {
            value: target,
            duration: 0.85,
            ease: 'power2.out',
            overwrite: true,
            onUpdate() {
                element.textContent = formatAnimatedValue(state.value, decimals, prefix, suffix);
            },
            onComplete() {
                element.textContent = raw;
                delete element.dataset.counting;
            }
        });
    }

    function initSections(root) {
        const container = root || document;
        const sections = Array.from(container.querySelectorAll('.dashboard-animate-section'))
            .filter(section => !section.classList.contains('hidden'));
        if (!sections.length || reducedMotionQuery.matches || !hasGsap()) {
            sections.forEach(section => {
                section.style.opacity = '1';
                section.style.transform = 'none';
            });
            return;
        }

        prepareGsap();
        const topCards = sections.filter(section => section.classList.contains('dashboard-top-card'));
        if (topCards.length) {
            window.gsap.fromTo(topCards,
                { y: 12, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.52, stagger: 0.07, ease: 'power2.out', clearProps: 'transform,opacity' }
            );
        }

        sections.filter(section => !section.classList.contains('dashboard-top-card')).forEach(section => {
            if (!window.ScrollTrigger) {
                window.gsap.fromTo(section, { y: 16, opacity: 0 }, {
                    y: 0, opacity: 1, duration: 0.55, ease: 'power2.out', clearProps: 'transform,opacity'
                });
                return;
            }
            window.gsap.fromTo(section, { y: 16, opacity: 0 }, {
                scrollTrigger: {
                    trigger: section,
                    scroller: container.id === 'mainContent' ? container : undefined,
                    start: 'top 88%',
                    once: true
                },
                y: 0,
                opacity: 1,
                duration: 0.55,
                ease: 'power2.out',
                clearProps: 'transform,opacity'
            });
        });
    }

    function animateKpis(root, previousValues) {
        const elements = Array.from((root || document).querySelectorAll('[data-kpi-value]'));
        elements.forEach((element, index) => {
            const previous = previousValues && previousValues[index];
            animateNumber(element, previous);
        });
    }

    function readKpiValues(root) {
        return Array.from((root || document).querySelectorAll('[data-kpi-value]')).map(element => {
            const value = Number(element.textContent.replace(/[^\d.-]/g, ''));
            return Number.isFinite(value) ? value : 0;
        });
    }

    function setSidebarOpen(isOpen) {
        const sidebar = document.getElementById('filterSidebar');
        const toggle = document.getElementById('filterToggleButton');
        const backdrop = document.getElementById('sidebarBackdrop');
        if (!sidebar) return;

        sidebar.classList.toggle('open', isOpen);
        sidebar.setAttribute('aria-hidden', String(!isOpen));
        if (toggle) toggle.setAttribute('aria-expanded', String(isOpen));
        if (backdrop) backdrop.classList.toggle('visible', isOpen && window.innerWidth <= 768);

        window.clearTimeout(sidebarResizeTimer);
        sidebarResizeTimer = window.setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
            refresh();
        }, reducedMotionQuery.matches ? 0 : 320);

        if (reducedMotionQuery.matches || !hasGsap()) return;
        window.gsap.killTweensOf(sidebar.querySelector('.sidebar-content'));
        window.gsap.fromTo(sidebar.querySelector('.sidebar-content'),
            { opacity: isOpen ? 0 : 1, y: isOpen ? 6 : 0 },
            { opacity: isOpen ? 1 : 0, y: 0, duration: 0.28, ease: 'power2.out', overwrite: true }
        );
    }

    function refresh() {
        if (window.ScrollTrigger) window.ScrollTrigger.refresh();
    }

    window.DashboardAnimations = {
        animateKpis,
        initSections,
        readKpiValues,
        refresh,
        setSidebarOpen
    };
}());
