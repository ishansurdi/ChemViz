/**
 * Main Layout Component
 * Contains navigation and outlet for nested routes
 */

import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import Footer from './Footer'
import { useState } from 'react'

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-bg-base flex flex-col">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex flex-1">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 lg:ml-64 flex flex-col">
          <div className="container-custom py-8 flex-1">
            <Outlet />
          </div>
          <Footer />
        </main>
      </div>
    </div>
  )
}

export default Layout
