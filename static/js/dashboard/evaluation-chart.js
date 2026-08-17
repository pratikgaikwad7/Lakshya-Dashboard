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
            onClick: (event, elements, chart) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const range = chart.data.labels[index];
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
    const modal = document.getElementById('studentModal');
    const modalBody = modal.querySelector('.flex-1.overflow-y-auto');
    const scoreTypeLabels = { all: 'Grand total', bits: 'BITS', ojt: 'OJT', training: 'Training' };
    const scoreTypeLabel = scoreTypeLabels[scoreType] || 'Score';
    
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

    modal.classList.add('is-evaluation-list');
    document.getElementById('modal-title').textContent = `${scoreTypeLabel} score · ${range}`;
    document.getElementById('modalSub').textContent = 'Loading matching student records…';
    document.getElementById('modalAvatar').innerHTML = '<i class="fas fa-chart-column" aria-hidden="true"></i>';
    modalBody.innerHTML = '<div class="eval-range-state"><span class="eval-range-spinner" aria-hidden="true"></span><strong>Loading students</strong><p>Fetching records for the selected score range.</p></div>';
    modalBody.setAttribute('aria-busy', 'true');
    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
    modal.querySelector('.student-modal-close')?.focus();

    csrfFetch('/get-students-in-range', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error(`Student range request failed (${res.status})`);
        return res.json();
    })
    .then(students => {
        modalBody.setAttribute('aria-busy', 'false');
        // The skeleton is trusted application markup; all record values use textContent below.
        modalBody.innerHTML = `
            <div class="eval-range-content">
                <div class="eval-range-summary"><span><i class="fas fa-users" aria-hidden="true"></i><b id="evalRangeCount"></b></span><p>Click any row to open the student profile.</p></div>
                <div class="eval-range-table-wrap">
                    <table class="eval-range-table">
                        <thead>
                            <tr>
                                <th>Sr No</th><th>Student</th><th>Ticket</th><th>Plant</th><th>Sem</th><th>Score</th>
                            </tr>
                        </thead>
                        <tbody id="evalModalTableBody"></tbody>
                    </table>
                </div>
            </div>
        `;
        document.getElementById('modalSub').textContent = `${students.length} ${students.length === 1 ? 'student' : 'students'} in this range`;
        document.getElementById('evalRangeCount').textContent = `${students.length} matching ${students.length === 1 ? 'student' : 'students'}`;

        const tbody = document.getElementById('evalModalTableBody');
        if (students.length === 0) {
            const emptyRow = document.createElement('tr');
            const emptyCell = document.createElement('td');
            emptyCell.colSpan = 6;
            emptyCell.className = 'eval-range-empty';
            emptyCell.innerHTML = '<i class="fas fa-user-slash" aria-hidden="true"></i><strong>No matching students</strong><span>Try another score range or adjust the chart filters.</span>';
            emptyRow.appendChild(emptyCell);
            tbody.appendChild(emptyRow);
        }

        students.forEach((student, index) => {
            let score = student.calc_grand_total;
            if (scoreType === 'bits') score = student.calc_bits_total;
            if (scoreType === 'ojt') score = student.calc_ojt_total;
            if (scoreType === 'training') score = student.calc_training_total;

            const row = document.createElement('tr');
            row.className = 'eval-range-row';
            row.dataset.index = String(index);
            if (student.id) {
                row.dataset.profileUrl = `/evaluations/${encodeURIComponent(student.id)}/profile`;
                row.tabIndex = 0;
                row.setAttribute('aria-label', `View ${student.employee_name || 'student'} profile`);
            }
            const values = [
                index + 1,
                student.employee_name || '',
                student.ticket_no || '',
                student.plant_location ? student.plant_location.replace(/_/g, ' ') : 'Unknown',
                student.semester || '',
                Number(score || 0).toFixed(2),
            ];
            values.forEach((value, cellIndex) => {
                const cell = document.createElement('td');
                if (cellIndex === 5) cell.className = 'eval-range-score';
                if (cellIndex === 1) cell.className = 'eval-range-name';
                if (cellIndex === 1 && student.id) {
                    const profileLink = document.createElement('a');
                    profileLink.href = row.dataset.profileUrl;
                    profileLink.className = 'eval-range-profile-link';
                    profileLink.textContent = String(value);
                    cell.appendChild(profileLink);
                } else {
                    cell.textContent = String(value);
                }
                row.appendChild(cell);
            });
            tbody.appendChild(row);
        });

        if (tbody) {
            tbody.addEventListener('click', function(e) {
                if (e.target.closest('a')) return;
                const row = e.target.closest('tr');
                if (row && row.dataset.profileUrl) {
                    window.location.href = row.dataset.profileUrl;
                }
            });
            tbody.addEventListener('keydown', function(e) {
                if (e.key !== 'Enter' && e.key !== ' ') return;
                const row = e.target.closest('tr');
                if (!row || !row.dataset.profileUrl) return;
                e.preventDefault();
                window.location.href = row.dataset.profileUrl;
            });
        }
    })
    .catch(error => {
        console.error('Error loading students in score range:', error);
        modalBody.setAttribute('aria-busy', 'false');
        document.getElementById('modalSub').textContent = 'Student records could not be loaded';
        modalBody.innerHTML = '<div class="eval-range-state eval-range-state--error"><i class="fas fa-triangle-exclamation" aria-hidden="true"></i><strong>Unable to load students</strong><p>Close this window and try the score range again.</p></div>';
    });
}
