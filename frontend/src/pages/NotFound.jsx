/**
 * 404 Not Found Page
 */

import { Link } from 'react-router-dom'
import { HomeIcon } from '@heroicons/react/24/outline'

function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base px-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-industrial-blue font-heading mb-4">404</h1>
        <h2 className="text-3xl font-bold text-charcoal mb-4">Page Not Found</h2>
        <p className="text-slate mb-8 max-w-md">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link to="/dashboard" className="btn btn-primary inline-flex items-center gap-2">
          <HomeIcon className="w-5 h-5" />
          <span>Back to Dashboard</span>
        </Link>
      </div>
    </div>
  )
}

export default NotFound
