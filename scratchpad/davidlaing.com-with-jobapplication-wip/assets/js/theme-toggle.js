// Theme toggle functionality for Solarized Dark/Light
(function() {
    'use strict';
    
    // Get stored theme or default to dark
    const getStoredTheme = () => localStorage.getItem('theme') || 'dark';
    const setStoredTheme = theme => localStorage.setItem('theme', theme);
    
    // Apply theme to document
    const applyTheme = theme => {
        document.documentElement.setAttribute('data-theme', theme);
        updateToggleText(theme);
    };
    
    // Update toggle button text
    const updateToggleText = theme => {
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
            toggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
        }
    };
    
    // Toggle between themes
    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        applyTheme(newTheme);
        setStoredTheme(newTheme);
    };
    
    // Initialize theme on page load
    const initTheme = () => {
        const storedTheme = getStoredTheme();
        applyTheme(storedTheme);
        
        // Add event listener to toggle button
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.addEventListener('click', toggleTheme);
        }
    };
    
    // Handle system theme changes
    const handleSystemThemeChange = (e) => {
        // Only auto-switch if user hasn't manually set a preference
        if (!localStorage.getItem('theme')) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    };
    
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', handleSystemThemeChange);
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
    
    // Keyboard shortcut for theme toggle (Ctrl/Cmd + Shift + T)
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            toggleTheme();
        }
    });
    
})();