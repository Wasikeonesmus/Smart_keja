import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { MapPin, Bed, Bath, Star, Filter, Search as SearchIcon } from 'lucide-react'
import './Search.css'

const Search = () => {
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    search: '',
    county: '',
    minPrice: '',
    maxPrice: '',
    bedrooms: '',
    propertyType: ''
  })

  useEffect(() => {
    fetchProperties()
  }, [filters])

  const fetchProperties = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
      
      const response = await axios.get(`/api/properties/?${params}`)
      setProperties(response.data.properties || [])
    } catch (error) {
      console.error('Error fetching properties:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value })
  }

  return (
    <div className="search-page">
      <div className="container">
        <div className="search-header">
          <h1>Find Your Perfect Property</h1>
          <p>Search through verified properties across Kenya</p>
        </div>

        <div className="search-layout">
          <aside className="filters-sidebar">
            <div className="filters-card">
              <h3 className="filters-title">
                <Filter size={20} />
                Filters
              </h3>
              
              <div className="filter-group">
                <label className="filter-label">Search</label>
                <div className="search-input-wrapper">
                  <SearchIcon size={18} />
                  <input
                    type="text"
                    placeholder="Search properties..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    className="filter-input"
                  />
                </div>
              </div>

              <div className="filter-group">
                <label className="filter-label">County</label>
                <input
                  type="text"
                  placeholder="e.g., Nairobi"
                  value={filters.county}
                  onChange={(e) => handleFilterChange('county', e.target.value)}
                  className="filter-input"
                />
              </div>

              <div className="filter-group">
                <label className="filter-label">Price Range</label>
                <div className="price-inputs">
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.minPrice}
                    onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                    className="filter-input"
                  />
                  <span>to</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.maxPrice}
                    onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                    className="filter-input"
                  />
                </div>
              </div>

              <div className="filter-group">
                <label className="filter-label">Bedrooms</label>
                <select
                  value={filters.bedrooms}
                  onChange={(e) => handleFilterChange('bedrooms', e.target.value)}
                  className="filter-input"
                >
                  <option value="">Any</option>
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                  <option value="4">4+</option>
                </select>
              </div>
            </div>
          </aside>

          <main className="search-results">
            {loading ? (
              <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading properties...</p>
              </div>
            ) : (
              <>
                <div className="results-header">
                  <p className="results-count">
                    {properties.length} properties found
                  </p>
                </div>
                <div className="properties-grid">
                  {properties.map((property) => (
                    <PropertyCard key={property.id} property={property} />
                  ))}
                </div>
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}

const PropertyCard = ({ property }) => {
  return (
    <Link to={`/property/${property.id}`} className="property-card">
      <div className="property-image">
        <img 
          src={property.image || '/placeholder-property.jpg'} 
          alt={property.name}
          loading="lazy"
        />
        {property.verified && (
          <span className="verified-badge">✓ Verified</span>
        )}
      </div>
      <div className="property-info">
        <h3 className="property-name">{property.name}</h3>
        <p className="property-location">
          <MapPin size={16} />
          {property.location}
        </p>
        <div className="property-features">
          <span>
            <Bed size={16} />
            {property.bedrooms}
          </span>
          <span>
            <Bath size={16} />
            {property.bathrooms}
          </span>
        </div>
        <div className="property-footer">
          <div className="property-price">
            <span className="price-amount">KES {property.price?.toLocaleString()}</span>
            <span className="price-period">/month</span>
          </div>
          {property.rating > 0 && (
            <div className="property-rating">
              <Star size={16} fill="currentColor" />
              <span>{property.rating}</span>
            </div>
          )}
        </div>
      </div>
    </Link>
  )
}

export default Search

