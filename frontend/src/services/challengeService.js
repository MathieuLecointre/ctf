import api from './api'
import { mockChallenges } from '../data/mockChallenges'

/**
 * Challenge Service - V1 Web HTTPS Specifications
 * Handles challenge discovery, Docker instance lifecycle (start, stop, extend),
 * and flag validation with resilient offline fallback support.
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
      // Propagate error if backend responded with specific status
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
}

export default challengeService
