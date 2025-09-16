/**
 * Glosentra Prefetch & Performance Enhancement
 * Handles link prefetching, skeleton loading, and performance optimizations
 */

(function () {
    'use strict';

    // Configuration
    const CONFIG = {
        prefetchDelay: 100,      // ms to wait before prefetching
        cacheTimeout: 300000,    // 5 minutes
        maxConcurrent: 3,        // max concurrent prefetch requests
        skeletonDelay: 200       // ms to show skeleton loader
    };

    // Cache for prefetched pages
    const prefetchCache = new Map();
    const activePrefetches = new Set();

    // Performance tracking
    let prefetchStats = {
        total: 0,
        hits: 0,
        misses: 0,
        errors: 0
    };

    /**
     * Initialize prefetch system
     */
    function init() {
        setupLinkPrefetching();
        setupSkeletonLoading();
        setupPerformanceOptimizations();

        console.log('🚀 Glosentra prefetch system initialized');
    }

    /**
     * Setup link prefetching on hover
     */
    function setupLinkPrefetching() {
        const links = document.querySelectorAll('a[href^="/"]');

        links.forEach(link => {
            let prefetchTimeout;

            // Mouse enter - start prefetch timer
            link.addEventListener('mouseenter', () => {
                prefetchTimeout = setTimeout(() => {
                    prefetchPage(link.href);
                }, CONFIG.prefetchDelay);
            });

            // Mouse leave - cancel prefetch
            link.addEventListener('mouseleave', () => {
                if (prefetchTimeout) {
                    clearTimeout(prefetchTimeout);
                }
            });

            // Click - use cached content if available
            link.addEventListener('click', (e) => {
                const cachedContent = prefetchCache.get(link.href);
                if (cachedContent && Date.now() - cachedContent.timestamp < CONFIG.cacheTimeout) {
                    e.preventDefault();
                    navigateToPage(link.href, cachedContent.html);
                }
            });
        });
    }

    /**
     * Prefetch a page
     */
    async function prefetchPage(url) {
        // Skip if already cached or prefetching
        if (prefetchCache.has(url) || activePrefetches.has(url)) {
            return;
        }

        // Limit concurrent prefetches
        if (activePrefetches.size >= CONFIG.maxConcurrent) {
            return;
        }

        activePrefetches.add(url);
        prefetchStats.total++;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-Prefetch': 'true'
                }
            });

            if (response.ok) {
                const html = await response.text();
                prefetchCache.set(url, {
                    html: html,
                    timestamp: Date.now()
                });
                prefetchStats.hits++;
            } else {
                prefetchStats.misses++;
            }
        } catch (error) {
            console.warn('Prefetch failed for', url, error);
            prefetchStats.errors++;
        } finally {
            activePrefetches.delete(url);
        }
    }

    /**
     * Navigate to page using cached content
     */
    function navigateToPage(url, html) {
        // Show loading state
        showSkeletonLoader();

        // Use requestAnimationFrame for smooth transition
        requestAnimationFrame(() => {
            // Parse the HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Update the page
            updatePageContent(doc);

            // Update URL without page reload
            history.pushState({}, '', url);

            // Hide loading state
            hideSkeletonLoader();

            // Re-initialize prefetch for new page
            setTimeout(() => {
                setupLinkPrefetching();
                setupSkeletonLoading();
            }, 100);
        });
    }

    /**
     * Update page content from cached HTML
     */
    function updatePageContent(doc) {
        // Update title
        if (doc.title) {
            document.title = doc.title;
        }

        // Update main content
        const newMain = doc.querySelector('main');
        const currentMain = document.querySelector('main');

        if (newMain && currentMain) {
            currentMain.innerHTML = newMain.innerHTML;
        }

        // Update navigation active states
        updateNavigationState(doc);

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('pagechange', {
            detail: { url: window.location.href }
        }));
    }

    /**
     * Update navigation active states
     */
    function updateNavigationState(doc) {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            const linkPath = new URL(link.href).pathname;

            if (linkPath === currentPath || (currentPath.startsWith('/deploy') && linkPath.startsWith('/deploy'))) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    /**
     * Setup skeleton loading
     */
    function setupSkeletonLoading() {
        // Add skeleton styles
        if (!document.getElementById('skeleton-styles')) {
            const style = document.createElement('style');
            style.id = 'skeleton-styles';
            style.textContent = `
                .skeleton {
                    background: linear-gradient(90deg, var(--glass) 25%, var(--border) 50%, var(--glass) 75%);
                    background-size: 200% 100%;
                    animation: skeleton-loading 1.5s infinite;
                }
                
                @keyframes skeleton-loading {
                    0% { background-position: 200% 0; }
                    100% { background-position: -200% 0; }
                }
                
                .skeleton-text {
                    height: 1rem;
                    border-radius: 0.25rem;
                    margin-bottom: 0.5rem;
                }
                
                .skeleton-title {
                    height: 1.5rem;
                    width: 60%;
                    border-radius: 0.25rem;
                    margin-bottom: 1rem;
                }
                
                .skeleton-card {
                    height: 200px;
                    border-radius: 1rem;
                    margin-bottom: 1rem;
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Show skeleton loader
     */
    function showSkeletonLoader() {
        const main = document.querySelector('main');
        if (!main) return;

        // Create skeleton content
        const skeletonHTML = `
            <div class="skeleton-overlay fixed inset-0 bg-bg0/80 backdrop-blur-sm z-50 flex items-center justify-center">
                <div class="bg-glass border border-border rounded-2xl p-8 max-w-md mx-auto">
                    <div class="skeleton skeleton-title mb-4"></div>
                    <div class="skeleton skeleton-text mb-2"></div>
                    <div class="skeleton skeleton-text mb-2"></div>
                    <div class="skeleton skeleton-text w-3/4"></div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', skeletonHTML);
    }

    /**
     * Hide skeleton loader
     */
    function hideSkeletonLoader() {
        const overlay = document.querySelector('.skeleton-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    /**
     * Setup performance optimizations
     */
    function setupPerformanceOptimizations() {
        // Image lazy loading
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));

        // Preload critical resources
        preloadCriticalResources();

        // Optimize animations
        optimizeAnimations();
    }

    /**
     * Preload critical resources
     */
    function preloadCriticalResources() {
        const criticalResources = [
            '/static/css/theme.css',
            '/static/js/process.js'
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = resource.endsWith('.css') ? 'style' : 'script';
            document.head.appendChild(link);
        });
    }

    /**
     * Optimize animations for performance
     */
    function optimizeAnimations() {
        // Reduce motion for users who prefer it
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.style.setProperty('--animation-duration', '0.01ms');
        }

        // Use transform and opacity for better performance
        const animatedElements = document.querySelectorAll('[class*="animate-"]');
        animatedElements.forEach(el => {
            el.style.willChange = 'transform, opacity';
        });
    }

    /**
     * Get prefetch statistics
     */
    function getStats() {
        return {
            ...prefetchStats,
            cacheSize: prefetchCache.size,
            activePrefetches: activePrefetches.size,
            hitRate: prefetchStats.total > 0 ? (prefetchStats.hits / prefetchStats.total * 100).toFixed(1) + '%' : '0%'
        };
    }

    /**
     * Clear prefetch cache
     */
    function clearCache() {
        prefetchCache.clear();
        console.log('Prefetch cache cleared');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose utilities globally for debugging
    window.GlosentraPrefetch = {
        getStats,
        clearCache,
        prefetchPage
    };

    // Handle browser back/forward
    window.addEventListener('popstate', () => {
        // Re-initialize for new page
        setTimeout(() => {
            setupLinkPrefetching();
            setupSkeletonLoading();
        }, 100);
    });

})();
