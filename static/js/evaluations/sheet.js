function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function calculateTotal() {
    const totalScoreDisplay = document.getElementById('totalScoreDisplay');
    let total = 0;

    document.querySelectorAll('#editForm input[name^="score_"]:not([disabled])').forEach(input => {
        const value = Number.parseFloat(input.value);
        if (!Number.isNaN(value)) {
            total += value;
        }
    });

    if (totalScoreDisplay) {
        totalScoreDisplay.textContent = total;
    }
}

function animateEvaluationCard(target) {
    if (!target || !window.gsap || prefersReducedMotion()) {
        return;
    }

    window.gsap.fromTo(
        target,
        { autoAlpha: 0, y: 24 },
        {
            autoAlpha: 1,
            y: 0,
            duration: 0.52,
            ease: 'power3.out',
            clearProps: 'opacity,transform,visibility'
        }
    );
}

function toggleEditMode() {
    const viewMode = document.getElementById('viewMode');
    const editMode = document.getElementById('editForm');
    const showViewMode = viewMode.classList.contains('hidden');
    const visibleCard = showViewMode ? viewMode : editMode;

    viewMode.classList.toggle('hidden', !showViewMode);
    editMode.classList.toggle('hidden', showViewMode);

    if (!showViewMode) {
        calculateTotal();
    }

    window.requestAnimationFrame(() => {
        animateEvaluationCard(visibleCard);
        document.getElementById('semesterRecords')?.scrollIntoView({
            behavior: prefersReducedMotion() ? 'auto' : 'smooth',
            block: 'start'
        });

        if (window.ScrollTrigger) {
            window.ScrollTrigger.refresh();
        }
    });
}

function updateSheetScrollProgress() {
    const progress = document.getElementById('sheetScrollProgress');
    const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = scrollableHeight > 0 ? Math.min(window.scrollY / scrollableHeight, 1) : 0;

    if (progress) {
        progress.style.transform = `scaleX(${ratio})`;
    }
}

function initSheetMotion() {
    updateSheetScrollProgress();

    if (!window.gsap || !window.ScrollTrigger || prefersReducedMotion()) {
        window.addEventListener('scroll', updateSheetScrollProgress, { passive: true });
        return;
    }

    window.gsap.registerPlugin(window.ScrollTrigger);

    window.gsap.from('.evaluation-nav .profile-back-link', {
        autoAlpha: 0,
        x: -16,
        duration: 0.58,
        ease: 'power3.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.from('.evaluation-nav__actions > *', {
        autoAlpha: 0,
        x: 16,
        duration: 0.58,
        stagger: 0.07,
        ease: 'power3.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.utils.toArray('.scroll-reveal').forEach(section => {
        window.gsap.from(section, {
            autoAlpha: 0,
            y: 36,
            duration: 0.76,
            ease: 'power3.out',
            clearProps: 'opacity,transform,visibility',
            scrollTrigger: {
                trigger: section,
                start: 'top 90%',
                once: true
            }
        });
    });

    window.gsap.from('.semester-track li', {
        y: 14,
        duration: 0.44,
        stagger: 0.055,
        ease: 'power2.out',
        clearProps: 'transform',
        scrollTrigger: {
            trigger: '.semester-track',
            start: 'top 88%',
            once: true
        }
    });

    window.gsap.from('#viewMode .semester-score', {
        y: 16,
        duration: 0.48,
        stagger: 0.07,
        ease: 'power2.out',
        clearProps: 'transform',
        scrollTrigger: {
            trigger: '#viewMode .semester-score-grid',
            start: 'top 88%',
            once: true
        }
    });

    window.gsap.from('#viewMode .ojt-metric', {
        y: 14,
        duration: 0.42,
        stagger: 0.045,
        ease: 'power2.out',
        clearProps: 'transform',
        scrollTrigger: {
            trigger: '#viewMode .ojt-metric-grid',
            start: 'top 88%',
            once: true
        }
    });

    window.gsap.to('#sheetScrollProgress', {
        scaleX: 1,
        ease: 'none',
        scrollTrigger: {
            trigger: document.documentElement,
            start: 'top top',
            end: 'bottom bottom',
            scrub: 0.25
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    calculateTotal();
    initSheetMotion();
});
