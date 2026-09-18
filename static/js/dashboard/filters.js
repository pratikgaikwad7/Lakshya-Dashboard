// ---------------------------------------------------------
// SIDEBAR CHECKBOX UTILITIES
// ---------------------------------------------------------
function selectAll(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]`);
    checkboxes.forEach(cb => cb.checked = true);
    syncLinkedBatchFilters(name);
    updateDropdownLabel(name);
    requestDashboardFilterRefresh();
}

function clearSelection(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]`);
    checkboxes.forEach(cb => cb.checked = false);
    syncLinkedBatchFilters(name);
    updateDropdownLabel(name);
    requestDashboardFilterRefresh();
}

function updateDropdownLabel(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
    const btnLabel = document.getElementById(`btn_label_${name}`);
    if (btnLabel) {
        btnLabel.textContent = checkboxes.length > 0 ? `${checkboxes.length} Selected` : 'All';
    }
}

function requestDashboardFilterRefresh() {
    const form = document.getElementById('dashboardFilterForm');
    if (form) form.requestSubmit();
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

function confirmFilterSelection(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;

    dropdown.classList.add('hidden');
    const trigger = document.querySelector(`[onclick*="'${dropdownId}'"]`);
    if (trigger) trigger.setAttribute('aria-expanded', 'false');
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

// Batch Year and Batch No describe the same cohort. Selecting either one also
// selects its matching value in the other control, while leaving every option
// available for the user to choose.
function syncLinkedBatchFilters(sourceName) {
    const form = document.getElementById('dashboardFilterForm');
    if (!form || !['year', 'batch_no'].includes(sourceName)) return;

    const links = (() => {
        try {
            return JSON.parse(form.dataset.batchFilterLinks || '{}');
        } catch (_) {
            return {};
        }
    })();
    const yearToNumbers = links.years || {};
    const numberToYears = links.batch_numbers || {};
    const yearInputs = Array.from(form.querySelectorAll('input[name="year"]'));
    const batchInputs = Array.from(form.querySelectorAll('input[name="batch_no"]'));

    const checkedValues = inputs => inputs.filter(input => input.checked).map(input => input.value);
    const selectMatchingBatchNumbers = years => {
        const matchingNumbers = new Set(years.flatMap(year => yearToNumbers[year] || []));
        batchInputs.forEach(input => {
            input.checked = matchingNumbers.has(input.value);
        });
        updateDropdownLabel('batch_no');
    };

    if (sourceName === 'batch_no') {
        const selectedNumbers = checkedValues(batchInputs);
        const linkedYears = new Set(selectedNumbers.flatMap(number => numberToYears[number] || []));
        yearInputs.forEach(input => { input.checked = linkedYears.has(input.value); });
        updateDropdownLabel('year');
        return;
    }

    selectMatchingBatchNumbers(checkedValues(yearInputs));
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('dashboardFilterForm');
    if (!form) return;

    form.querySelectorAll('input[name="year"], input[name="batch_no"]').forEach(input => {
        input.addEventListener('change', () => syncLinkedBatchFilters(input.name));
    });
    const hasSelectedBatchNumber = form.querySelector('input[name="batch_no"]:checked');
    syncLinkedBatchFilters(hasSelectedBatchNumber ? 'batch_no' : 'year');
});

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

    const employeeName = getVal('employee_name');
    if(employeeName) filters.employee_name = employeeName;

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
