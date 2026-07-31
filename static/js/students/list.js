// --- CORE APP ---

document.addEventListener('DOMContentLoaded', async () => {
    initStudentsMotion();
    populateBatchDropdowns(); 
    await loadFilterOptions(); 
    setCurrentYearFilter();   
    loadStudents();            
});

async function loadFilterOptions() {
    try {
        const response = await fetch(FILTER_URL);
        const data = await response.json();

        const locationSelect = document.getElementById('filter_location');
        locationSelect.innerHTML = '<option value="">All Locations</option>';
        data.locations.forEach(loc => {
            const option = document.createElement('option');
            option.value = loc; 
            option.textContent = loc.replace(/_/g, ' '); 
            locationSelect.appendChild(option);
        });

        populateSelect('filter_department', data.departments);
        populateSelect('filter_bits_stream', data.bits_streams);
        populateSelect('filter_function', data.functions);
        populateSelectWithFormatter('filter_year', data.years, formatAcademicYear);
        populateSelectWithFormatter('filter_batch_no', data.batch_nos, b => `Batch ${b}`);

    } catch (err) { console.error('Failed to load filter options', err); }
}

function populateSelect(id, options) {
    const select = document.getElementById(id);
    const firstOption = select.options[0];
    select.innerHTML = '';
    select.appendChild(firstOption);
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        select.appendChild(option);
    });
}

function populateSelectWithFormatter(id, options, formatter) {
    const select = document.getElementById(id);
    const firstOption = select.options[0];
    select.innerHTML = '';
    select.appendChild(firstOption);

    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = formatter(opt);
        select.appendChild(option);
    });
}

function setCurrentYearFilter() {
    const currentYear = new Date().getFullYear();
    const yearSelect = document.getElementById('filter_year');
    const yearExists = Array.from(yearSelect.options).some(opt => opt.value == currentYear);
    if (yearExists) yearSelect.value = currentYear;
}

function getFilterParams() {
    const params = new URLSearchParams();
    const fields = ['location', 'year', 'department', 'batch_no', 'function', 'bits_stream'];
    fields.forEach(f => {
        const val = document.getElementById(`filter_${f}`).value;
        if (val) params.append(f, val);
    });
    const status = document.getElementById('filter_status').value;
    if (status) params.append('student_status', status);
    return params.toString();
}

async function loadStudents() {
    try {
        const queryString = getFilterParams();
        const response = await fetch(`${API_URL}?${queryString}`);
        const data = await response.json();
        studentsCache = data;
        renderTable(data);
    } catch (err) { console.error('Failed to load students', err); }
}

function renderTable(data) {
    tableBody.innerHTML = '';
    if (data.length === 0) { emptyState.classList.remove('hidden'); return; }
    emptyState.classList.add('hidden');

    data.forEach((student, index) => {
        const row = document.createElement('tr');
        row.className = 'students-data-row transition-colors group';
        const displayYear = student.batch_year ? formatAcademicYear(student.batch_year) : '-';
        const displayLocation = student.plant_location ? student.plant_location.replace(/_/g, ' ') : '-';
        const status = student.status || 'active';
        let badgeClass = 'bg-green-100 text-green-800';
        if(status === 'dropped') badgeClass = 'bg-red-100 text-red-800';
        if(status === 'completed') badgeClass = 'bg-blue-100 text-blue-800';

        // This markup is application-owned. Database values are assigned below with textContent.
        row.innerHTML = `
            <td class="whitespace-nowrap text-center"><span data-field="serial" class="students-serial font-bold"></span></td>
            <td class="whitespace-nowrap">
                <div class="flex items-center">
                    <div data-field="avatar" class="students-avatar flex-shrink-0 flex items-center justify-center text-white font-bold"></div>
                    <div class="students-info-copy">
                        <div data-field="name" class="students-name font-semibold"></div>
                        <div data-field="ticket" class="students-meta"></div>
                    </div>
                </div>
            </td>
            <td data-field="status" class="whitespace-nowrap"></td>
            <td class="whitespace-nowrap">
                <div data-field="location" class="students-location font-medium"></div>
                <div data-field="batch" class="students-meta"></div>
            </td>
            <td data-field="department" class="whitespace-nowrap students-department font-medium"></td>
            <td class="whitespace-nowrap">
                <div data-field="mobile" class="students-mobile"></div>
                <div data-field="email" class="students-email"></div>
            </td>
            <td class="whitespace-nowrap text-right font-medium">
                 <button data-action="edit" class="students-edit-action transition font-bold">
                    <i class="fas fa-edit mr-1"></i> Edit
                </button>
                <button data-action="delete" class="students-delete-action transition font-bold">
                    <i class="fas fa-trash mr-1"></i> Delete
                </button>
            </td>
        `;

        row.querySelector('[data-field="serial"]').textContent = String(index + 1);
        row.querySelector('[data-field="avatar"]').textContent = student.employee_name ? student.employee_name[0].toUpperCase() : 'N';
        row.querySelector('[data-field="name"]').textContent = student.employee_name || '';
        row.querySelector('[data-field="ticket"]').textContent = student.ticket_no || '';
        row.querySelector('[data-field="location"]').textContent = displayLocation;
        row.querySelector('[data-field="batch"]').textContent = `${displayYear} | Batch: ${student.batch_no || '-'}`;
        row.querySelector('[data-field="department"]').textContent = student.department || '-';
        row.querySelector('[data-field="mobile"]').textContent = student.mobile_no || '';
        row.querySelector('[data-field="email"]').textContent = student.email || '';

        const statusBadge = document.createElement('span');
        statusBadge.className = `students-status-badge inline-flex font-semibold ${badgeClass} capitalize`;
        statusBadge.textContent = status;
        row.querySelector('[data-field="status"]').appendChild(statusBadge);
        row.querySelector('[data-action="edit"]').addEventListener('click', () => editStudent(student.id));
        row.querySelector('[data-action="delete"]').addEventListener('click', () => deleteStudent(student.id));
        tableBody.appendChild(row);
    });

    if (window.gsap && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        window.gsap.from('#studentTableBody .students-data-row', {
            autoAlpha: 0,
            y: 8,
            duration: 0.4,
            stagger: 0.022,
            ease: 'power2.out',
            clearProps: 'opacity,transform,visibility'
        });
    }
}

function initStudentsMotion() {
    if (!window.gsap || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    window.gsap.from('.students-header__inner > *, .students-command-bar > *', {
        autoAlpha: 0,
        y: -9,
        duration: 0.5,
        stagger: 0.06,
        ease: 'power2.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.from('.students-filter-card, .students-data-card', {
        autoAlpha: 0,
        y: 14,
        duration: 0.58,
        stagger: 0.08,
        ease: 'power3.out',
        clearProps: 'opacity,transform,visibility'
    });

    window.gsap.to('.students-header__aurora--one', {
        xPercent: -8,
        duration: 8,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
    });
}

function applyFilters() { loadStudents(); }

function clearFilters() {
    document.getElementById('filter_location').value = '';
    document.getElementById('filter_department').value = '';
    document.getElementById('filter_bits_stream').value = '';
    document.getElementById('filter_batch_no').value = '';
    document.getElementById('filter_function').value = '';
    document.getElementById('filter_status').value = '';
    setCurrentYearFilter();
    loadStudents();
}
