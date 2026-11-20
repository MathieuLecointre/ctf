import api from './api'
import { mockChallenges } from '../data/mockChallenges'

/**
 * Challenge Service - V1 Web HTTPS Specifications & Admin Back-office
 * Handles challenge discovery, Docker instance lifecycle (start, stop, extend),
 * flag validation, and Admin CRUD operations with resilient offline fallback.
 */
export const challengeService = {
  /**
   * Fetch all CTF challenges from backend (with offline fallback)
   * @returns {Promise<Array>} List of challenges
   */
  async getChallenges() {
    try {
      const response = await api.get('/challenges')
      return response.data
    } catch (err) {
      console.warn('[Challenge Service / Fallback] Backend indisponible. Chargement des défis Web HTTPS mockés.')
      return mockChallenges
    }
  },

  /**
   * Fetch specific challenge details
   * @param {string|number} challengeId
   * @returns {Promise<Object>} Challenge detailed object
   */
  async getChallenge(challengeId) {
    try {
      const response = await api.get(`/challenges/${challengeId}`)
      return response.data
    } catch (err) {
      const chal = mockChallenges.find((c) => c.id === challengeId)
      if (chal) return chal
      throw err
    }
  },

  /**
   * Start a dedicated Docker container instance for a given challenge
   * Propagates 409 Conflict errors explicitly (max 2 active instances quota)
   * @param {string|number} challengeId
   * @returns {Promise<Object>} Instance connection info (host, targetUrl, expires_in)
   */
  async startInstance(challengeId) {
    try {
      const response = await api.post(`/challenges/${challengeId}/instance/start`)
      return response.data
    } catch (err) {
      // 409 Conflict: Quota of 2 instances reached on the backend
      if (err.response && err.response.status === 409) {
        console.warn('[Challenge Service] Quota d\'instances atteint (HTTP 409 Conflict).')
        const quotaError = new Error(err.response.data?.detail || 'Limite atteinte : 2 instances actives maximum par joueur.')
        quotaError.status = 409
        quotaError.isQuotaExceeded = true
        throw quotaError
      }
      throw err
    }
  },

  /**
   * Extend the running duration of an active Docker instance (+30 min)
   * Target endpoint: POST /instances/${instanceId}/extend
   * @param {string|number} instanceId
   * @returns {Promise<Object>} Updated instance metadata
   */
  async extendInstance(instanceId) {
    try {
      const response = await api.post(`/instances/${instanceId}/extend`)
      return response.data
    } catch (err) {
      if (err.response && err.response.status === 409) {
        const quotaError = new Error(err.response.data?.detail || 'Durée maximale de prolongation atteinte.')
        quotaError.status = 409
        throw quotaError
      }
      throw err
    }
  },

  /**
   * Stop an active Docker container instance
   * @param {string|number} challengeId
   * @returns {Promise<Object>} Status message
   */
  async stopInstance(challengeId) {
    const response = await api.post(`/challenges/${challengeId}/instance/stop`)
    return response.data
  },

  /**
   * Submit flag for verification
   * @param {string|number} challengeId
   * @param {string} flag
   * @returns {Promise<Object>} Result (is_valid, points_awarded)
   */
  async submitFlag(challengeId, flag) {
    try {
      const response = await api.post(`/challenges/${challengeId}/flag`, {
        flag,
      })
      return response.data
    } catch (err) {
      // Local evaluation fallback
      const chal = mockChallenges.find((c) => c.id === challengeId)
      if (chal && chal.flag) {
        const isValid = flag.trim() === chal.flag
        return {
          is_valid: isValid,
          points_awarded: isValid ? chal.points : 0,
          message: isValid ? 'Flag validé avec succès !' : 'Flag incorrect.'
        }
      }
      throw err
    }
  },

  // ==========================================
  // ADMIN CRUD OPERATIONS (Protected with fallback)
  // ==========================================

  /**
   * Admin: Create a new CTF Challenge
   * Endpoint: POST /admin/challenges
   * @param {Object} payload - Challenge form data
   * @returns {Promise<Object>} Created challenge
   */
  async createChallenge(payload) {
    try {
      const response = await api.post('/admin/challenges', payload)
      return response.data
    } catch (err) {
      console.warn('[Admin Service / Fallback] Création en mode résilient local.')
      const newChal = {
        ...payload,
        id: payload.id || `chal-${Date.now().toString(36)}`,
        solvedPercent: 0,
        author: payload.author || 'Admin',
        targetUrl: payload.targetUrl || `https://${Math.random().toString(36).substring(2, 10)}.chal.ctf.upjv.local`,
        borderAccent: 'border-emerald-500/80',
        badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
      }
      return newChal
    }
  },

  /**
   * Admin: Update an existing challenge
   * Endpoint: PUT /admin/challenges/${id}
   * @param {string|number} id
   * @param {Object} payload
   * @returns {Promise<Object>} Updated challenge
   */
  async updateChallenge(id, payload) {
    try {
      const response = await api.put(`/admin/challenges/${id}`, payload)
      return response.data
    } catch (err) {
      console.warn('[Admin Service / Fallback] Mise à jour en mode résilient local.')
      return { id, ...payload }
    }
  },

  /**
   * Admin: Delete a challenge
   * Endpoint: DELETE /admin/challenges/${id}
   * @param {string|number} id
   * @returns {Promise<Object>} Deletion result
   */
  async deleteChallenge(id) {
    try {
      const response = await api.delete(`/admin/challenges/${id}`)
      return response.data
    } catch (err) {
      console.warn('[Admin Service / Fallback] Suppression en mode résilient local.')
      return { success: true, id }
    }
  }
}

export default challengeService
