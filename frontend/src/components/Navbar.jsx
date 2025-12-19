import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Home, Search, User, LogOut, Menu } from 'lucide-react'
import { useState } from 'react'
import './Navbar.css'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">🏠</div>
          <span className="brand-text">SmartKeja</span>
        </Link>

        <button 
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <Menu size={24} />
        </button>

        <div className={`navbar-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <Link to="/" className="navbar-link">
            <Home size={18} />
            <span>Home</span>
          </Link>
          <Link to="/search" className="navbar-link">
            <Search size={18} />
            <span>Search</span>
          </Link>

          {user ? (
            <>
              <Link to="/dashboard" className="navbar-link">
                <User size={18} />
                <span>Dashboard</span>
              </Link>
              <button onClick={handleLogout} className="btn btn-outline">
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary">
                Sign In
              </Link>
              <Link to="/signup" className="btn btn-primary">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar

