(function () {
    let dashboardRequestController = null;

    function setApplyButtonLoading(isLoading) {
        const button = document.getElementById('applyFiltersButton');
        if (!button) return;
        button.disabled = isLoading;
        button.classList.toggle('is-loading', isLoading);
        button.setAttribute('aria-busy', String(isLoading));
        const icon = button.querySelector('i');
        if (icon) {
            icon.className = isLoading ? 'fas fa-circle-notch' : 'fas fa-check-circle';
        }
    }

    async function refreshDashboard(url) {
        if (dashboardRequestController) dashboardRequestController.abort();
        const requestController = new AbortController();
        dashboardRequestController = requestController;
        const currentMain = document.getElementById('mainContent');
        const previousKpis = window.DashboardAnimations
            ? window.DashboardAnimations.readKpiValues(currentMain)
            : [];

        if (currentMain) currentMain.classList.add('dashboard-refreshing');
        setApplyButtonLoading(true);

        try {
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
                signal: requestController.signal
            });
            if (!response.ok) throw new Error(`Dashboard request failed (${response.status})`);

            const documentText = await response.text();
            const nextDocument = new DOMParser().parseFromString(documentText, 'text/html');
            const nextMain = nextDocument.getElementById('mainContent');
            const nextSummary = nextDocument.getElementById('activeFilterSummary');
            if (!nextMain) throw new Error('Dashboard response was incomplete.');

            if (typeof destroyDashboardCharts === 'function') destroyDashboardCharts();
            currentMain.replaceWith(nextMain);

            const currentSummary = document.getElementById('activeFilterSummary');
            if (currentSummary && nextSummary) currentSummary.replaceWith(nextSummary);

            window.history.pushState({}, '', url);
            if (typeof initializeDashboardContent === 'function') {
                initializeDashboardContent({ previousKpis });
            }
            if (typeof toggleSidebar === 'function') toggleSidebar(false);
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Unable to refresh dashboard filters:', error);
                if (window.DashboardLoading) {
                    window.DashboardLoading.showToast('Dashboard filters could not be refreshed. Please try again.');
                }
            }
        } finally {
            if (dashboardRequestController === requestController) {
                const activeMain = document.getElementById('mainContent');
                if (activeMain) activeMain.classList.remove('dashboard-refreshing');
                setApplyButtonLoading(false);
                dashboardRequestController = null;
            }
        }
    }

    function submitFilters(form) {
        const query = new URLSearchParams(new FormData(form));
        const url = `${form.action}?${query.toString()}`;
        refreshDashboard(url);
    }

    function init() {
        const form = document.getElementById('dashboardFilterForm');
        if (!form || form.dataset.liveBound === 'true') return;
        form.dataset.liveBound = 'true';
        form.addEventListener('submit', event => {
            event.preventDefault();
            submitFilters(form);
        });

        const ticketInput = form.querySelector('[name="ticket_no"]');
        if (ticketInput) {
            let debounceTimer = null;
            ticketInput.addEventListener('input', () => {
                window.clearTimeout(debounceTimer);
                debounceTimer = window.setTimeout(() => submitFilters(form), 450);
            });
        }

        const reset = form.querySelector('.filter-reset-button');
        if (reset) {
            reset.addEventListener('click', event => {
                event.preventDefault();
                form.reset();
                form.querySelectorAll('input[type="checkbox"]').forEach(input => {
                    input.checked = false;
                });
                form.querySelectorAll('[id^="btn_label_"]').forEach(label => {
                    label.textContent = 'All';
                });
                refreshDashboard(reset.href);
            });
        }
    }

    window.addEventListener('popstate', () => window.location.reload());
    document.addEventListener('DOMContentLoaded', init);
    window.DashboardLiveUpdates = { init, refreshDashboard };
}());
