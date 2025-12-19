/**
 * SmartKeja - Main Application Entry Point
 */

import { Navigation } from './components/navigation.js';
import { Filters } from './components/filters.js';
import { Search } from './components/search.js';
import { PropertyListings } from './components/property-listings.js';
import { Booking } from './components/booking.js';
import { lazyLoadImages } from './utils/helpers.js';

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize PropertyListings first (shared dependency)
    const propertyListings = new PropertyListings();
    
    // Initialize all components with dependencies
    new Navigation();
    new Filters(propertyListings);
    new Search(propertyListings);
    new Booking();
    
    // Lazy load images
    lazyLoadImages();
    
    // Add any global event listeners
    setupGlobalListeners();
    
    console.log('SmartKeja application initialized');
});

function setupGlobalListeners() {
    // Handle form submissions (only for forms that need custom handling)
    // Exclude signup, login, and other standard Django forms
    document.querySelectorAll('form').forEach(form => {
        // Skip forms that should submit normally (signup, login, etc.)
        if (form.id === 'signup-form' || form.id === 'login-form' || 
            form.action.includes('/signup/') || form.action.includes('/login/') ||
            form.action.includes('/accounts/')) {
            return; // Let these forms submit normally
        }
        
        // Only prevent default for forms that need custom handling
        form.addEventListener('submit', (e) => {
            // Check if form has a data-no-prevent attribute
            if (!form.hasAttribute('data-no-prevent')) {
                e.preventDefault();
                // Form handling will be done by individual components
            }
        });
    });
    
    // Handle file uploads with preview
    document.querySelectorAll('input[type="file"][accept="image/*"]').forEach(input => {
        input.addEventListener('change', (e) => {
            handleImagePreview(e.target);
        });
    });
}

function handleImagePreview(input) {
    const files = input.files;
    if (!files || files.length === 0) return;
    
    const previewContainer = input.parentElement.querySelector('.image-preview');
    if (!previewContainer) {
        const container = document.createElement('div');
        container.className = 'image-preview mt-3 d-flex flex-wrap gap-2';
        input.parentElement.appendChild(container);
    }
    
    Array.from(files).forEach(file => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'img-thumbnail';
                img.style.width = '150px';
                img.style.height = '150px';
                img.style.objectFit = 'cover';
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    });
}

