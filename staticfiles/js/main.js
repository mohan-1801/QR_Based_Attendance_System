// Theme Switcher & Global JS Logic
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const htmlElement = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars-fill text-primary';
        }
    }

    // Sidebar Toggle
    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Auto-hide Django Alert Messages after 5s
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
