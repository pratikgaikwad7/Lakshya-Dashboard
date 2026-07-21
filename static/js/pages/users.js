// Role → Plant Logic
document.addEventListener('DOMContentLoaded', () => {

    const roleSelect = document.getElementById('roleSelect');
    const plantBox = document.getElementById('plantLocationBox');

    const plantRoles = ['HR Head', 'Skill Head', 'SDC Coordinator'];

    roleSelect.addEventListener('change', function () {

        if (plantRoles.includes(this.value)) {
            plantBox.classList.remove('hidden');
            plantBox.required = true;
        } else {
            plantBox.classList.add('hidden');
            plantBox.required = false;
            plantBox.value = '';
        }

    });

});

