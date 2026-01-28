/**
 * Dashboard Page
 * Main landing page showing system overview and quick stats
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { quickAPI, datasetAPI } from '../services/api'
import toast from 'react-hot-toast'
import {
  ChartBarIcon,
  ArrowUpTrayIcon,
  DocumentArrowDownIcon,
  ClockIcon,
  ArrowDownTrayIcon,
  ComputerDesktopIcon,
} from '@heroicons/react/24/outline'

function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      const [summaryRes, datasetsRes] = await Promise.all([
        quickAPI.summary().catch(() => null),
        datasetAPI.history(),
      ])

      if (summaryRes?.data?.success) {
        setSummary(summaryRes.data.data)
      }

      if (datasetsRes?.data?.success) {
        setDatasets(datasetsRes.data.data)
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = async () => {
    try {
      const response = await quickAPI.report()
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ChemViz_Report_${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Report downloaded successfully')
    } catch (error) {
      toast.error('No data available for report generation')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-ash text-sm font-mono">Loading dashboard...</p>
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
            Analytics Dashboard
          </h1>
          <p className="text-slate">
            Precision analytics for chemical equipment parameters
          </p>
        </div>
        <div className="flex gap-3">
          <Link to="/upload" className="btn btn-primary flex items-center gap-2">
            <ArrowUpTrayIcon className="w-5 h-5" />
            Upload Dataset
          </Link>
          {summary && (
            <button
              onClick={downloadReport}
              className="btn btn-secondary flex items-center gap-2"
            >
              <DocumentArrowDownIcon className="w-5 h-5" />
              Download Report
            </button>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <QuickActionCard
          icon={ArrowUpTrayIcon}
          title="Upload Data"
          description="Import CSV datasets"
          link="/upload"
          color="blue"
        />
        <QuickActionCard
          icon={ChartBarIcon}
          title="View Analytics"
          description="Analyze equipment metrics"
          link="/analytics"
          color="green"
        />
        <QuickActionCard
          icon={ArrowDownTrayIcon}
          title="Desktop App"
          description="Download Windows application"
          link="https://github.com/ishansurdi/ChemViz/releases/latest/download/ChemViz-Desktop.exe"
          color="purple"
          external={true}
        />
        <QuickActionCard
          icon={ClockIcon}
          title="Dataset History"
          description="Browse past uploads"
          link="/history"
          color="purple"
        />
      </div>

      {/* Summary Statistics */}
      {summary && (
        <div className="card p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-charcoal font-heading">
              Latest Dataset Summary
            </h2>
            <span className="badge badge-success">
              {summary.dataset_info?.name || 'Latest'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              label="Total Equipment"
              value={summary.total_equipment}
              unit="items"
            />
            <StatCard
              label="Avg Flowrate"
              value={summary.avg_flowrate?.toFixed(2)}
              unit="L/min"
            />
            <StatCard
              label="Avg Pressure"
              value={summary.avg_pressure?.toFixed(2)}
              unit="Bar"
            />
            <StatCard
              label="Avg Temperature"
              value={summary.avg_temperature?.toFixed(2)}
              unit="°C"
            />
          </div>

          {/* Equipment Type Distribution */}
          {summary.equipment_type_distribution && summary.equipment_type_distribution.length > 0 && (
            <div className="mt-8">
              <h3 className="text-lg font-bold text-charcoal mb-4">Equipment Distribution</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {summary.equipment_type_distribution.slice(0, 6).map((dist, index) => (
                  <div key={index} className="p-4 bg-bg-base rounded-md">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-semibold text-charcoal truncate">
                        {dist.equipment_type}
                      </p>
                      <span className="badge badge-info">{dist.count}</span>
                    </div>
                    <div className="w-full bg-white rounded-full h-2 overflow-hidden">
                      <div
                        className="h-full bg-industrial-blue rounded-full"
                        style={{ width: `${dist.percentage}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-ash mt-1">{dist.percentage.toFixed(1)}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* No Data State */}
      {!summary && (
        <div className="card p-12 text-center">
          <div className="max-w-md mx-auto">
            <ChartBarIcon className="w-16 h-16 text-ash mx-auto mb-4" />
            <h3 className="text-xl font-bold text-charcoal mb-2">No Data Available</h3>
            <p className="text-slate mb-6">
              Upload your first dataset to start analyzing chemical equipment parameters.
            </p>
            <Link to="/upload" className="btn btn-primary inline-flex items-center gap-2">
              <ArrowUpTrayIcon className="w-5 h-5" />
              Upload Your First Dataset
            </Link>
          </div>
        </div>
      )}

      {/* Recent Datasets */}
      {datasets.length > 0 && (
        <div className="card p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-charcoal font-heading">Recent Datasets</h2>
            <Link to="/history" className="text-sm text-industrial-blue hover:underline">
              View all →
            </Link>
          </div>
          <div className="space-y-3">
            {datasets.slice(0, 5).map((dataset) => (
              <div
                key={dataset.id}
                className="flex items-center justify-between p-4 bg-bg-base rounded-md hover:bg-pale-steel transition-colors"
              >
                <div className="flex-1">
                  <p className="font-semibold text-charcoal">{dataset.name}</p>
                  <p className="text-xs text-ash">
                    {new Date(dataset.uploaded_at).toLocaleString()} • {dataset.total_equipment} equipment
                  </p>
                </div>
                <span
                  className={`badge ${
                    dataset.processing_status === 'completed'
                      ? 'badge-success'
                      : dataset.processing_status === 'failed'
                      ? 'badge-error'
                      : 'badge-warning'
                  }`}
                >
                  {dataset.processing_status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function QuickActionCard({ icon: Icon, title, description, link, onClick, color, external }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  }

  const content = (
    <>
      <div className={`w-12 h-12 rounded-md ${colorClasses[color]} flex items-center justify-center mb-4`}>
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-lg font-bold text-charcoal mb-1">{title}</h3>
      <p className="text-sm text-ash">{description}</p>
    </>
  )

  if (onClick) {
    return (
      <button onClick={onClick} className="card p-6 text-left hover:shadow-md transition-shadow">
        {content}
      </button>
    )
  }

  if (external) {
    return (
      <a 
        href={link} 
        className="card p-6 hover:shadow-md transition-shadow"
        download
        target="_blank"
        rel="noopener noreferrer"
      >
        {content}
      </a>
    )
  }

  return (
    <Link to={link} className="card p-6 hover:shadow-md transition-shadow">
      {content}
    </Link>
  )
}

function StatCard({ label, value, unit }) {
  return (
    <div className="text-center p-4 bg-bg-base rounded-md">
      <p className="text-sm text-ash uppercase tracking-wider mb-2 font-semibold">{label}</p>
      <div className="flex items-baseline justify-center gap-2">
        <span className="text-3xl font-bold text-charcoal font-heading">{value || '—'}</span>
        <span className="text-sm text-slate font-mono">{unit}</span>
      </div>
    </div>
  )
}

export default Dashboard
