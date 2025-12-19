/**
 * SmartKeja - Property Listings Component
 */

import { formatCurrency } from '../utils/helpers.js';

export class PropertyListings {
    constructor() {
        this.properties = [];
        this.filteredProperties = [];
        this.currentView = 'grid'; // grid, list, map
        this.init();
    }

    init() {
        this.loadProperties();
        this.setupViewToggle();
        this.renderProperties();
    }

    async loadProperties() {
        // Load properties from Django API
        try {
            const apiUrl = window.DJANGO_API_URL || '/api/properties/';
            const response = await fetch(apiUrl);
            const data = await response.json();
            this.properties = data.properties || [];
            console.log('Loaded properties:', this.properties.length, this.properties);
        } catch (error) {
            console.error('Error loading properties:', error);
            // Fallback to sample data
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
        }
        
        this.filteredProperties = [...this.properties];
        // Re-render after loading
        this.renderProperties();
    }

    setupViewToggle() {
        const viewRadios = document.querySelectorAll('input[name="view"]');
        viewRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentView = e.target.id.replace('View', '');
                if (this.currentView === 'map') {
                    this.renderMapView();
                } else {
                    this.renderProperties();
                }
            });
        });
    }
    
    async renderMapView() {
        const container = document.querySelector('#listings');
        if (!container) return;
        
        container.innerHTML = '<div id="allPropertiesMap" style="height: 600px; width: 100%; border-radius: 8px; overflow: hidden;"></div>';
        
        // Initialize map with all properties
        setTimeout(() => {
            this.initializeAllPropertiesMap();
        }, 300);
    }
    
    async initializeAllPropertiesMap() {
        // Load Leaflet and MarkerClusterGroup
        if (!window.L) {
            await this.loadLeaflet();
        }
        
        if (!window.L.markerClusterGroup) {
            await this.loadMarkerCluster();
        }
        
        const mapContainer = document.getElementById('allPropertiesMap');
        if (!mapContainer || !window.L) return;
        
        // Clear container
        mapContainer.innerHTML = '';
        
        // Create map
        this.allPropertiesMap = L.map('allPropertiesMap', {
            zoomControl: true,
            dragging: true,
            touchZoom: true,
            doubleClickZoom: true,
            scrollWheelZoom: true
        });
        
        // Set initial view to center of all properties or default
        const propertiesWithCoords = this.filteredProperties.filter(p => p.latitude && p.longitude);
        
        if (propertiesWithCoords.length > 0) {
            const avgLat = propertiesWithCoords.reduce((sum, p) => sum + parseFloat(p.latitude), 0) / propertiesWithCoords.length;
            const avgLng = propertiesWithCoords.reduce((sum, p) => sum + parseFloat(p.longitude), 0) / propertiesWithCoords.length;
            this.allPropertiesMap.setView([avgLat, avgLng], 12);
        } else {
            this.allPropertiesMap.setView([-1.2921, 36.8219], 12); // Nairobi default
        }
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 19
        }).addTo(this.allPropertiesMap);
        
        // Create marker cluster group
        const markers = L.markerClusterGroup({
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true
        });
        
        // Add markers for each property
        propertiesWithCoords.forEach(property => {
            const lat = parseFloat(property.latitude);
            const lng = parseFloat(property.longitude);
            
            const marker = L.marker([lat, lng], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                })
            });
            
            // Create popup content
            const popupContent = `
                <div style="min-width: 200px;">
                    <h6 class="mb-2">${property.name}</h6>
                    <p class="small mb-1"><i class="bi bi-geo-alt"></i> ${property.location}</p>
                    <p class="small mb-1"><strong>${formatCurrency(property.price)}/month</strong></p>
                    <p class="small mb-2">${property.bedrooms} Bed • ${property.bathrooms} Bath</p>
                    <button class="btn btn-sm btn-primary w-100" onclick="window.location.href='#property-${property.id}'">
                        View Details
                    </button>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            markers.addLayer(marker);
        });
        
        // Add markers to map
        this.allPropertiesMap.addLayer(markers);
        
        // Fit map to show all markers
        if (propertiesWithCoords.length > 0) {
            this.allPropertiesMap.fitBounds(markers.getBounds(), { padding: [50, 50] });
        }
        
        // Invalidate size to ensure proper rendering
        setTimeout(() => {
            this.allPropertiesMap.invalidateSize();
        }, 100);
    }
    
    loadLeaflet() {
        return new Promise((resolve) => {
            if (window.L) {
                resolve();
                return;
            }
            
            const cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
            document.head.appendChild(cssLink);
            
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }
    
    loadMarkerCluster() {
        return new Promise((resolve) => {
            if (window.L && window.L.markerClusterGroup) {
                resolve();
                return;
            }
            
            const cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css';
            document.head.appendChild(cssLink);
            
            const cssLink2 = document.createElement('link');
            cssLink2.rel = 'stylesheet';
            cssLink2.href = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css';
            document.head.appendChild(cssLink2);
            
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js';
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }

    async filterProperties(filters) {
        // Fetch filtered properties from Django API
        try {
            const apiUrl = window.DJANGO_API_URL || '/api/properties/';
            const params = new URLSearchParams();
            
            if (filters.county) params.append('county', filters.county);
            if (filters.estate) params.append('estate', filters.estate);
            if (filters.minPrice) params.append('minPrice', filters.minPrice);
            if (filters.maxPrice) params.append('maxPrice', filters.maxPrice);
            if (filters.bedrooms) params.append('bedrooms', filters.bedrooms);
            if (filters.propertyType && filters.propertyType.length > 0) {
                filters.propertyType.forEach(type => params.append('propertyType', type));
            }
            params.append('verified', filters.verified);
            
            const response = await fetch(`${apiUrl}?${params.toString()}`);
            const data = await response.json();
            this.filteredProperties = data.properties || [];
        } catch (error) {
            console.error('Error filtering properties:', error);
            // Fallback to client-side filtering
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
        }
        
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
        container.className = 'row';
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
        
        // Dispatch event to initialize maps after properties are rendered
        setTimeout(() => {
            document.dispatchEvent(new CustomEvent('propertiesLoaded'));
        }, 100);

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

        // Ensure all fields have default values
        const prop = {
            id: property.id || 0,
            name: property.name || 'Unnamed Property',
            location: property.location || 'Location not specified',
            price: property.price || 0,
            bedrooms: property.bedrooms !== undefined ? property.bedrooms : 0,
            bathrooms: property.bathrooms || 1,
            type: property.type || 'apartment',
            verified: property.verified || false,
            available: property.available !== undefined ? property.available : true,
            rating: property.rating || 0.0,
            reviews: property.reviews || property.review_count || 0,
            trustScore: property.trustScore || property.trust_score || 0,
            image: property.image || 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=300&fit=crop',
            description: property.description || 'No description available',
            latitude: property.latitude || null,
            longitude: property.longitude || null
        };

        // Fix image URL if it's relative
        if (prop.image && !prop.image.startsWith('http') && !prop.image.startsWith('/')) {
            prop.image = '/' + prop.image;
        }

        const availabilityBadge = prop.available 
            ? '<span class="badge bg-success">Available</span>'
            : '<span class="badge bg-danger">Unavailable</span>';

        const verifiedBadge = prop.verified
            ? '<div class="trust-badge"><i class="bi bi-shield-check text-success me-1"></i><strong>AI Verified</strong></div>'
            : '<div class="trust-badge"><i class="bi bi-award text-primary me-1"></i><strong>Best Value</strong></div>';

        const bedroomText = prop.bedrooms === 0 ? 'Studio' : `${prop.bedrooms} Bed`;

        col.innerHTML = `
            <div class="card property-card shadow-sm h-100">
                <!-- Property Image - Large and Centered -->
                <div class="property-image-wrapper">
                    <img src="${prop.image}" class="property-image" alt="${prop.name}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=600&fit=crop'">
                    ${verifiedBadge}
                    <div class="image-overlay"></div>
                </div>
                
                <!-- Property Information Section -->
                <div class="card-body property-info-section">
                    <!-- Title and Availability Badge -->
                    <div class="property-header">
                        <h4 class="property-title">${prop.name}</h4>
                        ${availabilityBadge}
                    </div>
                    
                    <!-- Location -->
                    <div class="property-location">
                        <i class="bi bi-geo-alt-fill"></i>
                        <span>${prop.location}</span>
                    </div>
                    
                    <!-- Description -->
                    <p class="property-description">${prop.description}</p>
                    
                    <!-- Property Details Grid -->
                    <div class="property-features">
                        <div class="feature-item">
                            <i class="bi bi-house-door-fill"></i>
                            <span>${bedroomText}</span>
                        </div>
                        <div class="feature-item">
                            <i class="bi bi-droplet-fill"></i>
                            <span>${prop.bathrooms} Bath</span>
                        </div>
                        <div class="feature-item rating-item">
                            <i class="bi bi-star-fill"></i>
                            <span><strong>${prop.rating.toFixed(1)}</strong> <small>(${prop.reviews})</small></span>
                        </div>
                    </div>
                    
                    <!-- Price and Booking Section -->
                    <div class="property-pricing">
                        <div class="price-display">
                            <span class="price-amount">${formatCurrency(prop.price)}</span>
                            <span class="price-period">per month</span>
                        </div>
                        <button class="btn btn-primary btn-booking" data-bs-toggle="modal" data-bs-target="#bookingModal" data-property-id="${prop.id}">
                            <i class="bi bi-calendar-check me-2"></i>Book Viewing
                        </button>
                    </div>
                    
                    <!-- Trust Score -->
                    <div class="trust-score-section">
                        <div class="trust-label">
                            <i class="bi bi-shield-check"></i>
                            <span>Trust Score</span>
                        </div>
                        <div class="progress progress-trust">
                            <div class="progress-bar bg-success" style="width: ${Math.min(100, Math.max(0, prop.trustScore))}%"></div>
                        </div>
                        <span class="trust-value">${prop.trustScore}%</span>
                    </div>
                </div>
                
                <!-- Map Section - Below Property Info -->
                ${prop.latitude && prop.longitude ? `
                <div class="property-map-section">
                    <div class="map-header">
                        <i class="bi bi-map-fill"></i>
                        <h6>Location Map</h6>
                    </div>
                    <div class="property-map-container" 
                         data-lat="${prop.latitude}" 
                         data-lng="${prop.longitude}"
                         data-property-id="${prop.id}">
                        <div class="map-loading">
                            <div class="spinner-border spinner-border-sm text-primary" role="status">
                                <span class="visually-hidden">Loading map...</span>
                            </div>
                        </div>
                    </div>
                    <div class="map-actions">
                        <a href="https://www.google.com/maps?q=${prop.latitude},${prop.longitude}" target="_blank" class="btn btn-outline-primary btn-map-action">
                            <i class="bi bi-google"></i>
                            <span>Google Maps</span>
                        </a>
                        <a href="https://www.google.com/maps/dir/?api=1&destination=${prop.latitude},${prop.longitude}" target="_blank" class="btn btn-outline-primary btn-map-action">
                            <i class="bi bi-signpost-2"></i>
                            <span>Directions</span>
                        </a>
                        <button class="btn btn-outline-primary btn-map-action" onclick="showPropertyMap(${prop.latitude}, ${prop.longitude}, '${prop.name}', '${prop.location}')" title="View Full Map">
                            <i class="bi bi-arrows-fullscreen"></i>
                            <span>Full Map</span>
                        </button>
                    </div>
                </div>
                ` : ''}
            </div>
        `;

        return col;
    }
    
    // Public method to refresh properties
    async refresh() {
        await this.loadProperties();
    }
}

