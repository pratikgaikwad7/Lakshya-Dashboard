document.addEventListener('DOMContentLoaded', () => {
    const cells = [...document.querySelectorAll('.heat-cell')];
    const maximum = Math.max(1, ...cells.map((cell) => Number(cell.dataset.count || 0)));
    cells.forEach((cell) => {
        const count = Number(cell.dataset.count || 0);
        cell.style.setProperty('--heat', count ? String(.12 + (count / maximum) * .78) : '0');
        cell.classList.toggle('is-empty', count === 0);
    });

    const search = document.getElementById('newDashboardStudentSearch');
    const rows = [...document.querySelectorAll('#newDashboardStudentRows tr[data-student-search]')];
    if (search) search.addEventListener('input', () => {
        const query = search.value.trim().toLowerCase();
        rows.forEach((row) => { row.hidden = query.length > 0 && !row.dataset.studentSearch.toLowerCase().includes(query); });
    });

    const batchFilter = document.getElementById('batchHistoryFilter');
    const batchLanes = [...document.querySelectorAll('.batch-lane[data-batch-year]')];
    const batchEmpty = document.getElementById('batchHistoryEmpty');
    const filterBatches = () => {
        const selection = batchFilter?.value || 'active';
        let visible = 0;
        batchLanes.forEach((lane) => {
            const shouldShow = selection === 'all'
                || (selection === 'active' && lane.dataset.cycleEnded !== 'true')
                || lane.dataset.batchYear === selection;
            lane.hidden = !shouldShow;
            if (shouldShow) visible += 1;
        });
        if (batchEmpty) batchEmpty.hidden = visible !== 0;
    };
    if (batchFilter) batchFilter.addEventListener('change', filterBatches);
    filterBatches();
});
