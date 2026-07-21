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

function closeDashboardDropdowns(exceptId) {
    document.querySelectorAll('.dropdown-menu, .checkbox-dropdown-menu').forEach(menu => {
        if (menu.id === exceptId) return;
        menu.classList.add('hidden');
    });
    document.querySelectorAll('[aria-haspopup="true"]').forEach(button => {
        const controlsId = (button.getAttribute('onclick') || '').match(/'(.*?)'/)?.[1];
        if (controlsId !== exceptId) button.setAttribute('aria-expanded', 'false');
    });
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
    const studentStatus = getCheckedVals('student_status');
    const gender = getCheckedVals('gender');
    const department = getCheckedVals('department');
    const functionSelect = getCheckedVals('function');
    const branch = getCheckedVals('branch');
    const bitsStream = getCheckedVals('bits_stream');
    const batchNo = getCheckedVals('batch_no');
    const plantLoc = getCheckedVals('plant_location');
    const year = getCheckedVals('year');
    const semester = getCheckedVals('semester');

    if(studentStatus.length > 0) filters.student_status = studentStatus;
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
