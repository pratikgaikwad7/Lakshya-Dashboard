// ---------------------------------------------------------
// EVALUATION SCORE DISTRIBUTION CHART
// ---------------------------------------------------------
let evaluationRequestController = null;

function updateEvaluationChart() {
    const chartCanvas = document.getElementById('evaluationChart');
    if (!chartCanvas) return;
    const scoreType = document.getElementById('evalScoreType').value;
    
    const years = Array.from(document.querySelectorAll('.eval-batch-checkbox:checked')).map(el => el.value);
    const plants = Array.from(document.querySelectorAll('.eval-plant-checkbox:checked')).map(el => el.value);
    const sems = Array.from(document.querySelectorAll('.eval-sem-checkbox:checked')).map(el => el.value);
    const globalFilters = getGlobalSidebarFilters();

    // Merge global sidebar filters with chart-specific filters
    // Chart-specific filters take precedence if selected
    const payload = {
        ...globalFilters,
        year: years.length > 0 ? years : globalFilters.year || [],
        plant_location: plants.length > 0 ? plants : globalFilters.plant_location || [],
        semester: sems.length > 0 ? sems : globalFilters.semester || [],
        score_type: scoreType
    };

    if (evaluationRequestController) evaluationRequestController.abort();
    evaluationRequestController = new AbortController();
    if (window.DashboardLoading) window.DashboardLoading.setLoading('evaluation-chart', true);

    csrfFetch('/get-performance-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: evaluationRequestController.signal
    })
    .then(response => {
        if (!response.ok) throw new Error(`Evaluation chart request failed (${response.status})`);
        return response.json();
    })
    .then(data => {
        initEvaluationChart(data, scoreType);
    })
    .catch(error => {
        if (error.name === 'AbortError') return;
        console.error('Error updating evaluation chart:', error);
        if (window.DashboardLoading) {
            window.DashboardLoading.showError('evaluation-chart', 'Evaluation data could not be loaded.');
        }
    });
}

function initEvaluationChart(data, scoreType) {
    const canvas = document.getElementById('evaluationChart');
    if (!canvas || !window.Chart) return;
    const ctx = canvas.getContext('2d');
    const labels = data.map(item => item.range);
    const counts = data.map(item => item.count);

    const barColors = [
        'rgb(239, 68, 68)', 'rgb(255, 106, 0)', 'rgb(255, 191, 0)',
        'rgb(153, 255, 0)', 'rgb(0, 255, 94)', 'rgb(9, 218, 255)'
    ];

    let xAxisTitle = 'Score Range';
    if(scoreType === 'bits') xAxisTitle = 'BITS Score Range (Out Of 30)';
    else if(scoreType === 'ojt') xAxisTitle = 'OJT Score Range (Out Of 50)';
    else if(scoreType === 'training') xAxisTitle = 'Training Score Range (Out Of 20)';
    else xAxisTitle = 'Grand Total Score Range (Out Of 100)';

    if (evaluationChartInstance && evaluationChartInstance.canvas === canvas) {
        evaluationChartInstance.data.labels = labels;
        evaluationChartInstance.data.datasets[0].data = counts;
        evaluationChartInstance.options.scales.x.title.text = xAxisTitle;
        evaluationChartInstance.update();
        if (window.DashboardLoading) window.DashboardLoading.markReady('evaluation-chart');
        return;
    }

    if (evaluationChartInstance) evaluationChartInstance.destroy();

    evaluationChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Students',
                data: counts,
                backgroundColor: barColors,
                borderRadius: 8,
                borderSkipped: false,
                barPercentage: 0.58,
                categoryPercentage: 0.7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: window.DashboardChartAnimations
                ? window.DashboardChartAnimations.barAnimation()
                : { duration: 800, easing: 'easeOutQuart' },
            layout: { padding: { top: 18 } },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const range = labels[index];
                    openEvalStudentModal(range);
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0, stepSize: 1, color: '#64748b', font: { size: 11, weight: '500' } },
                    title: { display: true, text: 'Number of Students', color: '#475569', font: { size: 12, weight: 'bold' } },
                    grid: { color: 'rgba(15, 23, 42, 0.06)' }
                },
                x: {
                    ticks: { color: '#64748b', font: { size: 11, weight: '600' } },
                    title: { display: true, text: xAxisTitle, color: '#475569', font: { size: 12, weight: 'bold' } },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: { 
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    callbacks: { label: function(context) { return `${context.parsed.y} Students`; } }
                },
                datalabels: { 
                    anchor: 'end', align: 'top', offset: 2, color: '#000000', 
                    font: { weight: 'bold', size: 12 }, formatter: (value) => value > 0 ? value : '' 
                }
            }
        }
    });
    if (window.DashboardLoading) window.DashboardLoading.markReady('evaluation-chart');
}

// ---------------------------------------------------------
// EVAL MODAL
// ---------------------------------------------------------
function openEvalStudentModal(range) {
    const scoreType = document.getElementById('evalScoreType').value;
    
    const years = Array.from(document.querySelectorAll('.eval-batch-checkbox:checked')).map(el => el.value);
    const plants = Array.from(document.querySelectorAll('.eval-plant-checkbox:checked')).map(el => el.value);
    const sems = Array.from(document.querySelectorAll('.eval-sem-checkbox:checked')).map(el => el.value);
    const globalFilters = getGlobalSidebarFilters();

    const payload = {
        ...globalFilters,
        year: years.length > 0 ? years : globalFilters.year || [],
        plant_location: plants.length > 0 ? plants : globalFilters.plant_location || [],
        semester: sems.length > 0 ? sems : globalFilters.semester || [],
        range: range,
        score_type: scoreType
    };

    csrfFetch('/get-students-in-range', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(students => {
        const modalBody = document.querySelector('#studentModal .flex-1.overflow-y-auto');
        // The skeleton is trusted application markup; all record values use textContent below.
        modalBody.innerHTML = `
            <div class="p-4">
                <div class="flex justify-between items-center mb-4">
                    <h3 id="evalModalTitle" class="text-lg font-bold text-slate-800"></h3>
                    <button id="evalModalClose" type="button" class="text-slate-400 hover:text-red-500 text-xl">&times;</button>
                </div>
                <div class="overflow-x-auto border rounded-lg">
                    <table class="min-w-full divide-y">
                        <thead class="bg-slate-50">
                            <tr>
                                <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">Name</th>
                                <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">Ticket</th>
                                <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">Location</th>
                                <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">Sem</th>
                                <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">Score</th>
                            </tr>
                        </thead>
                        <tbody id="evalModalTableBody" class="bg-white divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>
        `;
        document.getElementById('evalModalTitle').textContent = `Students in Range: ${range}`;
        document.getElementById('evalModalClose').addEventListener('click', closeStudentModal);
        document.getElementById('studentModal').classList.remove('hidden');

        const tbody = document.getElementById('evalModalTableBody');
        if (students.length === 0) {
            const emptyRow = document.createElement('tr');
            const emptyCell = document.createElement('td');
            emptyCell.colSpan = 5;
            emptyCell.className = 'text-center py-4 text-slate-400';
            emptyCell.textContent = 'No students found';
            emptyRow.appendChild(emptyCell);
            tbody.appendChild(emptyRow);
        }

        students.forEach((student, index) => {
            let score = student.calc_grand_total;
            if (scoreType === 'bits') score = student.calc_bits_total;
            if (scoreType === 'ojt') score = student.calc_ojt_total;
            if (scoreType === 'training') score = student.calc_training_total;

            const row = document.createElement('tr');
            row.className = 'hover:bg-indigo-50 cursor-pointer transition-colors';
            row.dataset.index = String(index);
            const values = [
                student.employee_name || '',
                student.ticket_no || '',
                student.plant_location ? student.plant_location.replace(/_/g, ' ') : 'Unknown',
                student.semester || '',
                Number(score || 0).toFixed(2),
            ];
            values.forEach((value, cellIndex) => {
                const cell = document.createElement('td');
                cell.className = cellIndex === 4
                    ? 'px-4 py-2 text-sm font-bold text-indigo-600'
                    : cellIndex === 0
                        ? 'px-4 py-2 text-sm font-medium text-slate-900'
                        : 'px-4 py-2 text-sm text-slate-600';
                cell.textContent = String(value);
                row.appendChild(cell);
            });
            tbody.appendChild(row);
        });

        if (tbody) {
            tbody.addEventListener('click', function(e) {
                const row = e.target.closest('tr');
                if (row && row.dataset.index !== undefined) {
                    const index = parseInt(row.dataset.index);
                    const studentData = students[index];
                    openStudentModal(studentData);
                }
            });
        }
    });
}
