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

    const search = document.getElementById('cohortQuickSearch');
    const rows = [...document.querySelectorAll('#cohortRows tr[data-cohort-search]')];
    search?.addEventListener('input', () => {
        const query = search.value.trim().toLowerCase();
        rows.forEach((row) => { row.hidden = query.length > 0 && !row.dataset.cohortSearch.toLowerCase().includes(query); });
    });
});
