Chart.register(ChartDataLabels);

const sidebar = document.getElementById('filterSidebar');
const studentTableContainer = document.getElementById('studentTableContainer');
const toggleTableText = document.getElementById('toggleTableText');
const toggleTableIcon = document.getElementById('toggleTableIcon');

let genderChartInstance = null;
let evaluationChartInstance = null; 
let studentModalOriginalContent = null;

document.addEventListener('DOMContentLoaded', function() {
    if (window.dashboardConfig) {
        initGenderChart(window.dashboardConfig.maleCount, window.dashboardConfig.femaleCount);
    }
    
    updateEvaluationChart();

    const modalBody = document.querySelector('#studentModal .flex-1.overflow-y-auto');
    if (modalBody) {
        studentModalOriginalContent = modalBody.innerHTML;
    }

    document.querySelectorAll('.eval-filter-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateEvaluationChart);
    });

    // Global click listener for closing dropdowns
    document.addEventListener('click', function(event) {
        const isClickInsideDropdown = event.target.closest('.dropdown-menu') || event.target.closest('.checkbox-dropdown-menu');
        const isClickOnDropdownBtn = event.target.closest('.dropdown-btn') || event.target.closest('.input-field');
        const isClickOnClearBtn = event.target.closest('button[onclick*="clearCheckboxes"]') || event.target.closest('button[onclick*="clearSelection"]');

        if (!isClickInsideDropdown && !isClickOnDropdownBtn && !isClickOnClearBtn) {
            document.querySelectorAll('.dropdown-menu, .checkbox-dropdown-menu').forEach(dd => {
                dd.classList.add('hidden');
            });
        }
    });
});

function toggleSidebar() {
    sidebar.classList.toggle('open');
}

function toggleStudentTable() {
    const isHidden = studentTableContainer.classList.contains('hidden');
    if (isHidden) {
        studentTableContainer.classList.remove('hidden');
        toggleTableText.textContent = 'Hide Student Records';
        toggleTableIcon.classList.remove('fa-chevron-down');
        toggleTableIcon.classList.add('fa-chevron-up');
    } else {
        studentTableContainer.classList.add('hidden');
        toggleTableText.textContent = 'Show Student Records';
        toggleTableIcon.classList.remove('fa-chevron-up');
        toggleTableIcon.classList.add('fa-chevron-down');
    }
}

function toggleDropdown(id) {
    document.querySelectorAll('.dropdown-menu, .checkbox-dropdown-menu').forEach(dd => {
        if(dd.id !== id) dd.classList.add('hidden');
    });
    const menu = document.getElementById(id);
    if (menu) menu.classList.toggle('hidden');
}

// ---------------------------------------------------------
// SIDEBAR CHECKBOX UTILITIES
// ---------------------------------------------------------
function selectAll(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]`);
    checkboxes.forEach(cb => cb.checked = true);
    updateDropdownLabel(name);
}

function clearSelection(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]`);
    checkboxes.forEach(cb => cb.checked = false);
    updateDropdownLabel(name);
}

function updateDropdownLabel(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
    const btnLabel = document.getElementById(`btn_label_${name}`);
    if (btnLabel) {
        btnLabel.textContent = checkboxes.length > 0 ? `${checkboxes.length} Selected` : 'All';
    }
}

function clearCheckboxes(type) {
    let selector = '';
    if(type === 'eval-batch') selector = '.eval-batch-checkbox';
    if(type === 'eval-plant') selector = '.eval-plant-checkbox';
    if(type === 'eval-sem') selector = '.eval-sem-checkbox';
    
    if(selector) {
        document.querySelectorAll(selector).forEach(cb => cb.checked = false);
        updateEvaluationChart();
    }
}

// ---------------------------------------------------------
// GLOBAL FILTER HELPER (UPDATED FOR CHECKBOXES)
// ---------------------------------------------------------
function getGlobalSidebarFilters() {
    const filters = {};
    
    // Helper to get checked values for a name
    const getCheckedVals = (name) => {
        return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(el => el.value);
    };

    // Helper for single select/text
    const getVal = (name) => {
        const el = document.querySelector(`[name="${name}"]`);
        return el ? el.value : '';
    };

    // Ticket No is a text input
    const ticketNo = getVal('ticket_no');
    if(ticketNo) filters.ticket_no = ticketNo;

    // Gather list filters from Sidebar
    const status = getCheckedVals('status');
    const gender = getCheckedVals('gender');
    const department = getCheckedVals('department');
    const functionSelect = getCheckedVals('function');
    const branch = getCheckedVals('branch');
    const bitsStream = getCheckedVals('bits_stream');
    const batchNo = getCheckedVals('batch_no');
    const plantLoc = getCheckedVals('plant_location');
    const year = getCheckedVals('year');
    const semester = getCheckedVals('semester');

    if(status.length > 0) filters.status = status;
    if(gender.length > 0) filters.gender = gender;
    if(department.length > 0) filters.department = department;
    if(functionSelect.length > 0) filters.function = functionSelect;
    if(branch.length > 0) filters.branch = branch;
    if(bitsStream.length > 0) filters.bits_stream = bitsStream;
    if(batchNo.length > 0) filters.batch_no = batchNo;
    if(plantLoc.length > 0) filters.plant_location = plantLoc;
    if(year.length > 0) filters.year = year;
    if(semester.length > 0) filters.semester = semester;

    return filters;
}

// ---------------------------------------------------------
// EVALUATION SCORE DISTRIBUTION CHART
// ---------------------------------------------------------
function updateEvaluationChart() {
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

    fetch('/get-performance-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        initEvaluationChart(data, scoreType);
    })
    .catch(error => console.error('Error updating evaluation chart:', error));
}

function initEvaluationChart(data, scoreType) {
    const ctx = document.getElementById('evaluationChart').getContext('2d');
    const labels = data.map(item => item.range);
    const counts = data.map(item => item.count);

    if (evaluationChartInstance) evaluationChartInstance.destroy();

    const barColors = [
        'rgb(239, 68, 68)', 'rgb(255, 106, 0)', 'rgb(255, 191, 0)',
        'rgb(153, 255, 0)', 'rgb(0, 255, 94)', 'rgb(9, 218, 255)'
    ];

    let xAxisTitle = 'Score Range';
    if(scoreType === 'bits') xAxisTitle = 'BITS Score Range (Out Of 30)';
    else if(scoreType === 'ojt') xAxisTitle = 'OJT Score Range (Out Of 50)';
    else if(scoreType === 'training') xAxisTitle = 'Training Score Range (Out Of 20)';
    else xAxisTitle = 'Grand Total Score Range (Out Of 100)';

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

    fetch('/get-students-in-range', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(students => {
        let tableRows = students.map((s, index) => {
            let scoreVal = s.calc_grand_total;
            if (scoreType === 'bits') scoreVal = s.calc_bits_total;
            if (scoreType === 'ojt') scoreVal = s.calc_ojt_total;
            if (scoreType === 'training') scoreVal = s.calc_training_total;

            return `
                <tr class="hover:bg-indigo-50 cursor-pointer transition-colors" data-index="${index}">
                    <td class="px-4 py-2 text-sm font-medium text-slate-900">${s.employee_name}</td>
                    <td class="px-4 py-2 text-sm text-slate-600">${s.ticket_no}</td>
                    <td class="px-4 py-2 text-sm text-slate-600">${s.plant_location.replace('_', ' ')}</td>
                    <td class="px-4 py-2 text-sm text-slate-600">${s.semester}</td>
                    <td class="px-4 py-2 text-sm font-bold text-indigo-600">${parseFloat(scoreVal).toFixed(2)}</td>
                </tr>
            `;
        }).join('');

        const modalBody = document.querySelector('#studentModal .flex-1.overflow-y-auto');
        
        modalBody.innerHTML = `
            <div class="p-4">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold text-slate-800">Students in Range: ${range}</h3>
                    <button onclick="closeStudentModal()" class="text-slate-400 hover:text-red-500 text-xl">&times;</button>
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
                        <tbody id="evalModalTableBody" class="bg-white divide-y divide-slate-100">
                            ${tableRows || '<tr><td colspan="5" class="text-center py-4 text-slate-400">No students found</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        document.getElementById('studentModal').classList.remove('hidden');

        const tbody = document.getElementById('evalModalTableBody');
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

// ---------------------------------------------------------
// STUDENT PROFILE MODAL
// ---------------------------------------------------------
function openStudentModal(student) {
    const modalBody = document.querySelector('#studentModal .flex-1.overflow-y-auto');
    if (studentModalOriginalContent) {
        modalBody.innerHTML = studentModalOriginalContent;
    }

    document.getElementById('modal-title').textContent = student.employee_name || 'N/A';
    document.getElementById('modalAvatar').textContent = (student.employee_name || '?')[0].toUpperCase();
    document.getElementById('modalSub').innerHTML = `
        <span>${student.department || 'Unknown Dept'}</span> 
        <span class="w-1 h-1 rounded-full bg-slate-500"></span> 
        <span>${student.ticket_no || 'N/A'}</span>
    `;

    document.getElementById('mTicket').textContent = student.ticket_no || 'N/A';
    document.getElementById('mEmail').textContent = student.email || 'N/A';
    document.getElementById('mMobile').textContent = student.mobile_no || 'N/A';
    document.getElementById('mGender').textContent = student.gender || 'N/A';
    document.getElementById('mBC').textContent = student.bc_no || 'N/A';
    document.getElementById('mDiploma').textContent = student.diploma_branch || 'N/A';
    
    const location = student.plant_location ? student.plant_location.replace(/_/g, ' ') : 'N/A';
    document.getElementById('mLocation').textContent = location;
    document.getElementById('mDept').textContent = student.department || 'N/A';
    document.getElementById('mFunction').textContent = student.function || 'N/A';
    document.getElementById('mManager').textContent = student.reporting_manager || 'N/A';
    document.getElementById('mStream').textContent = student.bits_stream || 'N/A';
    
    document.getElementById('mYear').textContent = formatAcademicYear(student.batch_year);
    document.getElementById('mBatch').textContent = student.batch_no ? `Batch ${student.batch_no}` : 'N/A';
    
    if (student.date_of_joining) {
        try {
            const dateObj = new Date(student.date_of_joining);
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            document.getElementById('mDOJ').textContent = dateObj.toLocaleDateString('en-US', options);
        } catch(e) {
            document.getElementById('mDOJ').textContent = student.date_of_joining;
        }
    } else {
        document.getElementById('mDOJ').textContent = 'N/A';
    }

    const semHeader = document.getElementById('mSemHeader');
    const statusBadge = document.getElementById('mStatusBadge');
    const activeStatusSpan = document.getElementById('mActiveStatus');
    
    semHeader.textContent = `Semester ${student.semester || '-'}`;
    
    let badgeHtml = '';
    
    if(student.student_status === 'dropped') {
         badgeHtml = '<span class="px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 border border-red-200 flex items-center gap-1"><i class="fas fa-ban"></i> Dropped</span>';
         activeStatusSpan.innerHTML = "Student Dropped";
         activeStatusSpan.className = "font-bold text-red-700";
    } else if (student.student_status === 'completed') {
         badgeHtml = '<span class="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 border border-blue-200 flex items-center gap-1"><i class="fas fa-user-graduate"></i> Completed</span>';
         activeStatusSpan.innerHTML = "Academics Completed";
         activeStatusSpan.className = "font-bold text-blue-700";
    } else {
        if(student.semester_status === 'completed') {
            badgeHtml = '<span class="px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700 border border-green-200 flex items-center gap-1"><i class="fas fa-check-circle"></i> Sem Completed</span>';
        } else if (student.semester_status === 'ongoing') {
            badgeHtml = '<span class="px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-700 border border-yellow-200 flex items-center gap-1"><i class="fas fa-spinner fa-spin"></i> Ongoing</span>';
        } else {
            badgeHtml = '<span class="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200">No Status</span>';
        }

        if(student.active_semester) {
            activeStatusSpan.innerHTML = `Semester ${student.active_semester} (Ongoing)`;
            activeStatusSpan.className = "font-bold text-green-700";
        } else {
            activeStatusSpan.innerHTML = "No Active Semester";
            activeStatusSpan.className = "font-bold text-slate-500";
        }
    }

    statusBadge.innerHTML = badgeHtml;

    document.getElementById('studentModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

function closeStudentModal() {
    document.getElementById('studentModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}

function formatAcademicYear(year) {
    if (!year) return 'N/A';
    const nextYear = (parseInt(year) + 1).toString().slice(-2);
    return `${year}-${nextYear}`;
}

// ---------------------------------------------------------
// CHART PLUGINS
// ---------------------------------------------------------
const centerTextPlugin = {
    id: 'centerText',
    beforeDraw(chart) {
        const { width, height, ctx } = chart;
        ctx.save();
        const total = chart.config.data.datasets[0].data.reduce((a, b) => a + b, 0);
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = 'bold 30px sans-serif';
        ctx.fillStyle = '#111827';
        ctx.fillText(total, width / 2, height / 2 - 8);
        ctx.font = '12px sans-serif';
        ctx.fillStyle = '#6b7280';
        ctx.fillText('Total', width / 2, height / 2 + 14);
        ctx.restore();
    }
};

function initGenderChart(maleCount, femaleCount) {
    const ctx = document.getElementById('genderChart').getContext('2d');
    const total = maleCount + femaleCount;

    if (genderChartInstance) genderChartInstance.destroy();

    genderChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Male', 'Female'],
            datasets: [{
                data: [maleCount, femaleCount],
                backgroundColor: ['rgb(1, 98, 255)', 'rgb(255, 0, 128)'],
                borderColor: ['rgba(255, 255, 255, 1)', 'rgba(255, 255, 255, 1)'],
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { display: true, position: 'bottom', labels: { color: '#374151', font: { size: 12, weight: 'bold' }, padding: 15, usePointStyle: true, pointStyle: 'circle' } },
                tooltip: { callbacks: { label: function(context) { let label = context.label || ''; if (label) label += ': '; if (context.parsed !== null) { const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0; label += `${context.parsed} (${percentage}%)`; } return label; } } },
                datalabels: { color: '#fff', anchor: 'center', align: 'center', font: { weight: 'bold', size: 14 }, formatter: (value) => value > 0 ? value : '' }
            }
        },
        plugins: [centerTextPlugin]
    });
}