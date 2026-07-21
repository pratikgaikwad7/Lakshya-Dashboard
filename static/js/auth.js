        function togglePassword() {
            const input = document.getElementById('passwordInput');
            const icon = document.getElementById('eyeIcon');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            // Left panel entrance
            const leftEl = document.querySelector('.left-panel .z-10');
            if (leftEl) {
                leftEl.style.opacity = '0';
                leftEl.style.transform = 'translateY(14px)';
                leftEl.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                requestAnimationFrame(() => requestAnimationFrame(() => {
                    leftEl.style.opacity = '1';
                    leftEl.style.transform = 'translateY(0)';
                }));
            }

            // Poster card entrance
            const posterOuter = document.querySelector('.poster-card-outer');
            if (posterOuter) {
                posterOuter.style.opacity = '0';
                posterOuter.style.transform = 'translateY(20px) scale(0.97)';
                posterOuter.style.transition = 'opacity 0.7s ease 0.15s, transform 0.7s ease 0.15s';
                requestAnimationFrame(() => requestAnimationFrame(() => {
                    posterOuter.style.opacity = '1';
                    posterOuter.style.transform = 'translateY(0) scale(1)';
                    // After entrance, re-enable float animation
                    setTimeout(() => {
                        posterOuter.style.transition = 'opacity 0.5s ease, transform 0.3s ease';
                    }, 900);
                }));
            }
        });
