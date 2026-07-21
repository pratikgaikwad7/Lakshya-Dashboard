(function () {
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    function animationDuration() {
        return reducedMotionQuery.matches ? 0 : 800;
    }

    function doughnutAnimation() {
        return {
            duration: reducedMotionQuery.matches ? 0 : 1100,
            delay: reducedMotionQuery.matches ? 0 : 140,
            easing: 'easeOutQuart',
            animateRotate: !reducedMotionQuery.matches,
            animateScale: false
        };
    }

    function doughnutRotation(maleCount, femaleCount) {
        const male = Math.max(Number(maleCount) || 0, 0);
        const female = Math.max(Number(femaleCount) || 0, 0);
        const total = male + female;
        if (total === 0) return 0;

        // Center the first (Male) arc on the right. The second (Female) arc
        // consequently remains centered on the left without swapping data.
        return 90 - ((male / total) * 180);
    }

    function barAnimation() {
        return {
            duration: animationDuration(),
            easing: 'easeOutQuart',
            delay(context) {
                if (reducedMotionQuery.matches) return 0;
                if (context.type === 'data' && context.mode === 'default') {
                    return Math.min(context.dataIndex * 35, 245);
                }
                return 0;
            }
        };
    }

    window.DashboardChartAnimations = {
        reducedMotion: () => reducedMotionQuery.matches,
        doughnutAnimation,
        doughnutRotation,
        barAnimation
    };
}());
