(function () {
    function sectionElement(section) {
        return typeof section === 'string'
            ? document.querySelector(`[data-dashboard-section="${section}"]`)
            : section;
    }

    function setLoading(section, isLoading) {
        const element = sectionElement(section);
        if (!element) return;
        const shell = element.classList.contains('dashboard-chart-shell')
            ? element
            : element.querySelector('.dashboard-chart-shell');
        const target = shell || element;
        target.classList.toggle('is-loading', isLoading);
        target.setAttribute('aria-busy', String(isLoading));
        if (isLoading) target.classList.remove('is-ready');
    }

    function markReady(section) {
        const element = sectionElement(section);
        if (!element) return;
        const shell = element.classList.contains('dashboard-chart-shell')
            ? element
            : element.querySelector('.dashboard-chart-shell');
        const target = shell || element;
        target.classList.remove('is-loading');
        target.classList.add('is-ready');
        target.setAttribute('aria-busy', 'false');
        const error = target.querySelector('.dashboard-section-error');
        if (error) error.remove();
    }

    function showError(section, message) {
        const element = sectionElement(section);
        if (!element) return;
        const shell = element.classList.contains('dashboard-chart-shell')
            ? element
            : element.querySelector('.dashboard-chart-shell');
        const target = shell || element;
        target.classList.remove('is-loading');
        target.classList.add('is-ready');
        target.setAttribute('aria-busy', 'false');
        let error = target.querySelector('.dashboard-section-error');
        if (!error) {
            error = document.createElement('div');
            error.className = 'dashboard-section-error';
            error.setAttribute('role', 'status');
            target.appendChild(error);
        }
        error.textContent = message;
    }

    function showToast(message) {
        const existing = document.querySelector('.dashboard-toast');
        if (existing) existing.remove();
        const toast = document.createElement('div');
        toast.className = 'dashboard-toast';
        toast.setAttribute('role', 'alert');
        toast.textContent = message;
        document.body.appendChild(toast);
        window.setTimeout(() => toast.remove(), 4500);
    }

    window.DashboardLoading = { setLoading, markReady, showError, showToast };
}());
