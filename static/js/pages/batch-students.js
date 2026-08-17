document.addEventListener('DOMContentLoaded', () => {
    const drawer = document.getElementById('cohortFilters');
    const backdrop = document.getElementById('cohortFilterBackdrop');
    const openButton = document.getElementById('cohortFilterOpen');
    const closeButton = document.getElementById('cohortFilterClose');
    const setOpen = (open) => {
        drawer?.classList.toggle('is-open', open);
        backdrop?.classList.toggle('is-open', open);
        drawer?.setAttribute('aria-hidden', String(!open));
        openButton?.setAttribute('aria-expanded', String(open));
        if (open) drawer?.querySelector('input,select')?.focus();
        else openButton?.focus();
    };
    openButton?.addEventListener('click', () => setOpen(true));
    closeButton?.addEventListener('click', () => setOpen(false));
    backdrop?.addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && drawer?.classList.contains('is-open')) setOpen(false); });

    const filterForm = document.getElementById('studentRecordFilterForm');
    let filterRequest;
    const applyFilters = async () => {
        if (!filterForm) return;
        if (filterRequest) filterRequest.abort();
        filterRequest = new AbortController();
        const params = new URLSearchParams(new FormData(filterForm));
        const nextUrl = `${filterForm.action}?${params.toString()}`;
        window.LakshyaLiveFilters?.setBusy(drawer, true, { message: 'Updating records…' });
        try {
            const response = await fetch(nextUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' }, signal: filterRequest.signal });
            if (!response.ok) throw new Error('Unable to update student records.');
            const nextDocument = new DOMParser().parseFromString(await response.text(), 'text/html');
            const replacements = [
                ['.cohort-summary', '.cohort-summary'],
                ['.cohort-intro > div', '.cohort-intro > div'],
                ['.cohort-roster__heading > div', '.cohort-roster__heading > div'],
                ['#cohortRows', '#cohortRows']
            ];
            replacements.forEach(([currentSelector, nextSelector]) => {
                const current = document.querySelector(currentSelector);
                const next = nextDocument.querySelector(nextSelector);
                if (current && next) current.replaceWith(next);
            });
            window.history.replaceState({}, '', nextUrl);
            window.LakshyaLiveFilters?.setBusy(drawer, false);
        } catch (error) {
            if (error.name === 'AbortError') return;
            window.LakshyaLiveFilters?.setBusy(drawer, false);
            const status = drawer?.querySelector('[data-filter-status]');
            if (status) { status.hidden = false; status.dataset.state = 'error'; status.textContent = 'Could not update. Try again.'; }
        }
    };
    window.LakshyaLiveFilters?.bind({ root: filterForm, autoSelector: '[data-auto-filter]', liveSelector: '[data-live-search]', onApply: applyFilters });
    filterForm?.addEventListener('submit', (event) => { event.preventDefault(); applyFilters(); });

    const search = document.getElementById('cohortQuickSearch');
    search?.addEventListener('input', () => {
        const query = search.value.trim().toLowerCase();
        document.querySelectorAll('#cohortRows tr[data-cohort-search]').forEach((row) => {
            row.hidden = query.length > 0 && !row.dataset.cohortSearch.toLowerCase().includes(query);
        });
    });
});
