// theme.js - Manages light/dark theme state based on localStorage
(function() {
    // Determine initial theme
    const savedTheme = localStorage.getItem('theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const initialTheme = savedTheme || 'dark'; // default to premium dark mode
    
    document.documentElement.setAttribute('data-theme', initialTheme);
    
    // Global theme toggle helper
    window.toggleTheme = function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Dispatch custom event for dynamically updating theme-aware items (like chart colors)
        window.dispatchEvent(new Event('themechange'));
    };
})();
