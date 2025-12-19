/**
 * SmartKeja - Search Component
 */

import { debounce } from '../utils/helpers.js';

export class Search {
    constructor(propertyListings) {
        this.searchInput = document.querySelector('#searchInput');
        this.searchButton = document.querySelector('#searchButton');
        this.propertyListings = propertyListings;
        this.init();
    }

    init() {
        if (this.searchInput) {
            // Real-time search with debounce
            this.searchInput.addEventListener('input', debounce((e) => {
                this.performSearch(e.target.value);
            }, 300));

            // Search on Enter key
            this.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(e.target.value);
                }
            });
        }

        if (this.searchButton) {
            this.searchButton.addEventListener('click', () => {
                const query = this.searchInput ? this.searchInput.value : '';
                this.performSearch(query);
            });
        }
    }

    performSearch(query) {
        if (!query.trim()) {
            this.propertyListings.showAllProperties();
            return;
        }

        const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
        this.propertyListings.searchProperties(searchTerms);
    }

    getSearchQuery() {
        return this.searchInput ? this.searchInput.value : '';
    }

    setSearchQuery(query) {
        if (this.searchInput) {
            this.searchInput.value = query;
            this.performSearch(query);
        }
    }
}

