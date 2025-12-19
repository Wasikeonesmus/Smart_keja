/**
 * SmartKeja - Map Location Component
 * OpenStreetMap integration with Leaflet.js
 */

export class MapLocation {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.map = null;
        this.marker = null;
        this.coordinates = { lat: null, lng: null };
        this.locationData = {
            county: '',
            subCounty: '',
            estate: ''
        };
        this.onLocationChange = options.onLocationChange || null;
        this.initialLocation = options.initialLocation || { lat: -1.2921, lng: 36.8219 }; // Nairobi center
        this.init();
    }

    async init() {
        // Load Leaflet CSS and JS if not already loaded
        if (!window.L) {
            await this.loadLeaflet();
        }
        
        // Wait a bit for DOM to be ready
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Ensure container exists before initializing map
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Map container #${this.containerId} not found. Retrying...`);
            // Retry after a delay
            setTimeout(() => {
                if (document.getElementById(this.containerId)) {
                    this.initMap();
                    this.setupLocationPicker();
                } else {
                    console.error(`Map container #${this.containerId} still not found after retry`);
                }
            }, 500);
            return;
        }
        
        this.initMap();
        this.setupLocationPicker();
    }

    loadLeaflet() {
        return new Promise((resolve, reject) => {
            if (window.L) {
                resolve();
                return;
            }

            // Load Leaflet CSS
            const cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
            cssLink.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
            cssLink.crossOrigin = '';
            document.head.appendChild(cssLink);

            // Load Leaflet JS
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
            script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
            script.crossOrigin = '';
            script.async = true;
            script.defer = true;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    initMap() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Map container #${this.containerId} not found`);
            return;
        }

        // Ensure container has height - make it larger for better interaction
        if (!container.style.height && container.offsetHeight === 0) {
            container.style.height = '600px';
            container.style.minHeight = '600px';
        }

        // Check if Leaflet is loaded
        if (!window.L) {
            console.error('Leaflet library not loaded');
            container.innerHTML = '<div class="alert alert-danger">Map library failed to load. Please refresh the page.</div>';
            return;
        }

        try {
            // Clear any loading message
            container.innerHTML = '';
            
            // Ensure container is visible
            container.style.display = 'block';
            container.style.visibility = 'visible';
            container.style.position = 'relative';
            container.style.cursor = 'crosshair';
            
            // Create coordinate display overlay
            this.createCoordinateDisplay(container);
            
            // Initialize map with OpenStreetMap tiles
            this.map = L.map(container, {
                center: [this.initialLocation.lat, this.initialLocation.lng],
                zoom: 12,
                zoomControl: true,
                touchZoom: true,
                doubleClickZoom: true,
                scrollWheelZoom: true,
                boxZoom: true,
                keyboard: true,
                dragging: true
            });

            // Add OpenStreetMap tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19,
                errorTileUrl: 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
            }).addTo(this.map);

            console.log('Map initialized successfully');

            // Force map to invalidate size after a short delay
            setTimeout(() => {
                if (this.map) {
                    this.map.invalidateSize();
                    console.log('Map size invalidated');
                }
            }, 500);
        } catch (error) {
            console.error('Error initializing map:', error);
            container.innerHTML = `<div class="alert alert-danger">Error loading map: ${error.message}</div>`;
        }

        // Add click listener to drop pin with visual feedback
        this.map.on('click', (e) => {
            this.showClickRipple(e.containerPoint.x, e.containerPoint.y, container);
            this.setMarker(e.latlng.lat, e.latlng.lng);
            this.reverseGeocode(e.latlng.lat, e.latlng.lng);
        });

        // Add touch support for mobile/tablet/pen
        this.map.on('touchstart', (e) => {
            if (e.originalEvent.touches.length === 1) {
                const touch = e.originalEvent.touches[0];
                const point = this.map.mouseEventToContainerPoint(e.originalEvent);
                this.showClickRipple(point.x, point.y, container);
            }
        });

        this.map.on('touchend', (e) => {
            if (e.originalEvent.changedTouches.length === 1 && !e.originalEvent.defaultPrevented) {
                const touch = e.originalEvent.changedTouches[0];
                const latlng = this.map.containerPointToLatLng(
                    this.map.mouseEventToContainerPoint(touch)
                );
                this.setMarker(latlng.lat, latlng.lng);
                this.reverseGeocode(latlng.lat, latlng.lng);
            }
        });

        // Try to get user's current location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    this.map.setView([userLocation.lat, userLocation.lng], 12);
                    this.setMarker(userLocation.lat, userLocation.lng);
                    this.reverseGeocode(userLocation.lat, userLocation.lng);
                },
                () => {
                    // Use default location if geolocation fails
                    this.setMarker(this.initialLocation.lat, this.initialLocation.lng);
                }
            );
        }
    }

    createCoordinateDisplay(container) {
        // Create a floating coordinate display panel
        const coordPanel = document.createElement('div');
        coordPanel.id = 'mapCoordinateDisplay';
        coordPanel.className = 'map-coordinate-display';
        coordPanel.innerHTML = `
            <div class="coord-label">📍 Location</div>
            <div class="coord-value" id="coordLat">Lat: --</div>
            <div class="coord-value" id="coordLng">Lng: --</div>
            <div class="coord-hint">Click or tap on map to set location</div>
        `;
        container.appendChild(coordPanel);
        this.coordPanel = coordPanel;
    }

    showClickRipple(x, y, container) {
        // Create ripple effect at click point
        const ripple = document.createElement('div');
        ripple.className = 'map-click-ripple';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        container.appendChild(ripple);

        // Animate ripple
        setTimeout(() => {
            ripple.style.transform = 'scale(3)';
            ripple.style.opacity = '0';
        }, 10);

        // Remove ripple after animation
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }

    setMarker(lat, lng) {
        this.coordinates = { lat, lng };

        // Update coordinate display
        if (this.coordPanel) {
            const latEl = document.getElementById('coordLat');
            const lngEl = document.getElementById('coordLng');
            if (latEl) latEl.textContent = `Lat: ${lat.toFixed(6)}`;
            if (lngEl) lngEl.textContent = `Lng: ${lng.toFixed(6)}`;
        }

        if (this.marker) {
            // Animate marker movement
            this.marker.setLatLng([lat, lng]);
            this.animateMarker();
        } else {
            // Create custom, more visible icon
            const icon = L.divIcon({
                className: 'custom-marker-icon',
                html: `
                    <div class="marker-pin">
                        <div class="marker-pulse"></div>
                        <svg width="40" height="50" viewBox="0 0 40 50" xmlns="http://www.w3.org/2000/svg">
                            <path d="M20 0C9 0 0 9 0 20C0 35 20 50 20 50C20 50 40 35 40 20C40 9 31 0 20 0Z" fill="#dc3545"/>
                            <circle cx="20" cy="20" r="8" fill="white"/>
                        </svg>
                    </div>
                `,
                iconSize: [40, 50],
                iconAnchor: [20, 50],
                popupAnchor: [0, -50]
            });

            this.marker = L.marker([lat, lng], {
                icon: icon,
                draggable: true,
                keyboard: true
            }).addTo(this.map);

            // Add popup with coordinates
            this.marker.bindPopup(`
                <div class="marker-popup">
                    <strong>📍 Property Location</strong><br>
                    Latitude: ${lat.toFixed(6)}<br>
                    Longitude: ${lng.toFixed(6)}<br>
                    <small>Drag to adjust</small>
                </div>
            `).openPopup();

            // Update position when marker is dragged
            this.marker.on('dragstart', () => {
                this.marker.closePopup();
            });

            this.marker.on('dragend', (e) => {
                const newLat = e.target.getLatLng().lat;
                const newLng = e.target.getLatLng().lng;
                this.coordinates = { lat: newLat, lng: newLng };
                
                // Update coordinate display
                if (this.coordPanel) {
                    const latEl = document.getElementById('coordLat');
                    const lngEl = document.getElementById('coordLng');
                    if (latEl) latEl.textContent = `Lat: ${newLat.toFixed(6)}`;
                    if (lngEl) lngEl.textContent = `Lng: ${newLng.toFixed(6)}`;
                }
                
                this.reverseGeocode(newLat, newLng);
                this.animateMarker();
            });

            // Animate marker on click
            this.marker.on('click', () => {
                this.animateMarker();
            });
        }

        // Smoothly pan to marker if it's far away
        const currentCenter = this.map.getCenter();
        const distance = this.map.distance(currentCenter, [lat, lng]);
        if (distance > 1000) {
            this.map.setView([lat, lng], this.map.getZoom(), { animate: true, duration: 0.5 });
        } else {
            this.map.setView([lat, lng], this.map.getZoom());
        }

        if (this.onLocationChange) {
            this.onLocationChange(this.coordinates, this.locationData);
        }
    }

    animateMarker() {
        // Add bounce animation to marker
        if (this.marker && this.marker._icon) {
            const icon = this.marker._icon;
            icon.style.transition = 'transform 0.3s ease';
            icon.style.transform = 'scale(1.2)';
            setTimeout(() => {
                icon.style.transform = 'scale(1)';
            }, 300);
        }
    }

    async reverseGeocode(lat, lng) {
        // Use Nominatim (OpenStreetMap's geocoding service)
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
                {
                    headers: {
                        'User-Agent': 'SmartKeja Property Platform'
                    }
                }
            );
            
            const data = await response.json();
            
            if (data && data.address) {
                // Extract location data from OpenStreetMap address structure
                const addr = data.address;
                
                // Map OpenStreetMap address fields to our structure
                if (addr.state || addr.region) {
                    this.locationData.county = addr.state || addr.region || '';
                }
                if (addr.suburb || addr.neighbourhood || addr.village) {
                    this.locationData.estate = addr.suburb || addr.neighbourhood || addr.village || '';
                }
                if (addr.county) {
                    this.locationData.subCounty = addr.county;
                }

                if (this.onLocationChange) {
                    this.onLocationChange(this.coordinates, this.locationData);
                }
            }
        } catch (error) {
            console.error('Reverse geocoding error:', error);
        }
    }

    setupLocationPicker() {
        // Initialize location hierarchy dropdowns
        this.initLocationHierarchy();
    }

    async initLocationHierarchy() {
        // Fetch location hierarchy from Django API
        try {
            const response = await fetch('/api/locations/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Location API response:', data);
            
            // API returns {locations: [...]}, so extract the array
            let locations = [];
            if (Array.isArray(data)) {
                locations = data;
            } else if (data && Array.isArray(data.locations)) {
                locations = data.locations;
            } else if (data && typeof data === 'object') {
                // Try to find any array property
                const arrayKeys = Object.keys(data).filter(key => Array.isArray(data[key]));
                if (arrayKeys.length > 0) {
                    locations = data[arrayKeys[0]];
                }
            }
            
            if (!Array.isArray(locations) || locations.length === 0) {
                console.warn('No valid locations array found, using defaults');
                locations = this.getDefaultLocations();
            }
            
            this.populateLocationDropdowns(locations);
        } catch (error) {
            console.error('Error loading location hierarchy:', error);
            // Use default Kenya locations
            this.populateLocationDropdowns(this.getDefaultLocations());
        }
    }

    populateLocationDropdowns(locations) {
        const countySelect = document.getElementById('propertyCounty');
        const subCountySelect = document.getElementById('propertySubCounty');
        const estateSelect = document.getElementById('propertyEstate');

        if (!countySelect) return;

        // Ensure locations is an array
        if (!Array.isArray(locations)) {
            console.error('Locations data is not an array:', locations);
            locations = this.getDefaultLocations();
        }

        // Populate counties
        const counties = [...new Set(locations.map(loc => loc.county))];
        counties.forEach(county => {
            const option = document.createElement('option');
            option.value = county;
            option.textContent = county;
            countySelect.appendChild(option);
        });

        // County change handler
        countySelect.addEventListener('change', (e) => {
            const selectedCounty = e.target.value;
            this.locationData.county = selectedCounty;
            
            // Populate sub-counties
            const subCounties = locations
                .filter(loc => loc.county === selectedCounty)
                .map(loc => loc.sub_county)
                .filter((v, i, a) => a.indexOf(v) === i && v);
            
            subCountySelect.innerHTML = '<option value="">Select Sub-county</option>';
            subCounties.forEach(subCounty => {
                const option = document.createElement('option');
                option.value = subCounty;
                option.textContent = subCounty;
                subCountySelect.appendChild(option);
            });

            this.updateMapCenter(selectedCounty);
        });

        // Sub-county change handler
        subCountySelect.addEventListener('change', (e) => {
            this.locationData.subCounty = e.target.value;
            const selectedSubCounty = e.target.value;
            
            // Populate estates
            const estates = locations
                .filter(loc => loc.county === this.locationData.county && 
                              (!selectedSubCounty || loc.sub_county === selectedSubCounty))
                .map(loc => loc.estate)
                .filter((v, i, a) => a.indexOf(v) === i);
            
            estateSelect.innerHTML = '<option value="">Select Estate</option>';
            estates.forEach(estate => {
                const option = document.createElement('option');
                option.value = estate;
                option.textContent = estate;
                estateSelect.appendChild(option);
            });
        });

        // Estate change handler
        estateSelect.addEventListener('change', (e) => {
            this.locationData.estate = e.target.value;
            const selectedEstate = locations.find(loc => 
                loc.county === this.locationData.county &&
                loc.estate === e.target.value
            );
            
            if (selectedEstate && selectedEstate.center_latitude && selectedEstate.center_longitude) {
                const lat = parseFloat(selectedEstate.center_latitude);
                const lng = parseFloat(selectedEstate.center_longitude);
                this.map.setView([lat, lng], 12);
                this.setMarker(lat, lng);
            }
        });
    }

    updateMapCenter(county) {
        // Center map on selected county (you can add county centers to database)
        const countyCenters = {
            'Nairobi': { lat: -1.2921, lng: 36.8219 },
            'Mombasa': { lat: -4.0435, lng: 39.6682 },
            'Kisumu': { lat: -0.0917, lng: 34.7680 }
        };

        if (countyCenters[county]) {
            this.map.setView([countyCenters[county].lat, countyCenters[county].lng], 12);
        }
    }

    getDefaultLocations() {
        return [
            { county: 'Nairobi', sub_county: 'Nairobi West', estate: 'Kilimani' },
            { county: 'Nairobi', sub_county: 'Nairobi West', estate: 'Westlands' },
            { county: 'Nairobi', sub_county: 'Nairobi West', estate: 'Parklands' },
            { county: 'Nairobi', sub_county: 'Nairobi South', estate: 'Karen' },
            { county: 'Mombasa', sub_county: 'Nyali', estate: 'Nyali' },
            { county: 'Kisumu', sub_county: 'Kisumu Central', estate: 'Milimani' }
        ];
    }

    getCoordinates() {
        return this.coordinates;
    }

    getLocationData() {
        return this.locationData;
    }

    setLocationData(county, subCounty, estate) {
        this.locationData = { county, subCounty, estate };
    }
}


