import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { User, Lock, ArrowRight } from 'lucide-react'
import './Auth.css'

const Login = () => {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(formData.username, formData.password)

    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error || 'Invalid username or password')
    }

    setLoading(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Welcome Back</h1>
            <p>Sign in to your SmartKeja account</p>
          </div>

          {error && (
            <div className="alert alert-error">
              {error}
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
                autoFocus
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <Lock size={18} />
                Password
              </label>
              <input
                type="password"
                name="password"
                className="form-input"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-full btn-lg"
              disabled={loading}
            >
              {loading ? 'Signing In...' : 'Sign In'}
              {!loading && <ArrowRight size={20} />}
            </button>
          </form>

          <p className="auth-footer">
            Don't have an account?{' '}
            <Link to="/signup" className="auth-link">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login

