import axios from 'axios'

/**
 * Base Axios instance configured for CTF UPJV Backend (FastAPI)
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

/**
 * Request Interceptor:
 * Injects JWT Bearer Token into headers if present in localStorage
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response Interceptor:
 * Global handler for HTTP 401 (Unauthorized), 403 (Forbidden), and Network Errors
 */
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      const { status } = error.response

      if (status === 401) {
        console.warn('[Security / Auth] Session expirée ou non autorisée (401). Nettoyage du token.')
        localStorage.removeItem('token')
      } else if (status === 403) {
        console.warn('[Security / Auth] Accès interdit (403). Droits insuffisants pour cette ressource.')
      }
    } else if (error.request) {
      console.warn('[Network Error] Aucune réponse reçue du serveur backend (serveur indisponible ou hors-ligne).')
    }

    return Promise.reject(error)
  }
)

export default api
