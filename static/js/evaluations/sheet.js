        function toggleEditMode() {
            const viewMode = document.getElementById('viewMode');
            const editMode = document.getElementById('editForm');
            
            if (viewMode.classList.contains('hidden')) {
                viewMode.classList.remove('hidden');
                editMode.classList.add('hidden');
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                viewMode.classList.add('hidden');
                editMode.classList.remove('hidden');
                calculateTotal();
            }
        }

        function calculateTotal() {
            const inputs = document.querySelectorAll('input[type="number"]:not([disabled])'); // Only count enabled inputs
            let total = 0;
            inputs.forEach(input => {
                if(input.name.startsWith('score_')) {
                    let val = parseFloat(input.value);
                    if (!isNaN(val)) {
                        total += val;
                    }
                }
            });
            document.getElementById('totalScoreDisplay').textContent = total;
        }
        
        document.addEventListener('DOMContentLoaded', calculateTotal);

        function openStudentModal() {
            document.getElementById('studentModal').classList.remove('hidden');
            document.body.classList.add('overflow-hidden'); 
        }

        function closeStudentModal() {
            document.getElementById('studentModal').classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        }
        
        function confirmSave() {
            // Double check if disabled (frontend safety)
            const disabledInputs = document.querySelectorAll('input:disabled');
            if (disabledInputs.length > 0) {
                return confirm("This record is locked. Changes cannot be saved.");
            }
            return confirm("Are you sure you want to save these evaluation marks?");
        }
    

