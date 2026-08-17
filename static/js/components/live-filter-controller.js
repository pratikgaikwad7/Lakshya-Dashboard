(function () {
    function setBusy(root, busy, options = {}) {
        if (!root) return;
        const status = options.status || root.querySelector('[data-filter-status]');
        root.classList.toggle('is-filtering', busy);
        root.setAttribute('aria-busy', String(busy));
        if (status) {
            delete status.dataset.state;
            status.hidden = !busy;
            status.textContent = busy ? (options.message || 'Updating results…') : '';
        }
    }

    function bind(options) {
        const root = typeof options.root === 'string'
            ? document.querySelector(options.root)
            : options.root;
        if (!root || root.dataset.liveFilterBound === 'true') return null;

        root.dataset.liveFilterBound = 'true';
        const timers = new WeakMap();
        const delay = options.delay ?? 350;
        const apply = (source) => options.onApply(source);

        root.querySelectorAll(options.autoSelector || '[data-auto-filter]').forEach((field) => {
            field.addEventListener('change', () => apply(field));
        });

        root.querySelectorAll(options.liveSelector || '[data-live-search], [data-live-filter]').forEach((field) => {
            field.addEventListener('input', () => {
                window.clearTimeout(timers.get(field));
                timers.set(field, window.setTimeout(() => apply(field), delay));
            });
        });

        return { setBusy: (busy, busyOptions) => setBusy(root, busy, busyOptions) };
    }

    window.LakshyaLiveFilters = { bind, setBusy };
}());
