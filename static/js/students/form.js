function openModal() {
    form.reset();
    document.getElementById('studentId').value = '';
    modalTitle.innerText = 'Add New Student';
    
    document.getElementById('batch_year').value = '';
    document.getElementById('batch_no').value = '';
    document.getElementById('end_date_display').value = '';
    document.getElementById('status').value = 'active';
    
    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

function closeModal() { 
    modal.classList.add('hidden'); 
    document.body.classList.remove('overflow-hidden');
}

async function editStudent(id) {
    const student = studentsCache.find(s => s.id === id);
    if (!student) return;
    
    const nameParts = (student.employee_name || "").trim().split(/\s+/);
    
    const firstName = nameParts[0] || '';
    const surname = nameParts.length > 1 ? nameParts[nameParts.length - 1] : '';
    const middleName = nameParts.length > 2 ? nameParts.slice(1, -1).join(' ') : '';

    document.getElementById('studentId').value = student.id;
    document.getElementById('first_name').value = firstName;
    document.getElementById('middle_name').value = middleName;
    document.getElementById('surname').value = surname;

    document.getElementById('ticket_no').value = student.ticket_no || '';
    document.getElementById('email').value = student.email || '';
    document.getElementById('gender').value = student.gender || '';
    document.getElementById('mobile_no').value = student.mobile_no || '';
    document.getElementById('diploma_branch').value = student.diploma_branch || '';
    document.getElementById('bits_stream').value = student.bits_stream || '';
    document.getElementById('department').value = student.department || '';
    document.getElementById('reporting_manager').value = student.reporting_manager || '';
    document.getElementById('function').value = student.function || '';
    
    const dojValue = student.date_of_joining || '';
    document.getElementById('date_of_joining').value = dojValue;
    
    updateEndDate();
    
    document.getElementById('plant_location').value = student.plant_location || '';
    document.getElementById('batch_year').value = student.batch_year || '';
    document.getElementById('batch_no').value = student.batch_no || '';
    document.getElementById('status').value = student.status || 'active';

    modalTitle.innerText = 'Edit Student Details';
    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

async function deleteStudent(id) {
    if (!confirm('Are you sure you want to delete this student?')) return;
    try {
        const response = await csrfFetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (response.ok) loadStudents(); else alert('Failed to delete');
    } catch (err) { console.error(err); }
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('studentId').value;
    const isEdit = !!id;
    
    const yearVal = document.getElementById('batch_year').value;
    const batchVal = document.getElementById('batch_no').value;

    const payload = {
        first_name: document.getElementById('first_name').value,
        middle_name: document.getElementById('middle_name').value,
        surname: document.getElementById('surname').value,
        
        ticket_no: document.getElementById('ticket_no').value,
        email: document.getElementById('email').value,
        gender: document.getElementById('gender').value,
        mobile_no: document.getElementById('mobile_no').value,
        diploma_branch: document.getElementById('diploma_branch').value,
        bits_stream: document.getElementById('bits_stream').value,
        department: document.getElementById('department').value,
        reporting_manager: document.getElementById('reporting_manager').value,
        function: document.getElementById('function').value,
        date_of_joining: document.getElementById('date_of_joining').value,
        plant_location: document.getElementById('plant_location').value,
        batch_year: yearVal ? parseInt(yearVal) : null,
        batch_no: batchVal ? parseInt(batchVal) : null,
        bc_no: '',
        status: document.getElementById('status').value
    };

    try {
        const url = isEdit ? `${API_URL}/${id}` : API_URL;
        const method = isEdit ? 'PUT' : 'POST';
        const response = await csrfFetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) { 
            closeModal(); 
            await loadStudents();
        } else { 
            const err = await response.json(); 
            alert('Error: ' + (err.error || 'Unknown error')); 
        }
    } catch (err) { console.error(err); alert('Failed to save student'); }
});

