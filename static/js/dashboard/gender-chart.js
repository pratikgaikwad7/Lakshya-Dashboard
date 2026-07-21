// ---------------------------------------------------------
// CHART PLUGINS
// ---------------------------------------------------------
const centerTextPlugin = {
    id: 'centerText',
    beforeDraw(chart) {
        const { width, height, ctx } = chart;
        ctx.save();
        const total = chart.config.data.datasets[0].data.reduce((a, b) => a + b, 0);
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = 'bold 30px sans-serif';
        ctx.fillStyle = '#111827';
        ctx.fillText(total, width / 2, height / 2 - 8);
        ctx.font = '12px sans-serif';
        ctx.fillStyle = '#6b7280';
        ctx.fillText('Total', width / 2, height / 2 + 14);
        ctx.restore();
    }
};

function initGenderChart(maleCount, femaleCount) {
    const canvas = document.getElementById('genderChart');
    if (!canvas || !window.Chart) return;
    const ctx = canvas.getContext('2d');
    const total = maleCount + femaleCount;
    const rotation = window.DashboardChartAnimations
        ? window.DashboardChartAnimations.doughnutRotation(maleCount, femaleCount)
        : 90 - ((maleCount / (total || 1)) * 180);

    if (genderChartInstance && genderChartInstance.canvas === canvas) {
        genderChartInstance.data.datasets[0].data = [maleCount, femaleCount];
        genderChartInstance.options.rotation = rotation;
        genderChartInstance.update();
        if (window.DashboardLoading) window.DashboardLoading.markReady('gender-chart');
        return;
    }

    if (genderChartInstance) genderChartInstance.destroy();

    genderChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Male', 'Female'],
            datasets: [{
                data: [maleCount, femaleCount],
                backgroundColor: ['rgb(1, 98, 255)', 'rgb(255, 0, 128)'],
                borderColor: ['rgba(255, 255, 255, 1)', 'rgba(255, 255, 255, 1)'],
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            rotation,
            circumference: 360,
            animation: window.DashboardChartAnimations
                ? window.DashboardChartAnimations.doughnutAnimation()
                : { duration: 1100, delay: 140, easing: 'easeOutQuart', animateRotate: true },
            plugins: {
                legend: { display: true, position: 'bottom', labels: { color: '#374151', font: { size: 12, weight: 'bold' }, padding: 15, usePointStyle: true, pointStyle: 'circle' } },
                tooltip: { callbacks: { label: function(context) { let label = context.label || ''; if (label) label += ': '; if (context.parsed !== null) { const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0; label += `${context.parsed} (${percentage}%)`; } return label; } } },
                datalabels: { color: '#fff', anchor: 'center', align: 'center', font: { weight: 'bold', size: 14 }, formatter: (value) => value > 0 ? value : '' }
            }
        },
        plugins: [centerTextPlugin]
    });
    if (window.DashboardLoading) window.DashboardLoading.markReady('gender-chart');
}

function destroyDashboardCharts() {
    if (genderChartInstance) {
        genderChartInstance.destroy();
        genderChartInstance = null;
    }
    if (evaluationChartInstance) {
        evaluationChartInstance.destroy();
        evaluationChartInstance = null;
    }
}
