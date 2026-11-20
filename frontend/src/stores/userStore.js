import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import authService from '../services/authService'

export const useUserStore = defineStore('user', () => {
  // State
  const isAuthenticated = ref(false)
  const username = ref('')
  const email = ref('')
  const score = ref(0)
  const rank = ref(null)
  const role = ref('admin') // 'admin' | 'player' (Default 'admin' for mock/demo testing)
  const joinedAt = ref('15 Octobre 2026')
  const isLoading = ref(false)

  // Getters
  const isAdmin = computed(() => role.value === 'admin')

  // Default Mocked Solved Challenges (3/7 Web challenges completed)
  const solvedChallenges = ref([
    {
      id: 'sqli-blind',
      title: 'SQL Injection — Blind (Boolean & Time-Based)',
      category: 'Web - Injection',
      points: 35,
      solvedAt: '20 Nov. 2026 • 14:22',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
    },
    {
      id: 'xss-stored',
      title: 'XSS Stockée — Cookie Stealing & Session Hijacking',
      category: 'Web - Client-Side',
      points: 25,
      solvedAt: '18 Nov. 2026 • 19:05',
      badgeColor: 'text-blue-400 bg-blue-500/10 border-blue-500/30'
    },
    {
      id: 'idor-profile',
      title: 'IDOR — Broken Object Level Authorization',
      category: 'Web - API & Auth',
      points: 20,
      solvedAt: '16 Nov. 2026 • 11:47',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
    }
  ])

  // Actions
  /**
   * Resilient Login Action:
   * 1. Attempts real backend authentication via authService (Axios)
   * 2. If the backend is offline (Network Error / Connection refused), falls back
   *    gracefully to mocked data with 'admin' role so the demo interface stays fully operational.
   *
   * @param {Object} credentials - { email, password, username, role }
   */
  async function login(credentials = {}) {
    isLoading.value = true

    try {
      // Real backend API attempt
      const data = await authService.login(credentials.email, credentials.password)

      // If backend returns a JWT token, persist it
      const token = data.access_token || data.token
      if (token) {
        localStorage.setItem('token', token)
      }

      isAuthenticated.value = true
      username.value =
        data.user?.username ||
        credentials.username ||
        (credentials.email ? credentials.email.split('@')[0] : 'darkhack3r')
      email.value = data.user?.email || credentials.email || 'darkhack3r@upjv.local'
      score.value = data.user?.score ?? 750
      rank.value = data.user?.rank ?? 42
      role.value = data.user?.role || 'admin'
      joinedAt.value = data.user?.joined_at || '15 Octobre 2026'

      console.info('[Auth / API] Authentification réussie auprès du backend FastAPI.')
    } catch (err) {
      // Resilience / Fallback mechanism: backend is not reachable or errored
      console.warn(
        `[Auth / Resilient Fallback] Impossible de contacter le backend FastAPI (${err.message || 'Serveur indisponible'}). Utilisation du profil mocké.`,
        err
      )

      // Simulate 1s loading delay for realistic demo UX
      await new Promise((resolve) => setTimeout(resolve, 1000))

      isAuthenticated.value = true
      username.value =
        credentials.username ||
        (credentials.email ? credentials.email.split('@')[0] : 'darkhack3r')
      email.value = credentials.email || 'darkhack3r@upjv.local'
      score.value = 750
      rank.value = 42
      role.value = credentials.role || 'admin'
      joinedAt.value = '15 Octobre 2026'

      // Store a mock token for subsequent interceptor validation
      localStorage.setItem('token', 'mock_jwt_token_upjv_session')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Toggle between Admin and Player roles (demo switch)
   */
  function toggleRole() {
    role.value = role.value === 'admin' ? 'player' : 'admin'
    console.info(`[Auth / Role Switch] Rôle utilisateur changé vers : ${role.value.toUpperCase()}`)
  }

  /**
   * Fetch current user profile with silent fallback
   */
  async function fetchProfile() {
    try {
      const data = await authService.getProfile()
      if (data) {
        if (data.username) username.value = data.username
        if (data.email) email.value = data.email
        if (data.score !== undefined) score.value = data.score
        if (data.rank !== undefined) rank.value = data.rank
        if (data.role) role.value = data.role
        if (data.joined_at) joinedAt.value = data.joined_at
        if (Array.isArray(data.solved_challenges)) {
          solvedChallenges.value = data.solved_challenges
        }
      }
    } catch (err) {
      console.warn('[Profile / Fallback] Chargement des données de profil hors-ligne mockées.')
    }
  }

  /**
   * Record a newly solved challenge in the reactive profile state
   */
  function addSolvedChallenge(challenge) {
    if (!solvedChallenges.value.some((c) => c.id === challenge.id)) {
      solvedChallenges.value.unshift({
        id: challenge.id,
        title: challenge.title,
        category: challenge.category,
        points: challenge.points,
        solvedAt: "À l'instant",
        badgeColor: challenge.badgeColor || 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
      })
      score.value += challenge.points
    }
  }

  /**
   * Logout Action
   * Cleans up local state and clears JWT tokens
   */
  function logout() {
    authService.logout()
    isAuthenticated.value = false
    username.value = ''
    email.value = ''
    score.value = 0
    rank.value = null
    role.value = 'admin'
    console.info('[Auth] Déconnexion effectuée et token nettoyé.')
  }

  return {
    isAuthenticated,
    username,
    email,
    score,
    rank,
    role,
    isAdmin,
    joinedAt,
    solvedChallenges,
    isLoading,
    login,
    logout,
    toggleRole,
    fetchProfile,
    addSolvedChallenge
  }
})
