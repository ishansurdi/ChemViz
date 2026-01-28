/**
 * DataTable Page
 * Display equipment records in a table with pagination
 */

import { useState, useEffect } from 'react'
import { quickAPI } from '../services/api'
import toast from 'react-hot-toast'
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  TableCellsIcon,
} from '@heroicons/react/24/outline'

function DataTable() {
  const [data, setData] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 50,
    total_records: 0,
    total_pages: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData(pagination.page)
  }, [])

  const fetchData = async (page) => {
    setLoading(true)
    try {
      const response = await quickAPI.data({
        page,
        page_size: pagination.page_size,
      })

      if (response.data.success) {
        setData(response.data.data.equipment || [])
        setPagination({
          page: response.data.data.page || page,
          page_size: response.data.data.page_size || 50,
          total_records: response.data.data.total_equipment || 0,
          total_pages: response.data.data.total_pages || 0,
        })
      }
    } catch (error) {
      console.error('Error fetching data:', error)
      toast.error('Failed to load equipment data')
    } finally {
      setLoading(false)
    }
  }

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.total_pages) {
      fetchData(newPage)
    }
  }

  if (loading && data.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-ash text-sm font-mono">Loading data...</p>
        </div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="card p-12 text-center">
        <TableCellsIcon className="w-16 h-16 text-ash mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-charcoal mb-4">No Data Available</h2>
        <p className="text-slate mb-6">
          Please upload a dataset first to view equipment records
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-charcoal mb-2 font-heading">
          Equipment Data Table
        </h1>
        <p className="text-slate">
          Viewing {pagination?.total_records || 0} equipment records
        </p>
      </div>

      {/* Table Card */}
      <div className="card overflow-hidden">
        {/* Table */}
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th className="w-12">#</th>
                <th>Equipment Name</th>
                <th>Type</th>
                <th className="text-center">Flowrate<br/><span className="text-[10px] text-ash font-normal">(L/min)</span></th>
                <th className="text-center">Pressure<br/><span className="text-[10px] text-ash font-normal">(Bar)</span></th>
                <th className="text-center">Temperature<br/><span className="text-[10px] text-ash font-normal">(°C)</span></th>
              </tr>
            </thead>
            <tbody>
              {data.map((equipment, index) => (
                <tr key={equipment.id}>
                  <td className="font-mono text-xs text-ash">
                    {(pagination.page - 1) * pagination.page_size + index + 1}
                  </td>
                  <td className="font-semibold">{equipment.equipment_name}</td>
                  <td>
                    <span className="badge badge-info">{equipment.equipment_type}</span>
                  </td>
                  <td className="text-center font-mono">{equipment.flowrate.toFixed(2)}</td>
                  <td className="text-center font-mono">{equipment.pressure.toFixed(2)}</td>
                  <td className="text-center font-mono">{equipment.temperature.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 px-6 py-4 border-t border-border bg-bg-base">
          <div className="text-sm text-slate">
            Showing{' '}
            <span className="font-semibold">
              {(pagination.page - 1) * pagination.page_size + 1}
            </span>{' '}
            to{' '}
            <span className="font-semibold">
              {Math.min(pagination.page * pagination.page_size, pagination.total_records)}
            </span>{' '}
            of <span className="font-semibold">{pagination.total_records}</span> results
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(pagination.page - 1)}
              disabled={pagination.page === 1 || loading}
              className="p-2 rounded-md border border-border hover:bg-surface disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeftIcon className="w-5 h-5 text-slate" />
            </button>

            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(pagination.total_pages, 5) }, (_, i) => {
                let pageNum
                if (pagination.total_pages <= 5) {
                  pageNum = i + 1
                } else if (pagination.page <= 3) {
                  pageNum = i + 1
                } else if (pagination.page >= pagination.total_pages - 2) {
                  pageNum = pagination.total_pages - 4 + i
                } else {
                  pageNum = pagination.page - 2 + i
                }

                return (
                  <button
                    key={i}
                    onClick={() => handlePageChange(pageNum)}
                    disabled={loading}
                    className={`w-10 h-10 rounded-md font-semibold text-sm transition-colors ${
                      pagination.page === pageNum
                        ? 'bg-industrial-blue text-white'
                        : 'border border-border hover:bg-surface text-slate'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}
            </div>

            <button
              onClick={() => handlePageChange(pagination.page + 1)}
              disabled={pagination.page === pagination.total_pages || loading}
              className="p-2 rounded-md border border-border hover:bg-surface disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRightIcon className="w-5 h-5 text-slate" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <p className="text-sm text-ash uppercase tracking-wider mb-1">Total Records</p>
          <p className="text-2xl font-bold text-charcoal font-heading">
            {pagination.total_records}
          </p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-sm text-ash uppercase tracking-wider mb-1">Current Page</p>
          <p className="text-2xl font-bold text-charcoal font-heading">
            {pagination.page}
          </p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-sm text-ash uppercase tracking-wider mb-1">Total Pages</p>
          <p className="text-2xl font-bold text-charcoal font-heading">
            {pagination.total_pages}
          </p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-sm text-ash uppercase tracking-wider mb-1">Per Page</p>
          <p className="text-2xl font-bold text-charcoal font-heading">
            {pagination.page_size}
          </p>
        </div>
      </div>
    </div>
  )
}

export default DataTable
