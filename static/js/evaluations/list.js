        // Toggle Sidebar Logic
        function toggleSidebar(forceOpen) {
            const sidebar = document.getElementById('filterSidebar');
            const overlay = document.getElementById('overlay');
            const toggle = document.getElementById('evaluationFilterToggle');
            const shouldOpen = typeof forceOpen === 'boolean'
                ? forceOpen
                : sidebar.classList.contains('sidebar-closed');
            
            if (shouldOpen) {
                // Open Sidebar
                sidebar.classList.remove('sidebar-closed');
                sidebar.classList.add('sidebar-open');
                sidebar.setAttribute('aria-hidden', 'false');
                if (toggle) toggle.setAttribute('aria-expanded', 'true');
                
                // Show Overlay
                overlay.classList.remove('hidden');
                setTimeout(() => {
                    overlay.classList.remove('opacity-0');
                    overlay.classList.add('opacity-100');
                }, 10);
            } else {
                // Close Sidebar
                sidebar.classList.remove('sidebar-open');
                sidebar.classList.add('sidebar-closed');
                sidebar.setAttribute('aria-hidden', 'true');
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
                
                // Hide Overlay
                overlay.classList.remove('opacity-100');
                overlay.classList.add('opacity-0');
                setTimeout(() => {
                    overlay.classList.add('hidden');
                }, 300);
            }
        }

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') toggleSidebar(false);
        });

        function openStudentModal(student) {
            document.getElementById('modal-title').textContent = student.employee_name || 'N/A';
            document.getElementById('modalAvatar').textContent = (student.employee_name || '?')[0].toUpperCase();
            setEvaluationModalSubtitle(student.department || 'Unknown Dept', student.ticket_no || 'N/A');

            // Populate Fields
            document.getElementById('mTicket').textContent = student.ticket_no || 'N/A';
            document.getElementById('mGender').textContent = student.gender || 'N/A';
            document.getElementById('mMobile').textContent = student.mobile_no || 'N/A';
            document.getElementById('mEmail').textContent = student.email || 'N/A';
            document.getElementById('mDiploma').textContent = student.diploma_branch || 'N/A';
            document.getElementById('mDept').textContent = student.department || 'N/A';
            document.getElementById('mBc').textContent = student.bc_no || 'N/A';
            document.getElementById('mFunction').textContent = student.function || 'N/A';
            document.getElementById('mManager').textContent = student.reporting_manager || 'N/A';
            document.getElementById('mBitsStream').textContent = student.bits_stream || 'N/A';
            
            let doj = student.date_of_joining ? student.date_of_joining.split('T')[0] : 'N/A';
            document.getElementById('mDoj').textContent = doj;
            
            document.getElementById('mLocation').textContent = student.plant_location || 'N/A';
            document.getElementById('mYear').textContent = student.batch_year || 'N/A';
            document.getElementById('mBatch').textContent = student.batch_no ? `Batch ${student.batch_no}` : 'N/A';

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

        function setEvaluationModalSubtitle(department, ticketNumber) {
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
    
