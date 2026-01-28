/**
 * Navbar Component
 * Top navigation bar with logo, status, and user menu
 */

import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Bars3Icon } from '@heroicons/react/24/outline'

function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth()

  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-border">
      <div className="max-w-full px-6 h-16 flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center gap-8">
          {/* Mobile Menu Button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-md hover:bg-bg-base transition-colors"
          >
            <Bars3Icon className="w-6 h-6 text-slate" />
          </button>

          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-3">
            <div className="w-7 h-7 bg-industrial-blue rounded flex items-center justify-center text-white font-bold text-sm">
              C
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold tracking-tight text-charcoal font-heading">
                ChemViz
              </span>
              <span className="text-[8px] text-ash font-bold tracking-[0.2em] uppercase leading-none font-mono">
                Industrial Intelligence
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-8">
            <NavLink to="/dashboard">Analyzer</NavLink>
            <NavLink to="/upload">Upload</NavLink>
            <NavLink to="/history">Archives</NavLink>
            <NavLink to="/analytics">Analytics</NavLink>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-6">
          {/* Status Indicator */}
          <div className="hidden sm:flex items-center gap-2 font-mono text-[10px] text-ash">
            <span className="w-1.5 h-1.5 rounded-full bg-green-600 animate-pulse"></span>
            SYSTEM_ACTIVE
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-semibold text-charcoal">{user?.username}</p>
              <p className="text-xs text-ash">{user?.email}</p>
            </div>
            <button
              onClick={logout}
              className="btn btn-secondary !py-1.5 !px-5 !text-[11px] uppercase tracking-wider"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

function NavLink({ to, children }) {
  return (
    <Link
      to={to}
      className="text-[11px] font-bold uppercase tracking-widest text-slate hover:text-industrial-blue transition-colors"
    >
      {children}
    </Link>
  )
}

export default Navbar
