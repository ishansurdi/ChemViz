/**
 * Upload Page
 * CSV file upload with drag-and-drop support
 */

import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { datasetAPI } from '../services/api'
import toast from 'react-hot-toast'
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline'

function Upload() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [datasetName, setDatasetName] = useState('')
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => {
    setDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      setFile(droppedFile)
      if (!datasetName) {
        setDatasetName(droppedFile.name.replace('.csv', ''))
      }
    } else {
      toast.error('Please upload a CSV file')
    }
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      if (!datasetName) {
        setDatasetName(selectedFile.name.replace('.csv', ''))
      }
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()

    if (!file) {
      toast.error('Please select a file')
      return
    }

    if (!datasetName.trim()) {
      toast.error('Please enter a dataset name')
      return
    }

    setUploading(true)
    setUploadProgress('Uploading file...')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('name', datasetName.trim())

      setUploadProgress('Processing data...')
      const response = await datasetAPI.upload(formData)

      if (response.data.success) {
        toast.success('Dataset uploaded and processed successfully!')
        setUploadProgress('Upload complete!')
        
        setTimeout(() => {
          navigate('/analytics')
        }, 1500)
      } else {
        throw new Error(response.data.error?.message || 'Upload failed')
      }
    } catch (error) {
      console.error('Upload error:', error)
      const errorMessage =
        error.response?.data?.error?.message || error.message || 'Failed to upload dataset'
      toast.error(errorMessage)
      setUploadProgress(null)
    } finally {
      setUploading(false)
    }
  }

  const removeFile = () => {
    setFile(null)
    setUploadProgress(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-charcoal mb-2 font-heading">
          Upload Dataset
        </h1>
        <p className="text-slate">
          Import CSV files containing chemical equipment parameter data
        </p>
      </div>

      {/* Upload Form */}
      <form onSubmit={handleUpload} className="space-y-6">
        {/* Dataset Name */}
        <div className="card p-8">
          <label htmlFor="datasetName" className="label">
            Dataset Name <span className="text-red-500">*</span>
          </label>
          <input
            id="datasetName"
            type="text"
            value={datasetName}
            onChange={(e) => setDatasetName(e.target.value)}
            className="input"
            placeholder="Enter a descriptive name for this dataset"
            required
          />
          <p className="mt-2 text-sm text-ash">
            Give your dataset a meaningful name for easy identification
          </p>
        </div>

        {/* File Upload Area */}
        <div className="card p-8">
          <label className="label mb-4">
            CSV File <span className="text-red-500">*</span>
          </label>

          {!file ? (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`file-upload-area ${dragging ? 'drag-over' : ''}`}
            >
              <CloudArrowUpIcon className="w-16 h-16 text-ash mx-auto mb-4" />
              <p className="text-lg font-semibold text-charcoal mb-2">
                Drop your CSV file here or click to browse
              </p>
              <p className="text-sm text-ash mb-4">
                Maximum file size: 10MB
              </p>
              <button type="button" className="btn btn-secondary !text-xs">
                Select File
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
          ) : (
            <div className="border border-border rounded-lg p-6 bg-bg-base">
              <div className="flex items-start gap-4">
                <DocumentTextIcon className="w-12 h-12 text-industrial-blue flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-charcoal truncate">{file.name}</p>
                  <p className="text-sm text-ash">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                  {uploadProgress && (
                    <div className="mt-3">
                      <p className="text-sm text-industrial-blue mb-2">{uploadProgress}</p>
                      <div className="w-full bg-white rounded-full h-2 overflow-hidden">
                        <div className="h-full bg-industrial-blue animate-pulse"></div>
                      </div>
                    </div>
                  )}
                </div>
                {!uploading && (
                  <button
                    type="button"
                    onClick={removeFile}
                    className="p-2 hover:bg-red-50 rounded-md transition-colors"
                  >
                    <XCircleIcon className="w-6 h-6 text-red-500" />
                  </button>
                )}
              </div>
            </div>
          )}

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm font-semibold text-blue-800 mb-2">Required CSV Format:</p>
            <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
              <li>Equipment Name - Name of the equipment</li>
              <li>Type - Equipment type (e.g., Chemical Reactor, Heat Exchanger)</li>
              <li>Flowrate - Flow rate value (numeric)</li>
              <li>Pressure - Pressure value (numeric)</li>
              <li>Temperature - Temperature value (numeric)</li>
            </ul>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="btn btn-secondary"
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!file || uploading || !datasetName.trim()}
            className="btn btn-primary flex items-center gap-2"
          >
            {uploading ? (
              <>
                <div className="spinner !w-5 !h-5 !border-2"></div>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <CloudArrowUpIcon className="w-5 h-5" />
                <span>Upload & Process</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Instructions */}
      <div className="card p-8">
        <h2 className="text-xl font-bold text-charcoal mb-4 font-heading">
          Upload Instructions
        </h2>
        <div className="space-y-4 text-sm text-slate">
          <div className="flex gap-3">
            <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-charcoal">Prepare Your CSV File</p>
              <p>Ensure your CSV file contains the required columns with proper headers</p>
            </div>
          </div>
          <div className="flex gap-3">
            <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-charcoal">Upload the File</p>
              <p>Drag and drop your CSV file or click to browse and select it</p>
            </div>
          </div>
          <div className="flex gap-3">
            <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-charcoal">Automatic Processing</p>
              <p>
                The system will automatically parse, validate, and analyze your data,
                generating summary statistics and visualizations
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-charcoal">View Results</p>
              <p>
                Once processed, you can view analytics, generate reports, and explore
                the equipment data
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Upload
