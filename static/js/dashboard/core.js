if (window.Chart && window.ChartDataLabels) {
    Chart.register(ChartDataLabels);
}

let genderChartInstance = null;
let evaluationChartInstance = null; 
let studentModalOriginalContent = null;

document.addEventListener('DOMContentLoaded', function() {
    const modalBody = document.querySelector('#studentModal .flex-1.overflow-y-auto');
    if (modalBody) {
        studentModalOriginalContent = modalBody.innerHTML;
    }

    initializeDashboardContent();

    // Global click listener for closing dropdowns
    document.addEventListener('click', function(event) {
        const isClickInsideDropdown = event.target.closest('.dropdown-menu') || event.target.closest('.checkbox-dropdown-menu');
        const isClickOnDropdownBtn = event.target.closest('.dropdown-btn') || event.target.closest('.input-field');
        const isClickOnClearBtn = event.target.closest('button[onclick*="clearCheckboxes"]') || event.target.closest('button[onclick*="clearSelection"]');

        if (!isClickInsideDropdown && !isClickOnDropdownBtn && !isClickOnClearBtn) {
            if (typeof closeDashboardDropdowns === 'function') closeDashboardDropdowns();
        }
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            toggleSidebar(false);
            if (typeof closeDashboardDropdowns === 'function') closeDashboardDropdowns();
        }
    });
});

function initializeDashboardContent(options = {}) {
    const main = document.getElementById('mainContent');
    if (!main) return;

    document.querySelectorAll('.eval-filter-checkbox').forEach(checkbox => {
        if (checkbox.dataset.dashboardBound === 'true') return;
        checkbox.dataset.dashboardBound = 'true';
        checkbox.addEventListener('change', updateEvaluationChart);
    });

    const maleCount = Number(main.dataset.maleCount || window.dashboardConfig?.maleCount || 0);
    const femaleCount = Number(main.dataset.femaleCount || window.dashboardConfig?.femaleCount || 0);
    initGenderChart(maleCount, femaleCount);
    updateEvaluationChart();

    if (window.DashboardAnimations) {
        window.DashboardAnimations.initSections(main);
        window.DashboardAnimations.animateKpis(main, options.previousKpis || null);
        window.DashboardAnimations.refresh();
    }
}

function toggleSidebar(forceOpen) {
    const sidebar = document.getElementById('filterSidebar');
    if (!sidebar) return;
    const isOpen = typeof forceOpen === 'boolean'
        ? forceOpen
        : !sidebar.classList.contains('open');
    if (window.DashboardAnimations) {
        window.DashboardAnimations.setSidebarOpen(isOpen);
    } else {
        sidebar.classList.toggle('open', isOpen);
    }
}

function toggleStudentTable() {
    const studentTableContainer = document.getElementById('studentTableContainer');
    const toggleTableText = document.getElementById('toggleTableText');
    const toggleTableIcon = document.getElementById('toggleTableIcon');
    if (!studentTableContainer || !toggleTableText || !toggleTableIcon) return;
    const isHidden = studentTableContainer.classList.contains('hidden');
    if (isHidden) {
        studentTableContainer.classList.remove('hidden');
        if (window.gsap && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            window.gsap.fromTo(studentTableContainer, { opacity: 0, y: 8 }, {
                opacity: 1, y: 0, duration: 0.35, ease: 'power2.out', clearProps: 'transform,opacity'
            });
        }
        toggleTableText.textContent = 'Hide Student Records';
        toggleTableIcon.classList.remove('fa-chevron-down');
        toggleTableIcon.classList.add('fa-chevron-up');
    } else {
        studentTableContainer.classList.add('hidden');
        toggleTableText.textContent = 'Show Student Records';
        toggleTableIcon.classList.remove('fa-chevron-up');
        toggleTableIcon.classList.add('fa-chevron-down');
    }
}

function toggleDropdown(id, trigger) {
    if (typeof closeDashboardDropdowns === 'function') closeDashboardDropdowns(id);
    const menu = document.getElementById(id);
    if (menu) {
        const willOpen = menu.classList.contains('hidden');
        menu.classList.toggle('hidden', !willOpen);
        const button = trigger || document.querySelector(`[onclick*="${id}"]`);
        if (button) button.setAttribute('aria-expanded', String(willOpen));
    }
}
