function updateDashboardBranchHeatmap(root = document) {
    const cells = [...root.querySelectorAll('.dashboard-branch-cell')];
    const maximum = Math.max(1, ...cells.map((cell) => Number(cell.dataset.count || 0)));

    cells.forEach((cell) => {
        const count = Number(cell.dataset.count || 0);
        cell.classList.toggle('is-empty', count === 0);
        cell.style.setProperty('--branch-heat', count ? String(.14 + (count / maximum) * .72) : '0');
    });
}

document.addEventListener('DOMContentLoaded', () => updateDashboardBranchHeatmap());

document.addEventListener('dashboard:content-updated', (event) => {
    updateDashboardBranchHeatmap(event.detail?.root || document);
});
