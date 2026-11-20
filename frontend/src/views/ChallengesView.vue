<script setup>
import { ref, computed, onUnmounted } from 'vue'
import challengeService from '../services/challengeService'
import { mockChallenges } from '../data/mockChallenges'
import { useNotificationStore } from '../stores/notificationStore'

const notifStore = useNotificationStore()

// ==========================================
// 1. DATA: CHALLENGES CATALOG (100% Web HTTPS)
// ==========================================
const challenges = ref(mockChallenges)
const selectedChallenge = ref(challenges.value[0])
const selectedCategoryFilter = ref('ALL')
const flagInput = ref('')
const flagFeedback = ref({ message: '', type: '' })

const categoriesList = [
  { label: 'Tous', value: 'ALL' },
  { label: 'Injection', value: 'Web - Injection' },
  { label: 'Client-Side', value: 'Web - Client-Side' },
  { label: 'API & Auth', value: 'Web - API & Auth' },
  { label: 'Server-Side', value: 'Web - Server-Side' },
  { label: 'Crypto Web', value: 'Web - Cryptographie' }
]

const filteredChallenges = computed(() => {
  if (selectedCategoryFilter.value === 'ALL') {
    return challenges.value
  }
  return challenges.value.filter((c) => c.category === selectedCategoryFilter.value)
})

const selectChallenge = (chal) => {
  selectedChallenge.value = chal
  flagInput.value = ''
  flagFeedback.value = { message: '', type: '' }
}

// ==========================================
// 2. DOCKER INSTANCES MANAGEMENT & QUOTA (MAX 2)
// ==========================================
// Map: challengeId -> { remainingSeconds, timerInterval, targetUrl, isExtending }
const runningInstances = ref(new Map())
const loadingChallengeIds = ref(new Set())
const quotaAlertMessage = ref('')

const MAX_DURATION_SECONDS = 10800 // 3 hours ceiling (10800s)
const INITIAL_DURATION_SECONDS = 3600 // 60 minutes default

// Check current challenge instance status
const isCurrentRunning = computed(() => {
  return runningInstances.value.has(selectedChallenge.value.id)
})

const isCurrentLoading = computed(() => {
  return loadingChallengeIds.value.has(selectedChallenge.value.id)
})

const currentInstanceData = computed(() => {
  return runningInstances.value.get(selectedChallenge.value.id) || null
})

// Dynamic formatted countdown (HH:MM:SS)
const formattedCountdown = computed(() => {
  const total = currentInstanceData.value ? Math.max(0, currentInstanceData.value.remainingSeconds) : INITIAL_DURATION_SECONDS
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const seconds = total % 60
  return [
    hours.toString().padStart(2, '0'),
    minutes.toString().padStart(2, '0'),
    seconds.toString().padStart(2, '0')
  ].join(':')
})

const isMaxExtensionReached = computed(() => {
  if (!currentInstanceData.value) return false
  return currentInstanceData.value.remainingSeconds >= MAX_DURATION_SECONDS
})

// Format target HTTPS URL
const currentInstanceUrl = computed(() => {
  if (currentInstanceData.value && currentInstanceData.value.targetUrl) {
    return currentInstanceData.value.targetUrl
  }
  return selectedChallenge.value.targetUrl
})

/**
 * Start Docker Instance
 * Enforces strict quota of maximum 2 active instances per user
 */
const startInstance = async () => {
  const chalId = selectedChallenge.value.id
  if (isCurrentRunning.value || isCurrentLoading.value) return

  quotaAlertMessage.value = ''

  // QUOTA CHECK: Max 2 instances active simultaneously
  if (runningInstances.value.size >= 2) {
    const errorMsg = 'Limite atteinte : 2 instances actives maximum par joueur.'
    quotaAlertMessage.value = errorMsg

    // Red toast notification
    notifStore.addNotification({
      id: Date.now(),
      title: 'QUOTA DÉPASSÉ (409)',
      category: 'FIRST_BLOOD', // Red themed badge
      message: errorMsg,
      timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    })
    return
  }

  // Set loading state
  loadingChallengeIds.value.add(chalId)

  try {
    // Attempt real backend FastAPI call
    const res = await challengeService.startInstance(chalId)
    console.info('[Docker / API] Instance déployée avec succès:', res)

    createLocalInstance(chalId, res?.targetUrl || selectedChallenge.value.targetUrl)
  } catch (err) {
    // Handle 409 Conflict from backend
    if (err.isQuotaExceeded || err.status === 409) {
      const quotaMsg = err.message || 'Limite atteinte : 2 instances actives maximum par joueur.'
      quotaAlertMessage.value = quotaMsg

      notifStore.addNotification({
        id: Date.now(),
        title: 'QUOTA DÉPASSÉ (409)',
        category: 'FIRST_BLOOD',
        message: quotaMsg,
        timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      })
      loadingChallengeIds.value.delete(chalId)
      return
    }

    // Resilient Fallback: backend offline, simulate 3s loading then activate
    console.warn(`[Docker / Fallback] Backend indisponible (${err.message}). Déploiement en mode simulation locale.`)

    setTimeout(() => {
      createLocalInstance(chalId, selectedChallenge.value.targetUrl)
    }, 3000)
  }
}

function createLocalInstance(chalId, url) {
  loadingChallengeIds.value.delete(chalId)
  quotaAlertMessage.value = ''

  const instanceObj = {
    remainingSeconds: INITIAL_DURATION_SECONDS,
    targetUrl: url,
    timerInterval: null
  }

  // Start real-time countdown interval (ticks each second)
  instanceObj.timerInterval = setInterval(() => {
    if (instanceObj.remainingSeconds > 0) {
      instanceObj.remainingSeconds--
    } else {
      // Countdown expired: automatically teardown instance
      stopInstance(chalId)
      notifStore.addNotification({
        id: Date.now(),
        title: 'INSTANCE EXPIRÉE',
        category: 'FIRST_BLOOD',
        message: `L'instance pour "${selectedChallenge.value.title}" a expiré et a été arrêtée.`,
        timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      })
    }
  }, 1000)

  runningInstances.value.set(chalId, instanceObj)

  // Success Notification
  notifStore.addNotification({
    id: Date.now(),
    title: 'INSTANCE EN LIGNE',
    category: 'FLAG_SOLVED',
    message: `Environnement prêt : ${url}`,
    timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  })
}

/**
 * Stop Docker Instance
 */
const stopInstance = async (chalId = selectedChallenge.value.id) => {
  const instance = runningInstances.value.get(chalId)
  if (instance && instance.timerInterval) {
    clearInterval(instance.timerInterval)
  }
  runningInstances.value.delete(chalId)
  quotaAlertMessage.value = ''

  try {
    await challengeService.stopInstance(chalId)
  } catch (err) {
    // Silent offline catch
  }
}

/**
 * Extend Docker Instance (+30 min / 1800s)
 * Ceiling: 3 hours (10800s)
 */
const extendInstance = async () => {
  const chalId = selectedChallenge.value.id
  const instance = runningInstances.value.get(chalId)
  if (!instance) return

  if (instance.remainingSeconds >= MAX_DURATION_SECONDS) {
    notifStore.addNotification({
      id: Date.now(),
      title: 'PLAFOND ATTEINT',
      category: 'FIRST_BLOOD',
      message: 'Durée maximale atteinte (3 heures maximum par instance).',
      timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    })
    return
  }

  try {
    await challengeService.extendInstance(chalId)
  } catch (err) {
    // Fallback logic
    console.warn('[Docker / Extend Fallback] Prolongation en mode résilient.')
  }

  // Add 30 minutes (1800 seconds) capped at MAX_DURATION_SECONDS
  const newSeconds = Math.min(MAX_DURATION_SECONDS, instance.remainingSeconds + 1800)
  instance.remainingSeconds = newSeconds

  notifStore.addNotification({
    id: Date.now(),
    title: 'INSTANCE PROLONGÉE',
    category: 'FLAG_SOLVED',
    message: 'Environnement prolongé de +30 minutes.',
    timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  })
}

// ==========================================
// 3. FLAG VALIDATION
// ==========================================
const submitFlag = async () => {
  if (!flagInput.value.trim()) {
    flagFeedback.value = {
      message: 'Veuillez saisir un flag au format CTF{...}',
      type: 'warning'
    }
    return
  }

  try {
    const result = await challengeService.submitFlag(selectedChallenge.value.id, flagInput.value)
    if (result.is_valid) {
      flagFeedback.value = {
        message: `Bravo ! Flag valide (+${selectedChallenge.value.points} pts)`,
        type: 'success'
      }
      notifStore.addNotification({
        id: Date.now(),
        title: 'FLAG VALIDÉ !',
        category: 'FLAG_SOLVED',
        message: `Vous avez validé "${selectedChallenge.value.title}" (+${selectedChallenge.value.points} pts).`,
        timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      })
    } else {
      flagFeedback.value = {
        message: 'Flag incorrect. Analysez attentivement les indices et les requêtes HTTP.',
        type: 'error'
      }
    }
  } catch (err) {
    flagFeedback.value = {
      message: 'Erreur lors de la validation du flag.',
      type: 'error'
    }
  }
}

// Cleanup all active timers on unmount
onUnmounted(() => {
  for (const instance of runningInstances.value.values()) {
    if (instance.timerInterval) {
      clearInterval(instance.timerInterval)
    }
  }
})
</script>

<template>
  <div class="space-y-8 font-inter text-slate-100 py-2">
    <!-- Breadcrumb: 100% Web HTTPS Scope -->
    <nav class="flex items-center space-x-2 text-xs font-mono font-semibold uppercase tracking-wider text-[#7ec8ff]">
      <span class="text-slate-400">CATALOGUE</span>
      <span class="text-slate-600">&gt;</span>
      <span class="text-slate-400">{{ selectedChallenge.category.toUpperCase() }}</span>
      <span class="text-slate-600">&gt;</span>
      <span class="text-[#7ec8ff] font-bold">{{ selectedChallenge.title.toUpperCase() }}</span>
    </nav>

    <!-- Main 2-Columns Layout: Detail + Attack Environment -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- ========================================== -->
      <!-- LEFT COLUMN (8 cols): ACTIVE CHALLENGE CARD -->
      <!-- ========================================== -->
      <div class="lg:col-span-8 space-y-6">
        <!-- Main Challenge View Box -->
        <div class="relative bg-[#162545]/40 border border-[#333f59] rounded-lg p-6 sm:p-8 backdrop-blur-sm">
          <!-- Tech Brackets Accents -->
          <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
          <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
          <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
          <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

          <!-- Challenge Title -->
          <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white font-inter mb-4">
            {{ selectedChallenge.title }}
          </h1>

          <!-- Badges Bar -->
          <div class="flex flex-wrap items-center gap-3 font-mono text-xs mb-6">
            <!-- Category Badge -->
            <div class="px-3 py-1 rounded bg-[#162545] border border-[#333f59] text-slate-300 uppercase">
              CATÉGORIE : <span class="text-[#7ec8ff] font-bold">{{ selectedChallenge.category }}</span>
            </div>

            <!-- Difficulty Badge (Yellow Stars) -->
            <div class="px-3 py-1 rounded bg-[#162545] border border-[#ffcc00]/60 text-[#ffcc00] flex items-center gap-1.5 font-bold">
              <span>DIFFICULTÉ :</span>
              <span class="tracking-widest">
                <template v-for="star in 5" :key="star">
                  {{ star <= selectedChallenge.difficulty ? '★' : '☆' }}
                </template>
              </span>
            </div>

            <!-- Points Badge (Cyan) -->
            <div class="px-3 py-1 rounded bg-[#162545] border border-[#7ec8ff] text-[#7ec8ff] font-bold">
              {{ selectedChallenge.points }} PTS
            </div>

            <!-- Author Badge -->
            <div class="px-3 py-1 rounded bg-[#162545] border border-[#333f59] text-slate-400 uppercase">
              PAR : <span class="text-slate-200">{{ selectedChallenge.author }}</span>
            </div>
          </div>

          <!-- Challenge Technical Description (Zero Lorem Ipsum) -->
          <div class="text-slate-300 text-sm leading-relaxed whitespace-pre-line mb-8 font-inter border-t border-[#333f59]/40 pt-6">
            {{ selectedChallenge.description }}
          </div>

          <!-- Flag Submission Form -->
          <div class="space-y-3 border-t border-[#333f59]/60 pt-6">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 bg-[#ff3e3e]"></span>
              <label for="flag-input" class="text-xs font-bold text-slate-200 uppercase tracking-wider font-rajdhani">
                Soumettre le flag
              </label>
            </div>

            <div class="flex flex-col sm:flex-row gap-3">
              <input
                id="flag-input"
                v-model="flagInput"
                type="text"
                placeholder="CTF{votre_flag_ici}"
                class="flex-1 bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white placeholder-slate-500 font-mono text-sm px-4 py-2.5 rounded focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
                @keyup.enter="submitFlag"
              />
              <button
                type="button"
                class="bg-[#7ec8ff] hover:bg-white text-[#0a1a2f] font-rajdhani font-bold px-8 py-2.5 rounded text-sm tracking-wider uppercase transition-colors shadow cursor-pointer select-none"
                @click="submitFlag"
              >
                Valider
              </button>
            </div>

            <!-- Validation Feedback Alert -->
            <div
              v-if="flagFeedback.message"
              :class="[
                flagFeedback.type === 'success' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/40' :
                flagFeedback.type === 'error' ? 'text-[#ff3e3e] bg-[#ff3e3e]/10 border-[#ff3e3e]/40' :
                'text-amber-400 bg-amber-500/10 border-amber-500/40',
                'px-3 py-2 rounded border text-xs font-mono transition-all'
              ]"
            >
              {{ flagFeedback.message }}
            </div>
          </div>
        </div>

        <!-- ========================================== -->
        <!-- CATALOGUE LIST & FILTERING (100% Web HTTPS) -->
        <!-- ========================================== -->
        <div class="space-y-4 pt-4">
          <!-- Filters & Header Bar -->
          <div class="flex flex-wrap items-center justify-between gap-4 pb-2 border-b border-[#333f59]/60">
            <div class="flex items-center gap-3">
              <h2 class="text-xl font-black text-white font-inter tracking-tight">
                Catalogue Défis Web HTTPS
              </h2>
              <span class="text-xs font-mono text-slate-400 bg-[#162545] px-2 py-0.5 rounded border border-[#333f59]">
                {{ filteredChallenges.length }}
              </span>
            </div>

            <!-- Filter tabs -->
            <div class="flex flex-wrap items-center gap-1.5 font-rajdhani text-xs font-bold uppercase tracking-wider">
              <button
                v-for="cat in categoriesList"
                :key="cat.value"
                type="button"
                :class="[
                  selectedCategoryFilter === cat.value
                    ? 'bg-[#004e7a] text-white border-[#7ec8ff]'
                    : 'bg-[#162545]/70 text-slate-300 border-[#333f59] hover:bg-[#162545] hover:text-white',
                  'px-3 py-1 rounded border transition-colors cursor-pointer'
                ]"
                @click="selectedCategoryFilter = cat.value"
              >
                {{ cat.label }}
              </button>
            </div>
          </div>

          <!-- Challenges Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="chal in filteredChallenges"
              :key="chal.id"
              :class="[
                chal.id === selectedChallenge.id
                  ? 'ring-2 ring-[#7ec8ff] bg-[#162545]/90'
                  : 'bg-[#162545]/40 hover:bg-[#162545]/70',
                chal.borderAccent,
                'border rounded-lg p-4 transition-all duration-200 cursor-pointer flex flex-col justify-between group relative overflow-hidden'
              ]"
              @click="selectChallenge(chal)"
            >
              <!-- Running Badge if instance active -->
              <span
                v-if="runningInstances.has(chal.id)"
                class="absolute top-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/50 text-[10px] font-mono text-emerald-400 font-bold"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                ACTIVE
              </span>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[11px] font-mono font-semibold text-slate-400">
                    {{ chal.category }}
                  </span>
                  <span class="text-xs font-mono font-bold text-[#7ec8ff]">
                    {{ chal.points }} pts
                  </span>
                </div>

                <h3 class="text-sm font-bold text-white font-rajdhani group-hover:text-[#7ec8ff] transition-colors mb-2">
                  {{ chal.title }}
                </h3>

                <div class="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-3 font-inter">
                  {{ chal.description }}
                </div>
              </div>

              <!-- Card Footer: Stats & Author -->
              <div class="border-t border-[#333f59]/60 pt-2 flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>Par {{ chal.author }}</span>
                <span class="text-slate-300">{{ chal.solvedPercent }}% validé</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========================================== -->
      <!-- RIGHT COLUMN (4 cols): ATTACK ENVIRONMENT  -->
      <!-- ========================================== -->
      <div class="lg:col-span-4 lg:sticky lg:top-24 space-y-4">
        <!-- Quota Alert Box if triggered -->
        <div
          v-if="quotaAlertMessage"
          class="bg-[#ff3e3e]/15 border-2 border-[#ff3e3e] rounded-lg p-4 text-xs font-mono text-white flex items-start gap-3 shadow-lg shadow-[#ff3e3e]/10 animate-bounce"
        >
          <svg class="w-5 h-5 text-[#ff3e3e] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <div class="font-bold text-[#ff3e3e] uppercase font-rajdhani text-sm">Quota Dépassé (409)</div>
            <p class="text-slate-200 mt-1">{{ quotaAlertMessage }}</p>
          </div>
        </div>

        <div class="relative bg-[#162545]/50 border border-[#333f59] rounded-lg p-6 backdrop-blur-sm space-y-6">
          <!-- Tech Brackets Accents -->
          <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
          <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
          <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
          <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

          <!-- Panel Header with Active Instances Counter -->
          <div class="flex items-center justify-between border-b border-[#333f59]/60 pb-3">
            <h2 class="text-sm font-bold text-white uppercase tracking-wider font-rajdhani flex items-center gap-2">
              <span class="w-2 h-2 bg-[#7ec8ff]"></span>
              Environnement d'attaque
            </h2>
            <div class="flex items-center gap-2 font-mono text-[10px]">
              <span class="text-slate-400">QUOTA :</span>
              <span
                :class="[
                  runningInstances.size >= 2 ? 'text-[#ff3e3e] font-bold' : 'text-[#7ec8ff] font-bold',
                  'px-1.5 py-0.5 rounded bg-[#0a1a2f] border border-[#333f59]'
                ]"
              >
                {{ runningInstances.size }} / 2
              </span>
            </div>
          </div>

          <!-- Terminal Screen Container -->
          <div class="bg-[#050b14] border border-[#333f59]/80 rounded-md p-5 font-mono text-xs space-y-4 min-h-[220px] flex flex-col justify-center">
            <!-- ---------------------------------------- -->
            <!-- STATE 1: IDLE / REPOS                    -->
            <!-- ---------------------------------------- -->
            <div v-if="!isCurrentRunning && !isCurrentLoading" class="space-y-4 text-center py-2">
              <div class="w-12 h-12 mx-auto rounded-full bg-[#162545] border border-[#333f59] flex items-center justify-center text-slate-400">
                <svg class="w-6 h-6 text-[#7ec8ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div class="space-y-1">
                <div class="text-slate-200 font-semibold font-rajdhani text-sm uppercase tracking-wide">
                  Instance Prête au Déploiement
                </div>
                <div class="text-[11px] text-slate-400 leading-relaxed max-w-xs mx-auto">
                  Route HTTPS isolée via reverse proxy Traefik.<br />
                  <span class="text-slate-500">Durée standard : 60 minutes.</span>
                </div>
              </div>
            </div>

            <!-- ---------------------------------------- -->
            <!-- STATE 2: LOADING / CHARGEMENT (3s)       -->
            <!-- ---------------------------------------- -->
            <div v-else-if="isCurrentLoading" class="space-y-4 text-center py-4">
              <div class="flex justify-center">
                <!-- Tailwind Animated Spinner -->
                <svg
                  class="animate-spin h-9 w-9 text-[#7ec8ff]"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              </div>
              <div class="space-y-1">
                <div class="text-[#7ec8ff] font-bold font-rajdhani text-sm uppercase tracking-wider animate-pulse">
                  Initialisation du conteneur Web...
                </div>
                <div class="text-[10px] text-slate-400 font-mono">
                  Attribution du sous-domaine Traefik HTTPS
                </div>
              </div>
            </div>

            <!-- ---------------------------------------- -->
            <!-- STATE 3: RUNNING / ACTIF (HTTPS Clignotant & Cliquable) -->
            <!-- ---------------------------------------- -->
            <div v-else-if="isCurrentRunning" class="space-y-4">
              <!-- Online status badge -->
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2 text-emerald-400 font-bold tracking-wider">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>INSTANCE EN LIGNE</span>
                </div>
                <span class="text-[10px] font-mono text-[#7ec8ff] uppercase bg-[#004e7a]/40 px-2 py-0.5 rounded border border-[#7ec8ff]/40">
                  HTTPS / TLS
                </span>
              </div>

              <!-- Clickable Target URL (No Separate Port) -->
              <div class="space-y-1.5 pt-1">
                <div class="text-[10px] text-slate-400 uppercase tracking-wider flex items-center justify-between">
                  <span>URL CIBLE (CLIQUABLE) :</span>
                  <span class="text-[#7ec8ff] text-[10px]">TRAEFIK ROUTED</span>
                </div>
                <a
                  :href="currentInstanceUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center justify-between text-slate-100 font-mono text-xs break-all bg-[#0a1a2f] p-3 rounded-lg border border-[#333f59] hover:border-[#7ec8ff] text-[#7ec8ff] hover:text-white transition-all group cursor-pointer"
                  title="Ouvrir le défi dans un nouvel onglet"
                >
                  <span class="truncate font-semibold">{{ currentInstanceUrl }}</span>
                  <svg class="w-4 h-4 shrink-0 ml-2 text-slate-400 group-hover:text-[#7ec8ff] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          </div>

          <!-- Bottom Actions / Controls -->
          <div class="space-y-4">
            <!-- État 1 : Bouton "Démarrer l'instance" -->
            <button
              v-if="!isCurrentRunning && !isCurrentLoading"
              type="button"
              class="w-full bg-[#004e7a] hover:bg-[#004e7a]/80 text-white border border-[#7ec8ff]/60 hover:border-[#7ec8ff] font-rajdhani font-bold py-3 rounded text-sm tracking-wider uppercase transition-all shadow cursor-pointer flex items-center justify-center gap-2"
              @click="startInstance"
            >
              <svg class="w-4 h-4 text-[#7ec8ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Démarrer l'instance</span>
            </button>

            <!-- État 2 : Bouton désactivé avec Loader animé (3s) -->
            <button
              v-else-if="isCurrentLoading"
              type="button"
              disabled
              class="w-full bg-[#162545] border border-[#7ec8ff]/40 text-[#7ec8ff] font-rajdhani font-bold py-3 rounded text-sm tracking-wider uppercase flex items-center justify-center gap-3 cursor-not-allowed opacity-90"
            >
              <svg
                class="animate-spin h-4 w-4 text-[#7ec8ff]"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Déploiement HTTPS (3s)...</span>
            </button>

            <!-- État 3 : Vrai Compte à rebours dynamique + Boutons d'Action -->
            <div v-else-if="isCurrentRunning" class="space-y-4">
              <!-- Real-time Dynamic Countdown (starts at 01:00:00) -->
              <div class="text-center py-2 bg-[#0a1a2f]/70 border border-[#333f59] rounded-lg">
                <div class="text-[10px] font-mono uppercase text-slate-400 tracking-wider mb-0.5">
                  TEMPS RESTANT AVANT EXPIRATION
                </div>
                <div class="font-mono text-3xl sm:text-4xl font-extrabold text-[#ff3e3e] tracking-widest drop-shadow-sm select-none">
                  {{ formattedCountdown }}
                </div>
              </div>

              <!-- Action Controls: Prolonger (+30 min) & Arrêter -->
              <div class="grid grid-cols-2 gap-3 font-rajdhani font-bold text-xs uppercase tracking-wider">
                <!-- Extend Button (+30 min) -->
                <button
                  type="button"
                  :disabled="isMaxExtensionReached"
                  :class="[
                    isMaxExtensionReached
                      ? 'border-slate-600 text-slate-500 bg-[#0a1a2f] cursor-not-allowed'
                      : 'border-[#7ec8ff] bg-[#004e7a]/40 hover:bg-[#004e7a] text-[#7ec8ff] hover:text-white cursor-pointer shadow',
                    'py-2.5 px-2 rounded border transition-all text-center flex items-center justify-center gap-1.5'
                  ]"
                  :title="isMaxExtensionReached ? 'Plafond maximum atteint (3 heures max)' : 'Ajouter 30 minutes au compte à rebours'"
                  @click="extendInstance"
                >
                  <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>{{ isMaxExtensionReached ? 'Max (3h)' : '+30 min' }}</span>
                </button>

                <!-- Stop Instance Button -->
                <button
                  type="button"
                  class="border border-[#ff3e3e] bg-transparent hover:bg-[#ff3e3e]/20 text-[#ff3e3e] py-2.5 px-2 rounded transition-colors cursor-pointer text-center select-none"
                  @click="stopInstance(selectedChallenge.id)"
                >
                  Arrêter
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
