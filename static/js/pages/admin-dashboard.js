(function () {
    const sidebar = document.getElementById('adminSidebar');
    const openButton = document.getElementById('adminSidebarOpen');
    const closeButton = document.getElementById('adminSidebarClose');
    const backdrop = document.getElementById('adminSidebarBackdrop');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function setSidebar(open) {
        sidebar.classList.toggle('is-open', open);
        backdrop.classList.toggle('is-visible', open);
        openButton.setAttribute('aria-expanded', String(open));
        document.body.classList.toggle('overflow-hidden', open);
    }

    openButton.addEventListener('click', () => setSidebar(true));
    closeButton.addEventListener('click', () => setSidebar(false));
    backdrop.addEventListener('click', () => setSidebar(false));
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') setSidebar(false);
    });

    if (!window.gsap || reducedMotion) return;

    window.gsap.from('.admin-topbar', {
        autoAlpha: 0,
        y: -12,
        duration: 0.55,
        ease: 'power3.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.from('.admin-nav__link', {
        autoAlpha: 0,
        x: -14,
        duration: 0.48,
        stagger: 0.055,
        ease: 'power2.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.from('.admin-hero__content > *', {
        autoAlpha: 0,
        y: 22,
        duration: 0.72,
        stagger: 0.09,
        ease: 'power3.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.from('.admin-stat-card', {
        autoAlpha: 0,
        y: 24,
        duration: 0.7,
        stagger: 0.1,
        delay: 0.2,
        ease: 'power3.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.from('.admin-action-card', {
        autoAlpha: 0,
        y: 20,
        duration: 0.62,
        stagger: 0.08,
        delay: 0.38,
        ease: 'power3.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.to('.admin-hero__aurora--one', {
        xPercent: -10,
        yPercent: 8,
        duration: 8,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
    });

    window.gsap.to('.admin-hero__aurora--two', {
        xPercent: 12,
        yPercent: -7,
        duration: 10,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
    });
}());
