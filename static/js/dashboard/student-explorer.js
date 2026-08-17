function initializeDashboardStudentExplorer(root = document) {
    const search = root.querySelector('#dashboardStudentSearch') || document.getElementById('dashboardStudentSearch');
    if (!search || search.dataset.studentExplorerBound === 'true') return;
    const scope = search.closest('.dashboard-student-explorer') || document;
    const rows = [...scope.querySelectorAll('#dashboardStudentRows tr[data-student-search]')];
    search.dataset.studentExplorerBound = 'true';
    search.addEventListener('input', () => {
        const query = search.value.trim().toLowerCase();
        rows.forEach((row) => { row.hidden = query.length > 0 && !row.dataset.studentSearch.toLowerCase().includes(query); });
    });
}

document.addEventListener('DOMContentLoaded', () => initializeDashboardStudentExplorer());
