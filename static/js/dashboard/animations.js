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
        // This is a high-frequency operational screen. Cards and data should be
        // immediately readable instead of arriving as a decorative sequence.
        sections.forEach(section => {
            section.style.opacity = '1';
            section.style.transform = 'none';
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

        // The drawer's CSS opacity transition is deliberately small and
        // interruptible; dashboard content itself remains stationary.
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
