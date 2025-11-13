/**
 * Mobile Menu Toggle
 * Handles hamburger menu open/close functionality
 */

(function() {
    'use strict';

    function initMobileMenu() {
        const menuButton = document.getElementById('mobile-menu-button');
        const menuOverlay = document.getElementById('mobile-menu-overlay');
        const menuClose = document.getElementById('mobile-menu-close');
        const menuBackdrop = menuOverlay?.querySelector('.mobile-menu-backdrop');
        
        if (!menuButton || !menuOverlay) {
            console.warn('Mobile menu elements not found');
            return;
        }
        
        function openMenu() {
            menuOverlay.classList.add('active');
            menuButton.setAttribute('aria-expanded', 'true');
            menuOverlay.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
        
        function closeMenu() {
            menuOverlay.classList.remove('active');
            menuButton.setAttribute('aria-expanded', 'false');
            menuOverlay.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }
        
        // Button click handler
        menuButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            openMenu();
        });
        
        // Close button handler
        if (menuClose) {
            menuClose.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeMenu();
            });
        }
        
        // Backdrop click handler
        if (menuBackdrop) {
            menuBackdrop.addEventListener('click', function(e) {
                e.stopPropagation();
                closeMenu();
            });
        }
        
        // Close menu when clicking any link
        const menuLinks = menuOverlay.querySelectorAll('.mobile-menu-link');
        menuLinks.forEach(link => {
            link.addEventListener('click', closeMenu);
        });
        
        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && menuOverlay.classList.contains('active')) {
                closeMenu();
            }
        });
    }

    // Initialize after templates are loaded
    document.addEventListener('templatesLoaded', initMobileMenu);
})();
