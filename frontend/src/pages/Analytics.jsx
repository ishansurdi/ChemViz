/**
 * Analytics Page
 * Data visualizations using Chart.js
 */

import { useState, useEffect } from 'react'
import { quickAPI, datasetAPI } from '../services/api'
import toast from 'react-hot-toast'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Line, Pie } from 'react-chartjs-2'
import { DocumentArrowDownIcon } from '@heroicons/react/24/outline'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

function Analytics() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    setLoading(true)
    try {
      const response = await quickAPI.summary()
      if (response.data.success) {
        setSummary(response.data.data)
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
      toast.error('Failed to load analytics data')
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
      toast.error('Failed to generate report')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-ash text-sm font-mono">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (!summary) {
    return (
      <div className="card p-12 text-center">
        <h2 className="text-2xl font-bold text-charcoal mb-4">No Data Available</h2>
        <p className="text-slate mb-6">
          Please upload a dataset first to view analytics
        </p>
      </div>
    )
  }

  // Prepare chart data
  const distributionData = summary.equipment_type_distribution || []
  
  // Bar chart for equipment type distribution
  const barChartData = {
    labels: distributionData.map((d) => d.equipment_type),
    datasets: [
      {
        label: 'Equipment Count',
        data: distributionData.map((d) => d.count),
        backgroundColor: '#365F8B',
        borderColor: '#2F5278',
        borderWidth: 1,
      },
    ],
  }

  // Line chart for average parameters per type
  const lineChartData = {
    labels: distributionData.map((d) => d.equipment_type),
    datasets: [
      {
        label: 'Avg Flowrate (L/min)',
        data: distributionData.map((d) => d.avg_flowrate),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Avg Pressure (Bar)',
        data: distributionData.map((d) => d.avg_pressure),
        borderColor: '#F59E0B',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Avg Temperature (°C)',
        data: distributionData.map((d) => d.avg_temperature),
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
    ],
  }

  // Pie chart for equipment distribution percentages
  const pieChartData = {
    labels: distributionData.map((d) => d.equipment_type),
    datasets: [
      {
        data: distributionData.map((d) => d.percentage),
        backgroundColor: [
          '#365F8B',
          '#10B981',
          '#F59E0B',
          '#EF4444',
          '#8B5CF6',
          '#EC4899',
          '#06B6D4',
          '#84CC16',
        ],
        borderColor: '#FFFFFF',
        borderWidth: 2,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            family: 'Inter',
            size: 11,
          },
          color: '#4B5563',
        },
      },
      title: {
        display: false,
      },
    },
    scales: {
      x: {
        ticks: {
          font: {
            family: 'Inter',
            size: 10,
          },
          color: '#6B7280',
        },
        grid: {
          color: '#F7F8FA',
        },
      },
      y: {
        ticks: {
          font: {
            family: 'Inter',
            size: 10,
          },
          color: '#6B7280',
        },
        grid: {
          color: '#F7F8FA',
        },
      },
    },
  }

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          font: {
            family: 'Inter',
            size: 11,
          },
          color: '#4B5563',
          padding: 12,
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.label}: ${context.parsed.toFixed(1)}%`
          },
        },
      },
    },
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-charcoal mb-2 font-heading">
            Analytics & Visualizations
          </h1>
          <p className="text-slate">
            Dataset: <span className="font-semibold">{summary.dataset_info?.name}</span>
          </p>
        </div>
        <button
          onClick={downloadReport}
          className="btn btn-primary flex items-center gap-2"
        >
          <DocumentArrowDownIcon className="w-5 h-5" />
          Download Report
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          label="Total Equipment"
          value={summary.total_equipment}
          unit="items"
          color="blue"
        />
        <StatCard
          label="Avg Flowrate"
          value={summary.avg_flowrate?.toFixed(2)}
          unit="L/min"
          color="green"
        />
        <StatCard
          label="Avg Pressure"
          value={summary.avg_pressure?.toFixed(2)}
          unit="Bar"
          color="orange"
        />
        <StatCard
          label="Avg Temperature"
          value={summary.avg_temperature?.toFixed(2)}
          unit="°C"
          color="red"
        />
      </div>

      {/* Equipment Distribution Bar Chart */}
      <div className="card p-8">
        <h2 className="text-xl font-bold text-charcoal mb-6 font-heading">
          Equipment Type Distribution
        </h2>
        <div className="h-80">
          <Bar data={barChartData} options={chartOptions} />
        </div>
      </div>

      {/* Parameter Comparison Line Chart */}
      <div className="card p-8">
        <h2 className="text-xl font-bold text-charcoal mb-6 font-heading">
          Average Parameters by Equipment Type
        </h2>
        <div className="h-80">
          <Line data={lineChartData} options={chartOptions} />
        </div>
      </div>

      {/* Two Column Layout for Pie Chart and Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <div className="card p-8">
          <h2 className="text-xl font-bold text-charcoal mb-6 font-heading">
            Distribution Percentage
          </h2>
          <div className="h-80">
            <Pie data={pieChartData} options={pieOptions} />
          </div>
        </div>

        {/* Distribution Table */}
        <div className="card p-8">
          <h2 className="text-xl font-bold text-charcoal mb-6 font-heading">
            Detailed Statistics
          </h2>
          <div className="overflow-auto max-h-80">
            <table className="table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th className="text-center">Count</th>
                  <th className="text-center">%</th>
                </tr>
              </thead>
              <tbody>
                {distributionData.map((dist, index) => (
                  <tr key={index}>
                    <td className="font-semibold">{dist.equipment_type}</td>
                    <td className="text-center">{dist.count}</td>
                    <td className="text-center">{dist.percentage.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, unit, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    orange: 'bg-orange-50 border-orange-200',
    red: 'bg-red-50 border-red-200',
  }

  return (
    <div className={`card p-6 ${colorClasses[color]}`}>
      <p className="text-sm text-ash uppercase tracking-wider mb-2 font-semibold">{label}</p>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-charcoal font-heading">{value || '—'}</span>
        <span className="text-sm text-slate font-mono">{unit}</span>
      </div>
    </div>
  )
}

export default Analytics
