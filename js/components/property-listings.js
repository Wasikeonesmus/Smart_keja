/**
 * SmartKeja - Property Listings Component
 */

import { formatCurrency } from '../utils/helpers.js';

export class PropertyListings {
    constructor() {
        this.properties = [];
        this.filteredProperties = [];
        this.currentView = 'grid'; // grid, list, map
        this.allPropertiesMap = null; // For map view with all properties
        this.init();
    }

    init() {
        this.loadProperties();
        this.setupViewToggle();
        this.renderProperties();
    }

    loadProperties() {
        // Sample property data - in real app, this would come from an API
        this.properties = [
            {
                id: 1,
                name: 'Modern 2BR Apartment',
                location: 'Kilimani, Nairobi',
                price: 35000,
                bedrooms: 2,
                bathrooms: 2,
                type: 'apartment',
                verified: true,
                available: true,
                rating: 4.8,
                reviews: 24,
                trustScore: 85,
                image: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=300&fit=crop',
                description: 'Spacious apartment with modern amenities, parking, and security.'
            },
            {
                id: 2,
                name: 'Luxury 3BR Penthouse',
                location: 'Westlands, Nairobi',
                price: 85000,
                bedrooms: 3,
                bathrooms: 3,
                type: 'apartment',
                verified: true,
                available: true,
                rating: 4.9,
                reviews: 41,
                trustScore: 92,
                image: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=300&fit=crop',
                description: 'Stunning penthouse with rooftop terrace and city views.'
            },
            {
                id: 3,
                name: 'Cozy Studio Apartment',
                location: 'Parklands, Nairobi',
                price: 18000,
                bedrooms: 0,
                bathrooms: 1,
                type: 'studio',
                verified: false,
                available: true,
                rating: 4.6,
                reviews: 18,
                trustScore: 78,
                image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&h=300&fit=crop',
                description: 'Perfect for young professionals, near public transport.'
            }
        ];
        
        this.filteredProperties = [...this.properties];
    }

    setupViewToggle() {
        const viewRadios = document.querySelectorAll('input[name="view"]');
        viewRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentView = e.target.id.replace('View', '');
                this.renderProperties();
            });
        });
    }

    filterProperties(filters) {
        this.filteredProperties = this.properties.filter(property => {
            // County/Estate filter (location-based)
            if (filters.county && !property.location.toLowerCase().includes(filters.county.toLowerCase())) {
                return false;
            }
            if (filters.estate && !property.location.toLowerCase().includes(filters.estate.toLowerCase())) {
                return false;
            }

            // Price range
            if (filters.minPrice && property.price < parseInt(filters.minPrice)) {
                return false;
            }
            if (filters.maxPrice && property.price > parseInt(filters.maxPrice)) {
                return false;
            }

            // Bedrooms
            if (filters.bedrooms) {
                const bedFilter = parseInt(filters.bedrooms);
                if (bedFilter === 4 && property.bedrooms < 4) {
                    return false;
                } else if (bedFilter !== 4 && property.bedrooms !== bedFilter) {
                    return false;
                }
            }

            // Property type
            if (filters.propertyType && filters.propertyType.length > 0) {
                if (!filters.propertyType.includes(property.type)) {
                    return false;
                }
            }

            // Verified
            if (filters.verified && !property.verified) {
                return false;
            }

            return true;
        });

        this.updateResultsCount();
        this.renderProperties();
    }

    searchProperties(searchTerms) {
        this.filteredProperties = this.properties.filter(property => {
            const searchableText = `
                ${property.name} 
                ${property.location} 
                ${property.description}
                ${property.type}
            `.toLowerCase();

            return searchTerms.every(term => searchableText.includes(term));
        });

        this.updateResultsCount();
        this.renderProperties();
    }

    showAllProperties() {
        this.filteredProperties = [...this.properties];
        this.updateResultsCount();
        this.renderProperties();
    }

    updateResultsCount() {
        const countElement = document.querySelector('#resultsCount');
        if (countElement) {
            countElement.textContent = `${this.filteredProperties.length} properties found`;
        }
    }

    renderProperties() {
        const container = document.querySelector('#listings');
        if (!container) return;

        // Clear existing properties
        container.innerHTML = '';

        if (this.filteredProperties.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-inbox fs-1 text-muted mb-3"></i>
                    <h4>No properties found</h4>
                    <p class="text-muted">Try adjusting your filters or search terms</p>
                </div>
            `;
            return;
        }

        // Update container class based on view
        container.className = 'row g-4';
        if (this.currentView === 'list') {
            container.classList.add('listings-list');
        } else {
            container.classList.add('listings-grid');
        }

        // Render properties
        this.filteredProperties.forEach(property => {
            const propertyCard = this.createPropertyCard(property);
            container.appendChild(propertyCard);
        });

        // Add fade-in animation
        container.querySelectorAll('.property-card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
        
        // Dispatch event to notify that properties have been rendered
        document.dispatchEvent(new CustomEvent('propertiesRendered'));
    }

    createPropertyCard(property) {
        const col = document.createElement('div');
        // Improved responsive breakpoints
        if (this.currentView === 'list') {
            col.className = 'col-12';
        } else {
            col.className = 'col-12 col-sm-6 col-md-6 col-lg-4';
        }

        const availabilityBadge = property.available 
            ? '<span class="badge bg-success">Available</span>'
            : '<span class="badge bg-danger">Unavailable</span>';

        const verifiedBadge = property.verified
            ? '<div class="trust-badge"><i class="bi bi-shield-check text-success me-1"></i><strong>AI Verified</strong></div>'
            : '<div class="trust-badge"><i class="bi bi-award text-primary me-1"></i><strong>Best Value</strong></div>';

        const bedroomText = property.bedrooms === 0 ? 'Studio' : `${property.bedrooms} Bed`;

        col.innerHTML = `
            <div class="card property-card shadow-sm h-100">
                <div class="position-relative">
                    <img src="${property.image}" class="card-img-top" alt="${property.name}" loading="lazy">
                    ${verifiedBadge}
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">${property.name}</h5>
                        ${availabilityBadge}
                    </div>
                    <p class="text-muted mb-2">
                        <i class="bi bi-geo-alt"></i> ${property.location}
                        ${property.latitude && property.longitude ? `
                            <button class="btn btn-link btn-sm p-0 ms-2 text-primary" onclick="showPropertyMap(${property.latitude}, ${property.longitude}, '${property.name}', '${property.location}')" title="View on Map">
                                <i class="bi bi-map"></i> View Map
                            </button>
                        ` : ''}
                    </p>
                    ${property.latitude && property.longitude ? `
                        <div class="property-map-container mb-2" style="height: 180px; border-radius: 8px; overflow: hidden; border: 1px solid #dee2e6;" 
                             data-lat="${property.latitude}" 
                             data-lng="${property.longitude}"
                             data-property-id="${property.id}">
                            <div class="w-100 h-100 d-flex align-items-center justify-content-center bg-light position-relative">
                                <div class="text-center position-absolute" style="z-index: 1000;">
                                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                                        <span class="visually-hidden">Loading map...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="d-flex gap-2 mb-2">
                            <a href="https://www.google.com/maps?q=${property.latitude},${property.longitude}" target="_blank" class="btn btn-sm btn-outline-primary flex-fill">
                                <i class="bi bi-google me-1"></i>Google Maps
                            </a>
                            <a href="https://www.google.com/maps/dir/?api=1&destination=${property.latitude},${property.longitude}" target="_blank" class="btn btn-sm btn-outline-primary flex-fill">
                                <i class="bi bi-signpost-2 me-1"></i>Directions
                            </a>
                        </div>
                    ` : ''}
                    <p class="card-text small">${property.description}</p>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="text-muted small">
                            <i class="bi bi-house me-1"></i> ${bedroomText}
                            <i class="bi bi-droplet ms-2 me-1"></i> ${property.bathrooms} Bath
                        </div>
                        <div>
                            <i class="bi bi-star-fill text-warning"></i>
                            <strong>${property.rating}</strong>
                            <small class="text-muted">(${property.reviews})</small>
                        </div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="h4 text-primary mb-0">${formatCurrency(property.price)}</div>
                            <small class="text-muted">per month</small>
                        </div>
                        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#bookingModal" data-property-id="${property.id}">
                            Book Viewing
                        </button>
                    </div>
                    <div class="progress progress-thin mt-3">
                        <div class="progress-bar bg-success" style="width: ${property.trustScore}%"></div>
                    </div>
                    <small class="text-muted">Trust Score: ${property.trustScore}%</small>
                </div>
            </div>
        `;

        return col;
    }
}

