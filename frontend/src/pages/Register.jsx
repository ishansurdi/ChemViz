/**
 * Register Page
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { UserPlusIcon } from '@heroicons/react/24/outline'
import Footer from '../components/Footer'

function Register() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    // Validate password length
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setLoading(true)

    const result = await register({
      username: formData.username,
      email: formData.email,
      password: formData.password,
      first_name: formData.first_name,
      last_name: formData.last_name,
    })

    if (result.success) {
      navigate('/dashboard')
    }

    setLoading(false)
  }

  return (
    <div className="min-h-screen flex flex-col bg-bg-base">
      <div className="flex-1 flex items-center justify-center px-4 py-12">
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
          <h2 className="text-3xl font-bold text-charcoal mb-2">Create Account</h2>
          <p className="text-slate">Join the industrial analytics platform</p>
        </div>

        {/* Register Form */}
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="label">
                  First Name
                </label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="input"
                  placeholder="John"
                />
              </div>

              <div>
                <label htmlFor="last_name" className="label">
                  Last Name
                </label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="input"
                  placeholder="Doe"
                />
              </div>
            </div>

            <div>
              <label htmlFor="username" className="label">
                Username <span className="text-red-500">*</span>
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
                placeholder="Choose a username"
              />
            </div>

            <div>
              <label htmlFor="email" className="label">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={formData.email}
                onChange={handleChange}
                className="input"
                placeholder="your.email@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="label">
                Password <span className="text-red-500">*</span>
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
                className="input"
                placeholder="At least 6 characters"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="label">
                Confirm Password <span className="text-red-500">*</span>
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="input"
                placeholder="Repeat your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full flex items-center justify-center gap-2 !mt-8"
            >
              {loading ? (
                <>
                  <div className="spinner !w-5 !h-5 !border-2"></div>
                  <span>Creating account...</span>
                </>
              ) : (
                <>
                  <UserPlusIcon className="w-5 h-5" />
                  <span>Create Account</span>
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="mt-8 pt-6 border-t border-border">
            <p className="text-center text-sm text-slate">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-semibold text-industrial-blue hover:text-industrial-blue-hover"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
      </div>
      <Footer />
    </div>
  )
}

export default Register
