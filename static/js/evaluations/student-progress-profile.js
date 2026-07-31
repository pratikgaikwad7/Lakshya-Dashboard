(function () {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function showSemester(button, options = {}) {
        const targetId = button.dataset.semesterTarget;
        const targetPanel = document.getElementById(targetId);
        if (!targetPanel) return;

        document.querySelectorAll('[data-semester-target]').forEach(item => {
            item.setAttribute('aria-selected', String(item === button));
        });
        document.querySelectorAll('[data-semester-panel]').forEach(panel => {
            panel.hidden = panel !== targetPanel;
        });

        const semesterNumber = targetId.replace('semester-', '');
        const label = document.getElementById('selectedSemesterLabel');
        if (label) label.textContent = `Semester ${semesterNumber}`;
        window.history.replaceState(null, '', `#${targetId}`);

        if (window.gsap && !reducedMotion) {
            gsap.fromTo(
                targetPanel,
                { y: 20, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.48, ease: 'power3.out', clearProps: 'transform,opacity' }
            );
        }

        if (options.scroll !== false) {
            document.getElementById('semesterRecords')?.scrollIntoView({
                behavior: reducedMotion ? 'auto' : 'smooth',
                block: 'start'
            });
        }
    }

    function initSemesterSelection() {
        const buttons = Array.from(document.querySelectorAll('[data-semester-target]'));
        if (!buttons.length) return;

        buttons.forEach(button => {
            button.addEventListener('click', () => showSemester(button));
        });

        const hashTarget = window.location.hash.replace('#', '');
        const hashButton = hashTarget
            ? buttons.find(button => button.dataset.semesterTarget === hashTarget)
            : null;
        const selectedButton = buttons.find(
            button => button.getAttribute('aria-selected') === 'true'
        );
        showSemester(hashButton || selectedButton || buttons[buttons.length - 1], {
            scroll: false
        });
    }

    function initMotion() {
        if (!window.gsap || !window.ScrollTrigger || reducedMotion) return;

        gsap.registerPlugin(ScrollTrigger);

        gsap.from('.profile-reveal', {
            y: 28,
            opacity: 0,
            duration: 0.9,
            stagger: 0.14,
            ease: 'power3.out'
        });

        gsap.utils.toArray('.scroll-reveal').forEach(section => {
            gsap.from(section, {
                y: 42,
                opacity: 0,
                duration: 0.8,
                ease: 'power3.out',
                scrollTrigger: {
                    trigger: section,
                    start: 'top 88%',
                    once: true
                }
            });
        });

        gsap.to('.ambient-orb--one', {
            yPercent: 28,
            xPercent: -8,
            ease: 'none',
            scrollTrigger: {
                trigger: '.profile-hero',
                start: 'top top',
                end: 'bottom top',
                scrub: 0.8
            }
        });

        gsap.to('.ambient-orb--two', {
            yPercent: -20,
            xPercent: 10,
            ease: 'none',
            scrollTrigger: {
                trigger: '.profile-hero',
                start: 'top top',
                end: 'bottom top',
                scrub: 0.8
            }
        });

        ScrollTrigger.create({
            start: 0,
            end: 'max',
            onUpdate(self) {
                gsap.set('#pageScrollProgress', { scaleX: self.progress });
            }
        });
    }

    function initFallbackScrollProgress() {
        if (!reducedMotion) return;
        const progress = document.getElementById('pageScrollProgress');
        if (!progress) return;

        window.addEventListener('scroll', () => {
            const scrollRange = document.documentElement.scrollHeight - window.innerHeight;
            const ratio = scrollRange > 0 ? window.scrollY / scrollRange : 0;
            progress.style.transform = `scaleX(${ratio})`;
        }, { passive: true });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initSemesterSelection();
        initMotion();
        initFallbackScrollProgress();
    });
}());
