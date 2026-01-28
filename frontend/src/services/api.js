/**
 * API Service - Axios Configuration and API Calls
 * Handles all HTTP requests to Django backend
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refreshToken')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
            refresh: refreshToken,
          })

          const { access } = response.data
          localStorage.setItem('accessToken', access)

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: () => api.post('/auth/logout/'),
}

// Dataset API
export const datasetAPI = {
  list: () => api.get('/datasets/'),
  get: (id) => api.get(`/datasets/${id}/`),
  upload: (formData) => api.post('/datasets/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  history: () => api.get('/datasets/history/'),
  summary: (id) => api.get(`/datasets/${id}/summary/`),
  data: (id, params) => api.get(`/datasets/${id}/data/`, { params }),
  report: (id) => api.get(`/datasets/${id}/report/`, {
    responseType: 'blob',
  }),
}

// Quick access API (latest dataset)
export const quickAPI = {
  summary: () => api.get('/summary/'),
  data: (params) => api.get('/data/', { params }),
  report: () => api.get('/report/', {
    responseType: 'blob',
  }),
}

// Health check
export const healthAPI = {
  check: () => api.get('/health/'),
}

export default api
