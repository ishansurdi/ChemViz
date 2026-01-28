/**
 * History Page
 * Display dataset upload history
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { datasetAPI } from '../services/api'
import toast from 'react-hot-toast'
import {
  ClockIcon,
  DocumentTextIcon,
  ChartBarIcon,
  DocumentArrowDownIcon,
} from '@heroicons/react/24/outline'

function History() {
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const response = await datasetAPI.history()
      if (response.data.success) {
        setDatasets(response.data.data)
      }
    } catch (error) {
      console.error('Error fetching history:', error)
      toast.error('Failed to load dataset history')
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = async (datasetId, datasetName) => {
    try {
      const response = await datasetAPI.report(datasetId)
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ChemViz_${datasetName}_Report.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Report downloaded successfully')
    } catch (error) {
      toast.error('Failed to generate report')
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-ash text-sm font-mono">Loading history...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-charcoal mb-2 font-heading">
            Dataset History
          </h1>
          <p className="text-slate">
            View and manage your uploaded datasets (Last 5 retained)
          </p>
        </div>
        <Link to="/upload" className="btn btn-primary">
          Upload New Dataset
        </Link>
      </div>

      {/* History List */}
      {datasets.length === 0 ? (
        <div className="card p-12 text-center">
          <ClockIcon className="w-16 h-16 text-ash mx-auto mb-4" />
          <h3 className="text-xl font-bold text-charcoal mb-2">No History Available</h3>
          <p className="text-slate mb-6">
            You haven't uploaded any datasets yet. Start by uploading your first CSV file.
          </p>
          <Link to="/upload" className="btn btn-primary">
            Upload Dataset
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {datasets.map((dataset, index) => (
            <div key={dataset.id} className="card p-6 hover:shadow-md transition-shadow">
              <div className="flex flex-col lg:flex-row lg:items-center gap-6">
                {/* Icon and Name */}
                <div className="flex items-start gap-4 flex-1">
                  <div className="w-12 h-12 bg-industrial-blue rounded-md flex items-center justify-center text-white font-bold flex-shrink-0">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold text-charcoal mb-1 truncate">
                      {dataset.name}
                    </h3>
                    <div className="flex flex-wrap gap-4 text-sm text-ash">
                      <span className="flex items-center gap-1">
                        <ClockIcon className="w-4 h-4" />
                        {formatDate(dataset.uploaded_at)}
                      </span>
                      {dataset.uploaded_by_username && (
                        <span>By: {dataset.uploaded_by_username}</span>
                      )}
                      <span>{formatFileSize(dataset.file_size)}</span>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 lg:gap-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-charcoal font-heading">
                      {dataset.total_equipment}
                    </p>
                    <p className="text-xs text-ash uppercase tracking-wider">Equipment</p>
                  </div>
                  <div className="text-center">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                        dataset.processing_status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : dataset.processing_status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {dataset.processing_status}
                    </span>
                    <p className="text-xs text-ash uppercase tracking-wider mt-1">Status</p>
                  </div>
                  <div className="col-span-2 md:col-span-1 flex items-center justify-center gap-2">
                    <button
                      onClick={() => downloadReport(dataset.id, dataset.name)}
                      className="btn btn-secondary !py-2 !px-4 !text-xs"
                      title="Download Report"
                      disabled={dataset.processing_status !== 'completed'}
                    >
                      <DocumentArrowDownIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Error Message */}
              {dataset.processing_status === 'failed' && dataset.error_message && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600">
                    <strong>Error:</strong> {dataset.error_message}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      {datasets.length > 0 && (
        <div className="card p-6 bg-blue-50 border-blue-200">
          <div className="flex gap-3">
            <DocumentTextIcon className="w-5 h-5 text-blue-600 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-semibold mb-1">Dataset Retention Policy</p>
              <p>
                The system automatically maintains the last 5 uploaded datasets. When you upload
                a 6th dataset, the oldest one will be automatically removed to maintain storage
                efficiency.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default History
