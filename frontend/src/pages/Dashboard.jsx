import { useAuth } from '../context/AuthContext'
import { User, Home, Calendar, Wallet } from 'lucide-react'
import './Dashboard.css'

const Dashboard = () => {
  const { user } = useAuth()

  return (
    <div className="dashboard">
      <div className="container">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <p>Welcome back, {user?.username || 'User'}!</p>
        </div>

        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-icon">
              <Home size={24} />
            </div>
            <div className="stat-info">
              <h3>My Properties</h3>
              <p className="stat-value">0</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Calendar size={24} />
            </div>
            <div className="stat-info">
              <h3>Bookings</h3>
              <p className="stat-value">0</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Wallet size={24} />
            </div>
            <div className="stat-info">
              <h3>Wallet Balance</h3>
              <p className="stat-value">KES 0</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

