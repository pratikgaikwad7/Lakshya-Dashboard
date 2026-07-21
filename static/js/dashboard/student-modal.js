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
    setStudentModalSubtitle(student.department || 'Unknown Dept', student.ticket_no || 'N/A');

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
         activeStatusSpan.textContent = "Student Dropped";
         activeStatusSpan.className = "font-bold text-red-700";
    } else if (student.student_status === 'completed') {
         badgeHtml = '<span class="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 border border-blue-200 flex items-center gap-1"><i class="fas fa-user-graduate"></i> Completed</span>';
         activeStatusSpan.textContent = "Academics Completed";
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
            activeStatusSpan.textContent = `Semester ${student.active_semester} (Ongoing)`;
            activeStatusSpan.className = "font-bold text-green-700";
        } else {
            activeStatusSpan.textContent = "No Active Semester";
            activeStatusSpan.className = "font-bold text-slate-500";
        }
    }

    statusBadge.innerHTML = badgeHtml;

    document.getElementById('studentModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

function setStudentModalSubtitle(department, ticketNumber) {
    const subtitle = document.getElementById('modalSub');
    const departmentElement = document.createElement('span');
    const divider = document.createElement('span');
    const ticketElement = document.createElement('span');
    departmentElement.textContent = department;
    divider.className = 'w-1 h-1 rounded-full bg-slate-500';
    ticketElement.textContent = ticketNumber;
    subtitle.replaceChildren(departmentElement, divider, ticketElement);
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

