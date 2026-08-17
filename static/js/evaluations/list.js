        // Toggle Sidebar Logic
        function toggleSidebar(forceOpen) {
            const sidebar = document.getElementById('filterSidebar');
            const overlay = document.getElementById('overlay');
            const toggle = document.getElementById('evaluationFilterToggle');
            const workspace = document.querySelector('.evaluation-list-workspace');
            const shouldOpen = typeof forceOpen === 'boolean'
                ? forceOpen
                : sidebar.classList.contains('sidebar-closed');
            
            if (shouldOpen) {
                // Open Sidebar
                sidebar.classList.remove('sidebar-closed');
                sidebar.classList.add('sidebar-open');
                sidebar.setAttribute('aria-hidden', 'false');
                if (toggle) toggle.setAttribute('aria-expanded', 'true');
                if (workspace) workspace.classList.add('filters-open');
                window.sessionStorage.setItem('evaluationFiltersOpen', 'true');

                if (window.matchMedia('(max-width: 900px)').matches) {
                    overlay.classList.remove('hidden');
                    requestAnimationFrame(() => {
                        overlay.classList.remove('opacity-0');
                        overlay.classList.add('opacity-100');
                    });
                }
            } else {
                // Close Sidebar
                sidebar.classList.remove('sidebar-open');
                sidebar.classList.add('sidebar-closed');
                sidebar.setAttribute('aria-hidden', 'true');
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
                if (workspace) workspace.classList.remove('filters-open');
                window.sessionStorage.setItem('evaluationFiltersOpen', 'false');
                
                // Hide Overlay
                overlay.classList.remove('opacity-100');
                overlay.classList.add('opacity-0');
                setTimeout(() => {
                    overlay.classList.add('hidden');
                }, 180);
            }
        }

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') toggleSidebar(false);
        });

        document.addEventListener('DOMContentLoaded', function() {
            const liveSearchFields = document.querySelectorAll('[data-live-search]');
            const filterForm = document.getElementById('evaluationFilterForm');
            const restoreOpen = window.sessionStorage.getItem('evaluationFiltersOpen') === 'true';
            let filterRequest;

            if (restoreOpen) toggleSidebar(true);

            if (filterForm) {
                const applyFilters = async (field) => {
                    if (field && field.name) {
                        window.sessionStorage.setItem('evaluationActiveSearch', field.name);
                    }

                    if (filterRequest) filterRequest.abort();
                    filterRequest = new AbortController();
                    const requestController = filterRequest;

                    const sidebar = document.getElementById('filterSidebar');
                    const tableBody = document.querySelector('.evaluation-data-grid tbody');
                    const tableScroller = document.querySelector('.evaluation-data-scroll');
                    const params = new URLSearchParams(new FormData(filterForm));
                    const nextUrl = `${filterForm.action}?${params.toString()}`;
                    const horizontalScroll = tableScroller ? tableScroller.scrollLeft : 0;

                    window.LakshyaLiveFilters.setBusy(sidebar, true, { message: 'Updating results…' });

                    try {
                        const response = await fetch(nextUrl, {
                            headers: { 'X-Requested-With': 'XMLHttpRequest' },
                            signal: requestController.signal
                        });
                        if (!response.ok) throw new Error('Unable to update evaluation results.');

                        const documentFragment = new DOMParser().parseFromString(await response.text(), 'text/html');
                        const nextTableBody = documentFragment.querySelector('.evaluation-data-grid tbody');
                        if (!nextTableBody || !tableBody) throw new Error('Evaluation results were not found.');

                        tableBody.replaceChildren(...Array.from(nextTableBody.children));
                        window.history.replaceState({}, '', nextUrl);
                        if (tableScroller) tableScroller.scrollLeft = horizontalScroll;
                        window.LakshyaLiveFilters.setBusy(sidebar, false);
                    } catch (error) {
                        if (error.name !== 'AbortError') {
                            window.LakshyaLiveFilters.setBusy(sidebar, false);
                            const status = sidebar.querySelector('[data-filter-status]');
                            if (status) {
                                status.hidden = false;
                                status.dataset.state = 'error';
                                status.textContent = 'Could not update. Try again.';
                            }
                        }
                    }
                };

                window.LakshyaLiveFilters.bind({
                    root: filterForm,
                    autoSelector: '[data-auto-filter]',
                    liveSelector: '[data-live-search]',
                    onApply: applyFilters
                });

                filterForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    applyFilters(document.activeElement);
                });

                const activeSearchName = window.sessionStorage.getItem('evaluationActiveSearch');
                const activeSearch = Array.from(liveSearchFields).find(field => (
                    field.name === activeSearchName && field.value
                ));
                if (activeSearch && restoreOpen) {
                    activeSearch.focus();
                    activeSearch.setSelectionRange(activeSearch.value.length, activeSearch.value.length);
                }
            }

        });
