// Global configuration for frontend -> backend API routing
(function () {
    'use strict';

    // If not already defined, default to same-origin
    if (!window.GLOSENTRA_API_BASE) {
        // Use current origin by default, e.g., http://localhost:5000
        window.GLOSENTRA_API_BASE = `${window.location.protocol}//${window.location.host}`;
    }
})();


