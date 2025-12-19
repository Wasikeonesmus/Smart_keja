/**
 * SmartKeja - Navigation Component
 */

import { scrollToElement } from '../utils/helpers.js';

export class Navigation {
    constructor() {
        this.navbar = document.querySelector('.navbar');
        this.init();
    }

    init() {
        this.setupSmoothScrolling();
        this.setupNavbarScroll();
        this.setupMobileMenu();
    }

    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href !== '#' && document.querySelector(href)) {
                    e.preventDefault();
                    scrollToElement(href);
                }
            });
        });
    }

    setupNavbarScroll() {
        let lastScroll = 0;
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 100) {
                this.navbar.classList.add('shadow-sm');
            } else {
                this.navbar.classList.remove('shadow-sm');
            }
            
            lastScroll = currentScroll;
        });
    }

    setupMobileMenu() {
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    }
                }
            });
        });
    }
}

