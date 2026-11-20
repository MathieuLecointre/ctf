import api from './api'

/**
 * Authentication Service
 * Manages identity, JWT tokens, and user session requests to the FastAPI backend
 */
export const authService = {
  /**
   * Log in user
   * @param {string} email
   * @param {string} password
   * @returns {Promise<Object>} API response data with access_token & user details
   */
  async login(email, password) {
    // FastAPI can accept either application/x-www-form-urlencoded or JSON
    // We send JSON payload conforming to standard auth contracts
    const response = await api.post('/auth/login', {
      email,
      password,
    })
    return response.data
  },

  /**
   * Register new user
   * @param {Object} userData
   * @returns {Promise<Object>} API response data
   */
  async register(userData) {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  /**
   * Fetch current authenticated user profile
   * @returns {Promise<Object>} User profile data
   */
  async getProfile() {
    const response = await api.get('/auth/me')
    return response.data
  },

  /**
   * Clear local session token
   */
  logout() {
    localStorage.removeItem('token')
  },
}

export default authService
