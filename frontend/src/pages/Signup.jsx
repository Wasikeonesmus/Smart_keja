import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { User, Mail, Lock, ArrowRight } from 'lucide-react'
import './Auth.css'

const Signup = () => {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password1: '',
    password2: ''
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    // Clear error when user types
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: '' })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)

    const result = await signup(
      formData.username,
      formData.email,
      formData.password1,
      formData.password2
    )

    if (result.success) {
      navigate('/dashboard')
    } else {
      setErrors({ general: result.error || 'Signup failed. Please try again.' })
    }

    setLoading(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Create Account</h1>
            <p>Join SmartKeja and start your property journey</p>
          </div>

          {errors.general && (
            <div className="alert alert-error">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label className="form-label">
                <User size={18} />
                Username
              </label>
              <input
                type="text"
                name="username"
                className="form-input"
                value={formData.username}
                onChange={handleChange}
                required
                placeholder="Enter your username"
              />
              {errors.username && <div className="form-error">{errors.username}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">
                <Mail size={18} />
                Email
              </label>
              <input
                type="email"
                name="email"
                className="form-input"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Enter your email"
              />
              {errors.email && <div className="form-error">{errors.email}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">
                <Lock size={18} />
                Password
              </label>
              <input
                type="password"
                name="password1"
                className="form-input"
                value={formData.password1}
                onChange={handleChange}
                required
                placeholder="Create a password"
              />
              {errors.password1 && <div className="form-error">{errors.password1}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">
                <Lock size={18} />
                Confirm Password
              </label>
              <input
                type="password"
                name="password2"
                className="form-input"
                value={formData.password2}
                onChange={handleChange}
                required
                placeholder="Confirm your password"
              />
              {errors.password2 && <div className="form-error">{errors.password2}</div>}
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-full btn-lg"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
              {!loading && <ArrowRight size={20} />}
            </button>
          </form>

          <p className="auth-footer">
            Already have an account?{' '}
            <Link to="/login" className="auth-link">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Signup

