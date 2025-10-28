// Theme Switcher
(function() {
    'use strict';
    
    // Theme state
    let isDark = false;
    
    // DOM elements
    let themeToggle;
    let body;
    
    // Initialize theme switcher
    function init() {
        body = document.body;
        createToggleButton();
        loadSavedTheme();
        setupEventListeners();
        
        // Debug: Log current theme state
        console.log('Theme switcher initialized. Current theme:', isDark ? 'dark' : 'light');
        console.log('Saved theme:', localStorage.getItem('theme'));
        console.log('System prefers dark:', window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
    
    // Create the theme toggle button
    function createToggleButton() {
        themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle';
        themeToggle.setAttribute('aria-label', 'Toggle theme');
        themeToggle.setAttribute('title', 'Toggle theme');
        themeToggle.setAttribute('type', 'button');
        themeToggle.setAttribute('role', 'button');
        
        // Ensure proper positioning
        themeToggle.style.position = 'fixed';
        themeToggle.style.top = '20px';
        themeToggle.style.right = '20px';
        themeToggle.style.zIndex = '1000';
        
        document.body.appendChild(themeToggle);
    }
    
    // Load saved theme from localStorage
    function loadSavedTheme() {
        const savedTheme = localStorage.getItem('theme');
        
        if (savedTheme === 'dark') {
            isDark = true;
        } else if (savedTheme === 'light') {
            isDark = false;
        } else {
            // No saved preference - check system preference
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                isDark = true;
            } else {
                isDark = false;
            }
        }
        
        applyTheme();
        updateToggleIcon();
    }
    
    // Apply the current theme
    function applyTheme() {
        if (isDark) {
            body.classList.add('dark-theme');
        } else {
            body.classList.remove('dark-theme');
        }
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
    
    // Update the toggle button icon
    function updateToggleIcon() {
        themeToggle.textContent = isDark ? '☀️' : '🌙';
    }
    
    // Toggle between themes
    function toggleTheme() {
        isDark = !isDark;
        applyTheme();
        updateToggleIcon();
        
        // Debug: Log theme change
        console.log('Theme toggled to:', isDark ? 'dark' : 'light');
    }
    
    // Reset to system theme (useful for testing)
    function resetToSystemTheme() {
        localStorage.removeItem('theme');
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            isDark = true;
        } else {
            isDark = false;
        }
        applyTheme();
        updateToggleIcon();
        console.log('Reset to system theme:', isDark ? 'dark' : 'light');
    }
    
    // Expose reset function globally for debugging
    window.resetTheme = resetToSystemTheme;
    
    // Setup event listeners
    function setupEventListeners() {
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
            themeToggle.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleTheme();
                }
            });
        }
        
        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', function(e) {
                // Only apply system preference if user hasn't manually set a preference
                const savedTheme = localStorage.getItem('theme');
                if (!savedTheme) {
                    isDark = e.matches;
                    applyTheme();
                    updateToggleIcon();
                }
            });
        }
        
        // Handle window resize for mobile responsiveness
        window.addEventListener('resize', function() {
            if (themeToggle && window.innerWidth <= 768) {
                themeToggle.style.top = '15px';
                themeToggle.style.right = '15px';
            } else if (themeToggle) {
                themeToggle.style.top = '20px';
                themeToggle.style.right = '20px';
            }
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
