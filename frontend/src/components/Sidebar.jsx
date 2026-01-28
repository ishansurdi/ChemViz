/**
 * Sidebar Component
 * Side navigation for mobile and desktop
 */

import { Link, useLocation } from 'react-router-dom'
import {
  HomeIcon,
  ArrowUpTrayIcon,
  ChartBarIcon,
  ClockIcon,
  TableCellsIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Upload Dataset', href: '/upload', icon: ArrowUpTrayIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Data Table', href: '/data', icon: TableCellsIcon },
  { name: 'History', href: '/history', icon: ClockIcon },
]

function Sidebar({ isOpen, onClose }) {
  const location = useLocation()

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-charcoal/50 z-40 lg:hidden"
          onClick={onClose}
        ></div>
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-screen w-64 bg-surface border-r border-border
          transform transition-transform duration-200 ease-in-out
          lg:translate-x-0 lg:mt-16
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Mobile Close Button */}
        <div className="lg:hidden flex items-center justify-between p-6 border-b border-border">
          <span className="font-heading font-bold text-lg text-charcoal">Menu</span>
          <button
            onClick={onClose}
            className="p-2 rounded-md hover:bg-bg-base transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-slate" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => onClose()}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-md transition-all duration-200
                  ${
                    isActive
                      ? 'bg-industrial-blue text-white shadow-sm'
                      : 'text-slate hover:bg-bg-base hover:text-charcoal'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span className="font-semibold text-sm">{item.name}</span>
              </Link>
            )
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-border">
          <div className="text-center">
            <p className="text-xs text-ash font-mono uppercase tracking-wider">
              v1.0.0
            </p>
            <p className="text-[10px] text-ash font-mono mt-1">
              IITB FOSSEE PROJECT
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}

export default Sidebar
