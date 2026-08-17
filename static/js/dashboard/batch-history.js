function initializeBatchHistoryFilter(root = document) {
    const filter = root.querySelector('#batchHistoryFilter') || document.getElementById('batchHistoryFilter');
    if (!filter) return;
    const scope = filter.closest('.dashboard-batch-footprint') || document;
    const lanes = [...scope.querySelectorAll('.batch-lane[data-batch-year]')];
    const empty = scope.querySelector('#batchHistoryEmpty');
    const count = scope.querySelector('#batchVisibleCount');
    const update = () => {
        const selection = filter.value || 'active';
        let visible = 0;
        lanes.forEach((lane) => {
            const show = selection === 'all' || (selection === 'active' && lane.dataset.cycleEnded !== 'true') || lane.dataset.batchYear === selection;
            lane.hidden = !show;
            if (show) visible += 1;
        });
        if (empty) empty.hidden = visible !== 0;
        if (count) count.textContent = `${visible} ${visible === 1 ? 'batch' : 'batches'}`;
    };
    if (filter.dataset.batchHistoryBound !== 'true') {
        filter.dataset.batchHistoryBound = 'true';
        filter.addEventListener('change', update);
    }
    update();
}

document.addEventListener('DOMContentLoaded', () => initializeBatchHistoryFilter());
