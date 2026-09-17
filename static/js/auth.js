(() => {
    const input = document.getElementById('passwordInput');
    const toggle = document.getElementById('passwordToggle');
    if (!input || !toggle) return;

    const icon = toggle.querySelector('i');
    toggle.addEventListener('click', () => {
        const willShow = input.type === 'password';
        input.type = willShow ? 'text' : 'password';
        toggle.setAttribute('aria-pressed', String(willShow));
        toggle.setAttribute('aria-label', willShow ? 'Hide password' : 'Show password');
        icon?.classList.toggle('fa-eye', !willShow);
        icon?.classList.toggle('fa-eye-slash', willShow);
        input.focus({ preventScroll: true });
    });
})();
