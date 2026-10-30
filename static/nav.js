    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');

    menuToggle.addEventListener('click', function() {
        navMenu.classList.toggle('show');
        const icon = this.querySelector('i');
        if (navMenu.classList.contains('show')) {
            icon.className = 'fas fa-times';
        } else {
            icon.className = 'fas fa-bars';
        }
    });

    // ===== CLOSE MENU ON LINK CLICK (MOBILE) =====
    document.querySelectorAll('.nav-links-custom a').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('show');
            menuToggle.querySelector('i').className = 'fas fa-bars';
        });
    });
