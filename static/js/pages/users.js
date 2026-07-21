document.addEventListener('DOMContentLoaded', () => {
    const roleSelect = document.getElementById('roleSelect');
    const plantGroup = document.getElementById('plantLocationGroup');
    const plantBox = document.getElementById('plantLocationBox');
    const createAction = document.getElementById('createUserAction');
    const plantRoles = ['HR Head', 'Skill Head', 'SDC Coordinator'];

    function updatePlantVisibility() {
        const needsPlant = plantRoles.includes(roleSelect.value);
        plantGroup.classList.toggle('hidden', !needsPlant);
        plantBox.required = needsPlant;
        createAction.classList.toggle('xl:col-span-1', !needsPlant);
        if (!needsPlant) plantBox.value = '';
    }

    roleSelect.addEventListener('change', updatePlantVisibility);
    updatePlantVisibility();

    const modal = document.getElementById('editUserModal');
    const editForm = document.getElementById('editUserForm');
    const usernameInput = document.getElementById('editUsername');
    const passwordInput = document.getElementById('editPassword');
    const confirmationInput = document.getElementById('editPasswordConfirmation');

    function openEditModal(userId, username) {
        editForm.action = `/users/update/${encodeURIComponent(userId)}`;
        usernameInput.value = username;
        passwordInput.value = '';
        confirmationInput.value = '';
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        window.requestAnimationFrame(() => usernameInput.focus());
    }

    function closeEditModal() {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        editForm.reset();
    }

    document.querySelectorAll('.users-edit-button').forEach(button => {
        button.addEventListener('click', () => {
            openEditModal(button.dataset.userId, button.dataset.username);
        });
    });

    document.querySelectorAll('[data-close-edit]').forEach(button => {
        button.addEventListener('click', closeEditModal);
    });

    document.querySelectorAll('.users-delete-form').forEach(form => {
        form.addEventListener('submit', event => {
            if (!window.confirm(`Delete the account "${form.dataset.username}"? This cannot be undone.`)) {
                event.preventDefault();
            }
        });
    });

    editForm.addEventListener('submit', event => {
        if (passwordInput.value !== confirmationInput.value) {
            event.preventDefault();
            confirmationInput.setCustomValidity('Passwords do not match.');
            confirmationInput.reportValidity();
        }
    });

    confirmationInput.addEventListener('input', () => confirmationInput.setCustomValidity(''));
    passwordInput.addEventListener('input', () => confirmationInput.setCustomValidity(''));

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && !modal.classList.contains('hidden')) closeEditModal();
    });
});
