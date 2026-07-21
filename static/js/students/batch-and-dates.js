// --- BATCH LOGIC ---

function formatAcademicYear(year) {
    if (!year) return "";
    const nextYear = (year + 1).toString().slice(-2);
    return `${year}-${nextYear}`;
}

function getBatchFromYear(year) {
    if (!year) return "";
    return (parseInt(year) - BASE_YEAR) + 1;
}

function getYearFromBatch(batchNo) {
    if (!batchNo) return "";
    return BASE_YEAR + (parseInt(batchNo) - 1);
}

function populateBatchDropdowns() {
    const yearSelect = document.getElementById('batch_year');
    const batchSelect = document.getElementById('batch_no');
    
    yearSelect.innerHTML = '<option value="">Select Year</option>';
    batchSelect.innerHTML = '<option value="">Select Batch</option>';

    const currentYear = new Date().getFullYear();
    const futureLimit = currentYear + 5; 

    for (let y = BASE_YEAR; y <= futureLimit; y++) {
        const opt = document.createElement('option');
        opt.value = y;
        opt.textContent = formatAcademicYear(y);
        yearSelect.appendChild(opt);
    }

    const batchesNeeded = (futureLimit - BASE_YEAR) + 1;
    for (let b = 1; b <= batchesNeeded; b++) {
        const opt = document.createElement('option');
        opt.value = b;
        opt.textContent = `Batch ${b}`;
        batchSelect.appendChild(opt);
    }
}

function syncBatchFromYear(context) {
    const yearSelect = (context === 'modal') 
        ? document.getElementById('batch_year') 
        : document.getElementById('filter_year');
    const batchSelect = (context === 'modal') 
        ? document.getElementById('batch_no') 
        : document.getElementById('filter_batch_no');

    const selectedYear = yearSelect.value;
    if (selectedYear) {
        batchSelect.value = getBatchFromYear(selectedYear);
    }
}

function syncYearFromBatch(context) {
    const yearSelect = (context === 'modal') 
        ? document.getElementById('batch_year') 
        : document.getElementById('filter_year');
    const batchSelect = (context === 'modal') 
        ? document.getElementById('batch_no') 
        : document.getElementById('filter_batch_no');

    const selectedBatch = batchSelect.value;
    if (selectedBatch) {
        yearSelect.value = getYearFromBatch(selectedBatch);
    }
}

// --- END DATE LOGIC ---

function updateEndDate() {
    const dojInput = document.getElementById('date_of_joining').value;
    const endDisplay = document.getElementById('end_date_display');
    
    if (dojInput) {
        const parts = dojInput.split('-');
        const year = parseInt(parts[0]);
        const month = parseInt(parts[1]) - 1; 
        const day = parseInt(parts[2]);

        let endYear = year + 5;
        let endDay = day;
        let endMonth = month;

        // Handle Leap Year case for Feb 29
        if (month === 1 && day === 29) { 
            const isLeap = new Date(endYear, 1, 29).getMonth() === 1;
            if (!isLeap) endDay = 28;
        }

        const finalDate = new Date(endYear, endMonth, endDay);
        const formattedDate = finalDate.toISOString().split('T')[0];
        endDisplay.value = formattedDate;
    } else {
        endDisplay.value = '';
    }
}


