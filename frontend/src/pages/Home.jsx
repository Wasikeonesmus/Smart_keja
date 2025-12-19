import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { MapPin, Bed, Bath, Star, ArrowRight } from 'lucide-react'
import './Home.css'

const Home = () => {
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProperties()
  }, [])

  const fetchProperties = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/properties/')
      setProperties(response.data.properties || [])
    } catch (err) {
      console.error('Error fetching properties:', err)
      setError('Failed to load properties')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Find Your Perfect Home in Kenya
          </h1>
          <p className="hero-subtitle">
            Verified properties, trusted landlords, seamless renting experience
          </p>
          <Link to="/search" className="btn btn-primary btn-lg">
            Start Searching
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>

      {/* Featured Properties */}
      <section className="featured-properties">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Featured Properties</h2>
            <Link to="/search" className="view-all-link">
              View All <ArrowRight size={16} />
            </Link>
          </div>

          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Loading properties...</p>
            </div>
          ) : error ? (
            <div className="error-container">
              <p className="text-error">{error}</p>
            </div>
          ) : (
            <div className="properties-grid">
              {properties.slice(0, 6).map((property) => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>
          )}
        </div>
      </section>
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

export default Home

