(function () {
    'use strict';

    // Simple client-side fallback for static hosting (e.g., GitHub Pages)
    // Ensures internal links work by mapping pretty paths to actual html files
    function resolvePathToFile(pathname) {
        const routes = {
            '/': 'index.html',
            '/about': 'about.html',
            '/docs': 'docs.html',
            '/analytics': 'analytics.html',
            '/deploy': 'deploy_detect.html',
            '/deploy/detect': 'deploy_detect.html',
            '/deploy/segment': 'deploy_segment.html',
            '/deploy/classify': 'deploy_classify.html',
            '/deploy/pose': 'deploy_pose.html',
            '/realtime': 'realtime.html'
        };
        return routes[pathname] || null;
    }

    function handleNavigation() {
        var file = resolvePathToFile(window.location.pathname);
        if (file && !window.location.pathname.endsWith(file)) {
            // Replace the URL with the actual file while keeping history nice
            window.location.replace('/' + file);
        }
    }

    // Run once on load
    handleNavigation();
})();


