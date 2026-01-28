(function () {
    const user = localStorage.getItem('farmx_user');
    if (!user) {
        // Find the script tag that loaded this file to determine the path context
        const scriptTag = document.querySelector('script[src*="auth-guard.js"]');
        const src = scriptTag ? scriptTag.getAttribute('src') : '';

        // If src starts with "../", we are in a subdirectory (e.g. market/), so go up one level
        // If src is "shared/...", we are at root, so go into auth/

        let loginPath;
        if (src && src.startsWith('../')) {
            loginPath = '../auth/login.html';
        } else {
            loginPath = 'auth/login.html';
        }

        window.location.href = loginPath;
    }
})();
