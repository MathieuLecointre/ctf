<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../stores/userStore'
import wsService from '../services/wsService'

const userStore = useUserStore()

// 15 Mocked Players
const players = ref([
  { rank: 1, username: '0xDEADBEEF', solved: 48, total: 50, score: 9850, lastActivity: 'Il y a 3 min', isTop: true, badge: 'GrandMaster' },
  { rank: 2, username: 'Ghost_Protocol', solved: 45, total: 50, score: 9120, lastActivity: 'Il y a 14 min', isTop: true, badge: 'KernelDev' },
  { rank: 3, username: 'CyberNinja', solved: 43, total: 50, score: 8650, lastActivity: 'Il y a 32 min', isTop: true, badge: 'WebExploit' },
  { rank: 4, username: 'System_Failure', solved: 39, total: 50, score: 7800, lastActivity: 'Il y a 1h', isTop: false, badge: 'ReverseEng' },
  { rank: 5, username: 'Null_Pointer', solved: 38, total: 50, score: 7550, lastActivity: 'Il y a 2h', isTop: false, badge: 'Forensics' },
  { rank: 6, username: 'SYN_Flood', solved: 35, total: 50, score: 6900, lastActivity: 'Il y a 3h', isTop: false, badge: 'NetSec' },
  { rank: 7, username: 'BufferBuster', solved: 34, total: 50, score: 6650, lastActivity: 'Il y a 5h', isTop: false, badge: 'Pwn' },
  { rank: 8, username: 'CryptoCat', solved: 31, total: 50, score: 6100, lastActivity: 'Il y a 6h', isTop: false, badge: 'Crypto' },
  { rank: 9, username: 'ShadowBroker', solved: 29, total: 50, score: 5750, lastActivity: 'Il y a 9h', isTop: false, badge: 'RedTeam' },
  { rank: 10, username: 'PacketStorm', solved: 28, total: 50, score: 5400, lastActivity: 'Hier', isTop: false, badge: 'BlueTeam' },
  { rank: 11, username: 'ZeroDayHunter', solved: 27, total: 50, score: 5150, lastActivity: 'Hier', isTop: false, badge: 'AppSec' },
  { rank: 12, username: 'RootAccess', solved: 25, total: 50, score: 4800, lastActivity: 'Il y a 2 jours', isTop: false, badge: 'SysAdmin' },
  { rank: 13, username: 'MalwareDoctor', solved: 24, total: 50, score: 4500, lastActivity: 'Il y a 2 jours', isTop: false, badge: 'Malware' },
  { rank: 14, username: 'XSS_Lord', solved: 22, total: 50, score: 4100, lastActivity: 'Il y a 3 jours', isTop: false, badge: 'BugHunter' },
  { rank: 15, username: 'GDB_Wizard', solved: 21, total: 50, score: 3950, lastActivity: 'Il y a 3 jours', isTop: false, badge: 'Assembly' },
])

const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const recentlyUpdatedUsername = ref(null)
const lastLiveEvent = ref(null)

let unsubscribeWs = null

// WebSocket Real-time Scoreboard Synchronization
onMounted(() => {
  unsubscribeWs = wsService.onMessage((event) => {
    if (event.type === 'SCORE_UPDATE' && event.data) {
      handleRealtimeScore(event.data)
    }
  })
})

onUnmounted(() => {
  if (unsubscribeWs) {
    unsubscribeWs()
  }
})

function handleRealtimeScore(data) {
  const targetPlayer = players.value.find((p) => p.username === data.username)

  if (targetPlayer) {
    targetPlayer.score += data.pointsAdded
    targetPlayer.solved = Math.min(targetPlayer.total, targetPlayer.solved + 1)
    targetPlayer.lastActivity = 'À l\'instant'
  } else {
    // If player wasn't in top 15, add dynamically
    players.value.push({
      rank: players.value.length + 1,
      username: data.username,
      solved: 1,
      total: 50,
      score: data.pointsAdded,
      lastActivity: 'À l\'instant',
      isTop: false,
      badge: 'Challenger'
    })
  }

  // Live Re-sorting by score
  players.value.sort((a, b) => b.score - a.score)

  // Re-index ranks
  players.value.forEach((p, index) => {
    p.rank = index + 1
    p.isTop = p.rank <= 3
  })

  // Visual highlights on row
  recentlyUpdatedUsername.value = data.username
  lastLiveEvent.value = {
    username: data.username,
    pointsAdded: data.pointsAdded,
    challengeTitle: data.challengeTitle,
    time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  setTimeout(() => {
    if (recentlyUpdatedUsername.value === data.username) {
      recentlyUpdatedUsername.value = null
    }
  }, 3500)
}

// Filter by search query
const filteredPlayers = computed(() => {
  if (!searchQuery.value.trim()) return players.value
  const q = searchQuery.value.toLowerCase()
  return players.value.filter((p) => p.username.toLowerCase().includes(q))
})

// Paginated players
const totalPages = computed(() => Math.ceil(filteredPlayers.value.length / itemsPerPage) || 1)

const paginatedPlayers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredPlayers.value.slice(start, start + itemsPerPage)
})

const getRankDisplay = (rank) => {
  return rank < 10 ? `0${rank}` : `${rank}`
}
</script>

<template>
  <div class="space-y-8 py-4 font-inter text-slate-100">
    <!-- Breadcrumb, Title & Live Status Indicator -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div class="space-y-1">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 bg-[#ff3e3e]"></span>
          <span class="text-xs font-bold text-[#ff3e3e] uppercase tracking-wider font-rajdhani">
            Communauté &amp; Compétition
          </span>
          <span class="mx-1 text-slate-600">•</span>
          <!-- WebSocket Live Pill -->
          <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/40 text-[10px] font-mono font-bold text-emerald-400">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            WEBSOCKET TEMPS RÉEL (8s)
          </span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-black uppercase tracking-tight text-white font-inter">
          Leaderboard Général
        </h1>
        <p class="text-xs text-slate-400 font-mono">
          Mise à jour en direct via WebSockets standards
        </p>
      </div>

      <!-- Quick Stats Pods -->
      <div class="flex items-center gap-4 font-rajdhani">
        <div class="bg-[#162545]/60 border border-[#333f59] rounded-lg px-4 py-2">
          <div class="text-[11px] text-slate-400 font-semibold uppercase">Participants</div>
          <div class="text-lg font-bold text-white font-mono">1 284</div>
        </div>
        <div class="bg-[#162545]/60 border border-[#333f59] rounded-lg px-4 py-2">
          <div class="text-[11px] text-slate-400 font-semibold uppercase">Top Score</div>
          <div class="text-lg font-bold text-[#ffcc00] font-mono">
            {{ players[0]?.score.toLocaleString('fr-FR') }} pts
          </div>
        </div>
      </div>
    </div>

    <!-- Live Event Ticker (when a WebSocket event arrives) -->
    <div
      v-if="lastLiveEvent"
      class="bg-[#162545]/80 border border-[#7ec8ff]/60 rounded-lg p-3 flex items-center justify-between text-xs font-mono shadow-lg transition-all animate-fadeIn"
    >
      <div class="flex items-center gap-3">
        <span class="px-2 py-0.5 rounded bg-[#7ec8ff]/20 text-[#7ec8ff] font-bold text-[10px] uppercase">
          LIVE FEED
        </span>
        <span class="text-white">
          <strong class="text-[#7ec8ff]">{{ lastLiveEvent.username }}</strong> vient de marquer
          <strong class="text-[#ffcc00]">+{{ lastLiveEvent.pointsAdded }} pts</strong> sur
          <em>{{ lastLiveEvent.challengeTitle }}</em>
        </span>
      </div>
      <span class="text-slate-400 text-[10px] hidden sm:inline">{{ lastLiveEvent.time }}</span>
    </div>

    <!-- Active User Sticky Banner if Authenticated -->
    <div
      v-if="userStore.isAuthenticated"
      class="bg-gradient-to-r from-[#004e7a]/40 via-[#162545] to-[#ff3e3e]/20 border border-[#7ec8ff]/40 rounded-lg p-4 flex items-center justify-between shadow-lg"
    >
      <div class="flex items-center gap-4">
        <div class="w-10 h-10 rounded-lg bg-[#004e7a] border border-[#7ec8ff] flex items-center justify-center font-mono font-bold text-sm text-[#7ec8ff]">
          #{{ userStore.rank || 42 }}
        </div>
        <div>
          <div class="text-xs font-mono text-[#7ec8ff] uppercase font-semibold">Votre Position</div>
          <div class="text-sm font-bold text-white font-mono flex items-center gap-2">
            <span>{{ userStore.username }}</span>
            <span class="px-2 py-0.5 rounded bg-[#ff3e3e]/20 text-[#ff3e3e] text-[10px] font-mono">VOUS</span>
          </div>
        </div>
      </div>
      <div class="text-right font-mono">
        <div class="text-xs text-slate-400">Score Personnel</div>
        <div class="text-lg font-bold text-[#ffcc00]">{{ userStore.score }} pts</div>
      </div>
    </div>

    <!-- Leaderboard Table Container -->
    <div class="relative bg-[#162545]/40 border border-[#333f59] rounded-lg p-6 backdrop-blur-sm space-y-6">
      <!-- Tech Corner Brackets -->
      <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
      <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
      <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
      <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

      <!-- Controls: Search & Tabs -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pb-4 border-b border-[#333f59]/60">
        <!-- Search filter -->
        <div class="relative w-full sm:w-72">
          <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 pointer-events-none">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Filtrer par pseudo..."
            class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white placeholder-slate-500 rounded-lg pl-9 pr-3 py-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
          />
        </div>

        <!-- Counter info -->
        <div class="text-xs font-mono text-slate-400">
          Affichage de <span class="text-white font-bold">{{ paginatedPlayers.length }}</span> sur <span class="text-white font-bold">{{ filteredPlayers.length }}</span> hackers
        </div>
      </div>

      <!-- Table Structure -->
      <div class="overflow-x-auto">
        <table class="w-full text-left font-rajdhani border-collapse">
          <thead>
            <tr class="border-b border-[#333f59] text-xs font-bold uppercase tracking-wider text-slate-400">
              <th class="py-3 px-4 w-16 text-center">Rang</th>
              <th class="py-3 px-4">Hackeur</th>
              <th class="py-3 px-4 hidden md:table-cell">Spécialité</th>
              <th class="py-3 px-4 text-center">Défis Résolus</th>
              <th class="py-3 px-4 hidden lg:table-cell">Dernier Flag</th>
              <th class="py-3 px-4 text-right">Score Total</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#333f59]/40 text-sm">
            <tr
              v-for="player in paginatedPlayers"
              :key="player.username"
              :class="[
                recentlyUpdatedUsername === player.username
                  ? 'bg-[#004e7a]/50 ring-2 ring-[#7ec8ff] shadow-lg shadow-[#7ec8ff]/20 animate-pulse transition-all duration-300'
                  : userStore.isAuthenticated && userStore.username === player.username
                    ? 'bg-[#004e7a]/20 border border-[#7ec8ff]/40'
                    : 'hover:bg-[#162545]/80 transition-colors',
              ]"
            >
              <!-- Rank -->
              <td class="py-3.5 px-4 text-center font-mono font-black">
                <span
                  v-if="player.rank === 1"
                  class="inline-flex items-center justify-center w-7 h-7 rounded bg-[#ffcc00]/20 text-[#ffcc00] border border-[#ffcc00]/50"
                  title="1ère place (Or)"
                >
                  🥇
                </span>
                <span
                  v-else-if="player.rank === 2"
                  class="inline-flex items-center justify-center w-7 h-7 rounded bg-slate-400/20 text-slate-200 border border-slate-400/50"
                  title="2ème place (Argent)"
                >
                  🥈
                </span>
                <span
                  v-else-if="player.rank === 3"
                  class="inline-flex items-center justify-center w-7 h-7 rounded bg-amber-700/20 text-amber-500 border border-amber-600/50"
                  title="3ème place (Bronze)"
                >
                  🥉
                </span>
                <span v-else class="text-slate-400">
                  {{ getRankDisplay(player.rank) }}
                </span>
              </td>

              <!-- Username & Badge -->
              <td class="py-3.5 px-4 font-bold text-white">
                <div class="flex items-center gap-2">
                  <span class="font-mono">{{ player.username }}</span>
                  <span
                    v-if="userStore.isAuthenticated && userStore.username === player.username"
                    class="px-2 py-0.5 rounded bg-[#ff3e3e]/20 text-[#ff3e3e] text-[10px] font-mono uppercase"
                  >
                    Vous
                  </span>
                  <!-- Realtime update tag indicator -->
                  <span
                    v-if="recentlyUpdatedUsername === player.username"
                    class="px-2 py-0.5 rounded bg-[#7ec8ff]/30 text-[#7ec8ff] text-[10px] font-mono font-bold animate-bounce"
                  >
                    +SCORE
                  </span>
                </div>
              </td>

              <!-- Badge / Speciality -->
              <td class="py-3.5 px-4 hidden md:table-cell">
                <span class="px-2.5 py-1 rounded-full bg-[#0a1a2f] border border-[#333f59] text-[11px] font-mono text-[#7ec8ff]">
                  {{ player.badge }}
                </span>
              </td>

              <!-- Solved Challenges -->
              <td class="py-3.5 px-4 text-center font-mono text-slate-300">
                <div class="flex items-center justify-center gap-2">
                  <span>{{ player.solved }}/{{ player.total }}</span>
                  <div class="w-16 h-1.5 rounded-full bg-[#0a1a2f] border border-[#333f59] overflow-hidden hidden sm:block">
                    <div
                      class="h-full bg-gradient-to-r from-[#004e7a] to-[#7ec8ff]"
                      :style="{ width: `${(player.solved / player.total) * 100}%` }"
                    ></div>
                  </div>
                </div>
              </td>

              <!-- Last Flag -->
              <td class="py-3.5 px-4 text-xs font-mono text-slate-400 hidden lg:table-cell">
                {{ player.lastActivity }}
              </td>

              <!-- Total Score -->
              <td class="py-3.5 px-4 text-right font-mono font-bold text-base">
                <span
                  :class="[
                    recentlyUpdatedUsername === player.username ? 'text-[#7ec8ff] scale-110 inline-block font-black transition-transform' :
                    player.rank === 1 ? 'text-[#ffcc00]' :
                    player.rank <= 3 ? 'text-[#7ec8ff]' :
                    'text-slate-100'
                  ]"
                >
                  {{ player.score.toLocaleString('fr-FR') }} pts
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Controls -->
      <div class="flex items-center justify-between pt-4 border-t border-[#333f59]/60 font-rajdhani text-xs font-bold uppercase tracking-wider">
        <button
          type="button"
          :disabled="currentPage === 1"
          class="px-4 py-2 rounded bg-[#0a1a2f] border border-[#333f59] text-slate-300 hover:text-white hover:border-[#7ec8ff] disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
          @click="currentPage--"
        >
          &larr; Précédent
        </button>

        <div class="flex items-center gap-2">
          <button
            v-for="page in totalPages"
            :key="page"
            type="button"
            :class="[
              currentPage === page
                ? 'bg-[#004e7a] text-white border-[#7ec8ff]'
                : 'bg-[#0a1a2f] text-slate-400 border-[#333f59] hover:text-white',
              'w-8 h-8 rounded border flex items-center justify-center font-mono transition-colors cursor-pointer'
            ]"
            @click="currentPage = page"
          >
            {{ page }}
          </button>
        </div>

        <button
          type="button"
          :disabled="currentPage === totalPages"
          class="px-4 py-2 rounded bg-[#0a1a2f] border border-[#333f59] text-slate-300 hover:text-white hover:border-[#7ec8ff] disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
          @click="currentPage++"
        >
          Suivant &rarr;
        </button>
      </div>
    </div>
  </div>
</template>
