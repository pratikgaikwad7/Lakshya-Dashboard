// --- EXCEL UPLOAD LOGIC ---

const uploadInput = document.getElementById('excelUploadInput');

uploadInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        uploadExcelFile(this.files[0]);
    }
});

async function uploadExcelFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const uploadBtn = document.querySelector('button[onclick*="excelUploadInput"]');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Uploading...';
    uploadBtn.disabled = true;

    try {
        const response = await csrfFetch('/api/students/upload-excel', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            showUploadResult(result);
            if (result.inserted > 0) {
                loadStudents();
            }
        } else {
            await window.LakshyaDialog.alert({
                title: 'Upload failed',
                message: result.error || 'An unknown upload error occurred.',
                tone: 'danger',
                icon: 'fa-file-circle-exclamation'
            });
        }
    } catch (err) {
        console.error(err);
        await window.LakshyaDialog.alert({
            title: 'Upload failed',
            message: 'The server could not be reached. Please try again.',
            tone: 'danger',
            icon: 'fa-plug-circle-xmark'
        });
    } finally {
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
        uploadInput.value = '';
    }
}

function showUploadResult(data) {
    document.getElementById('res-total').innerText = data.total_rows;
    document.getElementById('res-inserted').innerText = data.inserted;
    document.getElementById('res-skipped').innerText = data.skipped;
    document.getElementById('res-failed').innerText = data.failed;

    const errorContainer = document.getElementById('errorDetailsContainer');
    const errorList = document.getElementById('errorList');
    errorList.innerHTML = '';

    if (data.failed > 0 && data.errors && data.errors.length > 0) {
        errorContainer.classList.remove('hidden');
        data.errors.forEach(err => {
            const div = document.createElement('div');
            div.textContent = err;
            div.className = 'mb-1 border-b border-red-100 pb-1 last:border-0';
            errorList.appendChild(div);
        });
    } else {
        errorContainer.classList.add('hidden');
    }

    document.getElementById('uploadResultModal').classList.remove('hidden');
}

function closeUploadResult() {
    document.getElementById('uploadResultModal').classList.add('hidden');
}
