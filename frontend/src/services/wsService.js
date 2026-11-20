/**
 * Native WebSocket Service for CTF UPJV
 * Connects to the FastAPI backend (ws://localhost:8000/ws) with automatic reconnection
 * and a resilient offline event simulator (fallback) emitting real-time updates every 8 seconds.
 */

class WebSocketService {
  constructor() {
    this.url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
    this.socket = null
    this.listeners = new Set()
    this.reconnectInterval = 5000
    this.reconnectTimer = null
    this.simulatorTimer = null
    this.isSimulating = false
    this.isConnected = false

    // Pool of mock data for offline simulation
    this.mockPlayers = [
      '0xDEADBEEF',
      'Ghost_Protocol',
      'CyberNinja',
      'System_Failure',
      'Null_Pointer',
      'SYN_Flood',
      'BufferBuster',
      'CryptoCat',
      'ShadowBroker',
      'darkhack3r'
    ]

    this.mockChallenges = [
      'SQL Injection — Blind',
      'XSS Stockée',
      'IDOR API Profil',
      'CSRF Email Takeover',
      'SSRF Intranet Recon',
      'JWT Auth Bypass',
      'Crypto Web (Padding Oracle)'
    ]

    this.connect()
  }

  /**
   * Connect to native WebSocket endpoint
   */
  connect() {
    try {
      this.socket = new WebSocket(this.url)

      this.socket.onopen = () => {
        console.info('[WebSocket / Native] Connecté au serveur temps réel FastAPI.')
        this.isConnected = true
        this.stopSimulator()
      }

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data)
          this.notifyListeners(payload)
        } catch (err) {
          console.warn('[WebSocket] Message JSON invalide reçu:', event.data)
        }
      }

      this.onerror = () => {
        // Handled silently before fallback
      }

      this.socket.onclose = () => {
        this.isConnected = false
        this.startSimulator()
        this.scheduleReconnect()
      }
    } catch (err) {
      this.isConnected = false
      this.startSimulator()
      this.scheduleReconnect()
    }
  }

  /**
   * Schedule reconnection attempt
   */
  scheduleReconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      if (!this.isConnected) {
        this.connect()
      }
    }, this.reconnectInterval)
  }

  /**
   * Offline Resilience Fallback Simulator:
   * Emits simulated SCORE_UPDATE and NOTIFICATION events every 8 seconds
   */
  startSimulator() {
    if (this.isSimulating) return
    this.isSimulating = true
    console.warn('[WebSocket / Fallback] Backend temps réel injoignable. Activation du simulateur d\'événements local (8s).')

    // Initial event after 2 seconds, then every 8 seconds
    this.simulatorTimer = setInterval(() => {
      this.generateMockEvent()
    }, 8000)
  }

  stopSimulator() {
    if (this.simulatorTimer) {
      clearInterval(this.simulatorTimer)
      this.simulatorTimer = null
    }
    this.isSimulating = false
  }

  /**
   * Generate realistic simulated events
   */
  generateMockEvent() {
    const isFirstBlood = Math.random() > 0.6
    const randomPlayer = this.mockPlayers[Math.floor(Math.random() * this.mockPlayers.length)]
    const randomChal = this.mockChallenges[Math.floor(Math.random() * this.mockChallenges.length)]
    const points = Math.floor(Math.random() * 3 + 1) * 25 // 25, 50, 75

    if (isFirstBlood) {
      // 1. Notification Event (First blood / Flag validation)
      const notifEvent = {
        type: 'NOTIFICATION',
        data: {
          id: Date.now(),
          category: 'FIRST_BLOOD',
          title: '🩸 FIRST BLOOD !',
          message: `${randomPlayer} vient de débloquer le premier sang sur "${randomChal}" (+${points + 50} pts) !`,
          player: randomPlayer,
          challenge: randomChal,
          timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        }
      }
      this.notifyListeners(notifEvent)

      // Also update score for this player
      const scoreEvent = {
        type: 'SCORE_UPDATE',
        data: {
          username: randomPlayer,
          pointsAdded: points + 50,
          challengeTitle: randomChal,
          timestamp: 'À l\'instant'
        }
      }
      this.notifyListeners(scoreEvent)
    } else {
      // 2. Standard Score Update Event
      const scoreEvent = {
        type: 'SCORE_UPDATE',
        data: {
          username: randomPlayer,
          pointsAdded: points,
          challengeTitle: randomChal,
          timestamp: 'À l\'instant'
        }
      }
      this.notifyListeners(scoreEvent)

      // Notification broadcast
      const notifEvent = {
        type: 'NOTIFICATION',
        data: {
          id: Date.now(),
          category: 'FLAG_SOLVED',
          title: 'FLAG VALIDÉ',
          message: `${randomPlayer} a résolu "${randomChal}" (+${points} pts).`,
          player: randomPlayer,
          challenge: randomChal,
          timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        }
      }
      this.notifyListeners(notifEvent)
    }
  }

  /**
   * Subscribe to incoming messages/events
   * @param {Function} callback - Function called with { type, data }
   * @returns {Function} Unsubscribe function
   */
  onMessage(callback) {
    this.listeners.add(callback)
    return () => {
      this.listeners.delete(callback)
    }
  }

  /**
   * Broadcast payload to all registered listeners
   */
  notifyListeners(payload) {
    for (const listener of this.listeners) {
      try {
        listener(payload)
      } catch (err) {
        console.error('[WebSocket] Erreur dans un écouteur:', err)
      }
    }
  }

  /**
   * Send JSON data to native WebSocket
   */
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(typeof data === 'string' ? data : JSON.stringify(data))
    } else {
      console.warn('[WebSocket] Impossible d\'envoyer le message, socket non connecté.')
    }
  }
}

// Export singleton instance
export const wsService = new WebSocketService()
export default wsService
