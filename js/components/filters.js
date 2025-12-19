/**
 * SmartKeja - Filters Component
 */

import { debounce, setUrlParams, getUrlParams } from '../utils/helpers.js';

export class Filters {
    constructor(propertyListings) {
        this.filters = {
            county: '',
            estate: '',
            minPrice: '',
            maxPrice: '',
            bedrooms: '',
            propertyType: [],
            verified: true
        };
        this.propertyListings = propertyListings;
        this.init();
    }

    init() {
        this.loadFiltersFromURL();
        this.setupEventListeners();
        this.setupPriceRange();
    }

    loadFiltersFromURL() {
        const params = getUrlParams();
        Object.keys(params).forEach(key => {
            if (this.filters.hasOwnProperty(key)) {
                if (key === 'propertyType') {
                    this.filters[key] = params[key].split(',');
                } else {
                    this.filters[key] = params[key];
                }
            }
        });
        this.applyFiltersToUI();
    }

    applyFiltersToUI() {
        // County
        const countySelect = document.querySelector('#filterCounty');
        if (countySelect && this.filters.county) {
            countySelect.value = this.filters.county;
        }

        // Estate
        const estateSelect = document.querySelector('#filterEstate');
        if (estateSelect && this.filters.estate) {
            estateSelect.value = this.filters.estate;
        }

        // Price range
        const minPriceInput = document.querySelector('#filterMinPrice');
        const maxPriceInput = document.querySelector('#filterMaxPrice');
        const priceRange = document.querySelector('#priceRange');
        if (minPriceInput && this.filters.minPrice) {
            minPriceInput.value = this.filters.minPrice;
        }
        if (maxPriceInput && this.filters.maxPrice) {
            maxPriceInput.value = this.filters.maxPrice;
        }
        if (priceRange && this.filters.maxPrice) {
            priceRange.value = this.filters.maxPrice;
        }

        // Bedrooms
        const bedroomRadios = document.querySelectorAll('input[name="bedrooms"]');
        bedroomRadios.forEach(radio => {
            if (radio.value === this.filters.bedrooms) {
                radio.checked = true;
            }
        });

        // Property type checkboxes
        const propertyTypeCheckboxes = document.querySelectorAll('input[type="checkbox"][id^="type"]');
        propertyTypeCheckboxes.forEach(checkbox => {
            checkbox.checked = this.filters.propertyType.includes(checkbox.value);
        });

        // Verified toggle
        const verifiedToggle = document.querySelector('#filterVerified');
        if (verifiedToggle) {
            verifiedToggle.checked = this.filters.verified;
        }
    }

    setupEventListeners() {
        // County selection
        const countySelect = document.querySelector('#filterCounty');
        if (countySelect) {
            countySelect.addEventListener('change', (e) => {
                this.filters.county = e.target.value;
                this.updateEstateOptions();
                this.applyFilters();
            });
        }

        // Estate selection
        const estateSelect = document.querySelector('#filterEstate');
        if (estateSelect) {
            estateSelect.addEventListener('change', (e) => {
                this.filters.estate = e.target.value;
                this.applyFilters();
            });
        }

        // Price inputs
        const minPriceInput = document.querySelector('#filterMinPrice');
        const maxPriceInput = document.querySelector('#filterMaxPrice');
        const priceRange = document.querySelector('#priceRange');
        
        if (minPriceInput) {
            minPriceInput.addEventListener('input', debounce((e) => {
                this.filters.minPrice = e.target.value;
                if (priceRange) priceRange.value = e.target.value;
                this.applyFilters();
            }, 500));
        }

        if (maxPriceInput) {
            maxPriceInput.addEventListener('input', debounce((e) => {
                this.filters.maxPrice = e.target.value;
                if (priceRange) priceRange.value = e.target.value;
                this.applyFilters();
            }, 500));
        }

        if (priceRange) {
            priceRange.addEventListener('input', (e) => {
                this.filters.maxPrice = e.target.value;
                if (maxPriceInput) maxPriceInput.value = e.target.value;
                this.applyFilters();
            });
        }

        // Bedrooms
        const bedroomRadios = document.querySelectorAll('input[name="bedrooms"]');
        bedroomRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.filters.bedrooms = e.target.value;
                this.applyFilters();
            });
        });

        // Property type checkboxes
        const propertyTypeCheckboxes = document.querySelectorAll('input[type="checkbox"][id^="type"]');
        propertyTypeCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updatePropertyTypeFilter();
                this.applyFilters();
            });
        });

        // Verified toggle
        const verifiedToggle = document.querySelector('#filterVerified');
        if (verifiedToggle) {
            verifiedToggle.addEventListener('change', (e) => {
                this.filters.verified = e.target.checked;
                this.applyFilters();
            });
        }

        // Apply and Reset buttons
        const applyBtn = document.querySelector('#applyFilters');
        const resetBtn = document.querySelector('#resetFilters');
        
        if (applyBtn) {
            applyBtn.addEventListener('click', () => this.applyFilters());
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetFilters());
        }
    }

    setupPriceRange() {
        const priceRange = document.querySelector('#priceRange');
        const maxPriceInput = document.querySelector('#filterMaxPrice');
        
        if (priceRange && maxPriceInput) {
            priceRange.addEventListener('input', (e) => {
                maxPriceInput.value = e.target.value;
            });
        }
    }

    updateEstateOptions() {
        const estateSelect = document.querySelector('#filterEstate');
        if (!estateSelect) return;

        const estatesByCounty = {
            'Nairobi': ['Kilimani', 'Westlands', 'Karen', 'Parklands', 'Lavington', 'Kileleshwa'],
            'Mombasa': ['Nyali', 'Bamburi', 'Mtwapa', 'Likoni'],
            'Kisumu': ['Milimani', 'Kisumu Central', 'Nyalenda']
        };

        estateSelect.innerHTML = '<option value="">Select Estate</option>';
        
        if (this.filters.county && estatesByCounty[this.filters.county]) {
            estatesByCounty[this.filters.county].forEach(estate => {
                const option = document.createElement('option');
                option.value = estate;
                option.textContent = estate;
                estateSelect.appendChild(option);
            });
        }
    }

    updatePropertyTypeFilter() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][id^="type"]');
        this.filters.propertyType = Array.from(checkboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value || cb.id.replace('type', '').toLowerCase());
    }

    applyFilters() {
        // Update URL
        setUrlParams(this.filters);
        
        // Filter properties
        this.propertyListings.filterProperties(this.filters);
        
        // Update active filter badges
        this.updateFilterBadges();
    }

    resetFilters() {
        this.filters = {
            county: '',
            estate: '',
            minPrice: '',
            maxPrice: '',
            bedrooms: '',
            propertyType: [],
            verified: true
        };
        
        // Reset UI
        document.querySelectorAll('#filterCounty, #filterEstate, #filterMinPrice, #filterMaxPrice').forEach(input => {
            if (input) input.value = '';
        });
        
        document.querySelectorAll('input[name="bedrooms"]').forEach(radio => {
            radio.checked = false;
        });
        
        document.querySelectorAll('input[type="checkbox"][id^="type"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        const verifiedToggle = document.querySelector('#filterVerified');
        if (verifiedToggle) verifiedToggle.checked = true;
        
        this.applyFilters();
    }

    updateFilterBadges() {
        const badgesContainer = document.querySelector('#activeFilters');
        if (!badgesContainer) return;

        badgesContainer.innerHTML = '';
        
        if (this.filters.county) {
            badgesContainer.appendChild(this.createFilterBadge('county', this.filters.county));
        }
        if (this.filters.estate) {
            badgesContainer.appendChild(this.createFilterBadge('estate', this.filters.estate));
        }
        if (this.filters.bedrooms) {
            badgesContainer.appendChild(this.createFilterBadge('bedrooms', `${this.filters.bedrooms} Bedroom`));
        }
        if (this.filters.minPrice || this.filters.maxPrice) {
            const priceRange = `KSh ${this.filters.minPrice || '0'}-${this.filters.maxPrice || '100k+'}`;
            badgesContainer.appendChild(this.createFilterBadge('price', priceRange));
        }
    }

    createFilterBadge(key, value) {
        const badge = document.createElement('span');
        badge.className = 'badge bg-secondary me-2 mb-2';
        badge.innerHTML = `${value} <i class="bi bi-x-circle ms-1" data-filter="${key}"></i>`;
        
        badge.querySelector('i').addEventListener('click', () => {
            this.filters[key] = '';
            this.applyFilters();
        });
        
        return badge;
    }
}

