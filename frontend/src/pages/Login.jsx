/**
 * Login Page
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ArrowRightIcon } from '@heroicons/react/24/outline'

function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    const result = await login(formData.username, formData.password)

    if (result.success) {
      navigate('/dashboard')
    }

    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base px-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-12 h-12 bg-industrial-blue rounded-md flex items-center justify-center text-white font-bold text-xl">
              C
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold tracking-tight text-charcoal font-heading">
                ChemViz
              </h1>
              <p className="text-[10px] text-ash font-bold tracking-[0.2em] uppercase font-mono">
                Industrial Intelligence
              </p>
            </div>
          </div>
          <h2 className="text-3xl font-bold text-charcoal mb-2">Welcome Back</h2>
          <p className="text-slate">Sign in to access your analytics workspace</p>
        </div>

        {/* Login Form */}
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="label">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                autoComplete="username"
                value={formData.username}
                onChange={handleChange}
                className="input"
                placeholder="Enter your username"
              />
            </div>

            <div>
              <label htmlFor="password" className="label">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                value={formData.password}
                onChange={handleChange}
                className="input"
                placeholder="Enter your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="spinner !w-5 !h-5 !border-2"></div>
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRightIcon className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="mt-8 pt-6 border-t border-border">
            <p className="text-center text-sm text-slate">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="font-semibold text-industrial-blue hover:text-industrial-blue-hover"
              >
                Create one now
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-ash font-mono uppercase tracking-wider">
          Secure Authentication • IITB FOSSEE Project
        </p>
      </div>
    </div>
  )
}

export default Login
