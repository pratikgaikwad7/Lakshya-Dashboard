(function () {
    let layer;
    let panel;
    let icon;
    let eyebrow;
    let title;
    let message;
    let cancelButton;
    let confirmButton;
    let activeResolve;
    let previousFocus;
    let canDismiss = true;

    function createDialog() {
        if (layer) return;

        layer = document.createElement('div');
        layer.className = 'enterprise-dialog-layer';
        layer.hidden = true;
        layer.innerHTML = `
            <button type="button" class="enterprise-dialog-backdrop" aria-label="Close dialog"></button>
            <section class="enterprise-dialog-panel" role="alertdialog" aria-modal="true" aria-labelledby="enterpriseDialogTitle" aria-describedby="enterpriseDialogMessage" tabindex="-1">
                <div class="enterprise-dialog-accent" aria-hidden="true"></div>
                <div class="enterprise-dialog-content">
                    <span class="enterprise-dialog-icon" aria-hidden="true"><i class="fas fa-arrow-right"></i></span>
                    <div class="enterprise-dialog-copy">
                        <span class="enterprise-dialog-eyebrow">Confirmation required</span>
                        <h2 id="enterpriseDialogTitle" class="enterprise-dialog-title"></h2>
                        <p id="enterpriseDialogMessage" class="enterprise-dialog-message"></p>
                    </div>
                </div>
                <div class="enterprise-dialog-actions">
                    <button type="button" class="enterprise-dialog-button enterprise-dialog-button--secondary" data-enterprise-dialog-cancel>Cancel</button>
                    <button type="button" class="enterprise-dialog-button enterprise-dialog-button--primary" data-enterprise-dialog-confirm>Confirm</button>
                </div>
            </section>
        `;
        document.body.appendChild(layer);

        panel = layer.querySelector('.enterprise-dialog-panel');
        icon = layer.querySelector('.enterprise-dialog-icon i');
        eyebrow = layer.querySelector('.enterprise-dialog-eyebrow');
        title = layer.querySelector('.enterprise-dialog-title');
        message = layer.querySelector('.enterprise-dialog-message');
        cancelButton = layer.querySelector('[data-enterprise-dialog-cancel]');
        confirmButton = layer.querySelector('[data-enterprise-dialog-confirm]');

        layer.querySelector('.enterprise-dialog-backdrop').addEventListener('click', () => {
            if (canDismiss) finish(false);
        });
        cancelButton.addEventListener('click', () => finish(false));
        confirmButton.addEventListener('click', () => finish(true));
    }

    function finish(result) {
        if (!activeResolve) return;

        const resolve = activeResolve;
        activeResolve = null;
        layer.classList.remove('is-open');
        document.documentElement.classList.remove('enterprise-dialog-open');
        document.body.classList.remove('enterprise-dialog-open');

        window.setTimeout(() => {
            layer.hidden = true;
            if (previousFocus && typeof previousFocus.focus === 'function') {
                previousFocus.focus();
            }
            resolve(result);
        }, 210);
    }

    function handleKeydown(event) {
        if (!activeResolve) return;

        if (event.key === 'Escape' && canDismiss) {
            event.preventDefault();
            finish(false);
            return;
        }

        if (event.key !== 'Tab') return;
        const visibleButtons = [cancelButton, confirmButton].filter(
            button => !button.hidden
        );
        if (!visibleButtons.length) return;

        const first = visibleButtons[0];
        const last = visibleButtons[visibleButtons.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    async function open(options) {
        createDialog();

        if (activeResolve) {
            finish(false);
            await new Promise(resolve => window.setTimeout(resolve, 220));
        }

        const settings = {
            title: 'Confirm action',
            message: '',
            eyebrow: 'Confirmation required',
            confirmLabel: 'Confirm',
            cancelLabel: 'Cancel',
            tone: 'primary',
            icon: 'fa-arrow-right',
            dismissible: true,
            ...options
        };

        previousFocus = document.activeElement;
        canDismiss = settings.dismissible;
        panel.dataset.tone = settings.tone;
        icon.className = `fas ${settings.icon}`;
        eyebrow.textContent = settings.eyebrow;
        title.textContent = settings.title;
        message.textContent = settings.message;
        confirmButton.textContent = settings.confirmLabel;
        cancelButton.textContent = settings.cancelLabel || 'Cancel';
        cancelButton.hidden = !settings.cancelLabel;

        layer.hidden = false;
        document.documentElement.classList.add('enterprise-dialog-open');
        document.body.classList.add('enterprise-dialog-open');
        window.requestAnimationFrame(() => {
            layer.classList.add('is-open');
            window.setTimeout(() => confirmButton.focus(), 40);
        });

        return new Promise(resolve => {
            activeResolve = resolve;
        });
    }

    const api = {
        confirm(options) {
            return open(options);
        },
        alert(options) {
            return open({
                eyebrow: 'System message',
                confirmLabel: 'Close',
                cancelLabel: '',
                icon: 'fa-circle-info',
                ...options
            });
        }
    };

    window.LakshyaDialog = api;
    document.addEventListener('keydown', handleKeydown);

    document.addEventListener('submit', async event => {
        const form = event.target.closest('form[data-enterprise-confirm]');
        if (!form) return;

        if (form.dataset.enterpriseDialogBypass === 'true') {
            delete form.dataset.enterpriseDialogBypass;
            return;
        }

        event.preventDefault();
        const confirmed = await api.confirm({
            title: form.dataset.confirmTitle,
            message: form.dataset.confirmMessage,
            confirmLabel: form.dataset.confirmLabel || 'Confirm',
            cancelLabel: form.dataset.cancelLabel || 'Cancel',
            tone: form.dataset.confirmTone || 'primary',
            icon: form.dataset.confirmIcon || 'fa-arrow-right'
        });

        if (!confirmed) return;
        form.dataset.enterpriseDialogBypass = 'true';
        form.requestSubmit(event.submitter || undefined);
    }, true);
}());
