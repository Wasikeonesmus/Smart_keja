import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { MapPin, Bed, Bath, Star, Calendar } from 'lucide-react'
import './PropertyDetails.css'

const PropertyDetails = () => {
  const { id } = useParams()
  const [property, setProperty] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProperty()
  }, [id])

  const fetchProperty = async () => {
    try {
      const response = await axios.get(`/api/properties/${id}/`)
      setProperty(response.data)
    } catch (error) {
      console.error('Error fetching property:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="property-details-loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (!property) {
    return <div className="property-details-error">Property not found</div>
  }

  return (
    <div className="property-details">
      <div className="container">
        <div className="property-header">
          <h1>{property.name}</h1>
          <p className="property-location">
            <MapPin size={20} />
            {property.location}
          </p>
        </div>

        <div className="property-content">
          <div className="property-main">
            <div className="property-image-large">
              <img src={property.image || '/placeholder-property.jpg'} alt={property.name} />
            </div>

            <div className="property-info-section">
              <h2>About this property</h2>
              <p>{property.description}</p>
            </div>
          </div>

          <aside className="property-sidebar">
            <div className="booking-card">
              <div className="price-display">
                <span className="price-amount">KES {property.price?.toLocaleString()}</span>
                <span className="price-period">/month</span>
              </div>
              <button className="btn btn-primary btn-full btn-lg">
                <Calendar size={20} />
                Book Viewing
              </button>
            </div>

            <div className="property-features-card">
              <h3>Features</h3>
              <div className="features-list">
                <div className="feature-item">
                  <Bed size={20} />
                  <span>{property.bedrooms} Bedrooms</span>
                </div>
                <div className="feature-item">
                  <Bath size={20} />
                  <span>{property.bathrooms} Bathrooms</span>
                </div>
                {property.rating > 0 && (
                  <div className="feature-item">
                    <Star size={20} fill="currentColor" />
                    <span>Rating: {property.rating}</span>
                  </div>
                )}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  )
}

export default PropertyDetails

