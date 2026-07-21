(function () {
    const meta = document.querySelector('meta[name="csrf-token"]');
    const token = meta ? meta.content : '';

    window.csrfFetch = function (url, options = {}) {
        const requestOptions = { ...options };
        const method = String(requestOptions.method || 'GET').toUpperCase();
        if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
            requestOptions.headers = new Headers(requestOptions.headers || {});
            requestOptions.headers.set('X-CSRFToken', token);
        }
        return fetch(url, requestOptions);
    };
})();
