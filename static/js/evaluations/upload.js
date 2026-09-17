(function () {
    const form = document.getElementById('evaluationUploadForm');
    const input = document.getElementById('evaluationFile');
    const dropzone = document.getElementById('evaluationDropzone');
    const selectedFile = document.getElementById('evaluationSelectedFile');
    const submitButton = document.getElementById('evaluationUploadButton');
    const uploadState = document.querySelector('[data-upload-state]');
    const maximumBytes = 10 * 1024 * 1024;
    if (!form || !input || !dropzone || !selectedFile || !submitButton) return;

    function formatBytes(bytes) {
        if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
    function showFile(file) {
        const validExtension = /\.(xlsx|xls)$/i.test(file.name);
        const valid = validExtension && file.size <= maximumBytes;
        selectedFile.hidden = false;
        selectedFile.querySelector('[data-file-name]').textContent = file.name;
        selectedFile.querySelector('[data-file-size]').textContent = valid ? `${formatBytes(file.size)} · Ready to upload` : (!validExtension ? 'Choose an .xlsx or .xls file' : 'File exceeds the 10 MB limit');
        selectedFile.classList.toggle('is-invalid', !valid);
        submitButton.disabled = !valid;
        if (uploadState) {
            uploadState.textContent = valid ? 'Ready to import' : 'File needs attention';
            uploadState.classList.toggle('is-invalid', !valid);
            uploadState.classList.toggle('is-ready', valid);
        }
    }
    function clearFile() {
        input.value = '';
        selectedFile.hidden = true;
        submitButton.disabled = true;
        if (uploadState) {
            uploadState.textContent = 'Select a file';
            uploadState.classList.remove('is-invalid');
            uploadState.classList.remove('is-ready');
        }
        input.focus();
    }
    input.addEventListener('change', () => input.files[0] ? showFile(input.files[0]) : clearFile());
    for (const name of ['dragenter', 'dragover']) dropzone.addEventListener(name, event => { event.preventDefault(); dropzone.classList.add('is-dragging'); });
    for (const name of ['dragleave', 'drop']) dropzone.addEventListener(name, () => dropzone.classList.remove('is-dragging'));
    dropzone.addEventListener('drop', event => {
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        if (!file) return;
        const transfer = new DataTransfer();
        transfer.items.add(file);
        input.files = transfer.files;
        showFile(file);
    });
    selectedFile.querySelector('[data-remove-file]')?.addEventListener('click', clearFile);
    form.addEventListener('submit', () => {
        submitButton.disabled = true;
        submitButton.classList.add('is-uploading');
        if (uploadState) {
            uploadState.textContent = 'Uploading';
            uploadState.classList.remove('is-ready', 'is-invalid');
        }
        submitButton.querySelector('i').className = 'fas fa-circle-notch fa-spin';
        submitButton.querySelector('span').textContent = 'Uploading…';
    });
}());
