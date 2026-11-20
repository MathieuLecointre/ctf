<script setup>
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useUserStore } from '../stores/userStore'
import { mockChallenges } from '../data/mockChallenges'

const userStore = useUserStore()

onMounted(async () => {
  // Silent profile fetch attempt (with local fallback)
  await userStore.fetchProfile()
})

// Total available challenges count
const totalChallengesCount = computed(() => mockChallenges.length)
const solvedCount = computed(() => userStore.solvedChallenges.length)
const completionRate = computed(() => {
  if (!totalChallengesCount.value) return 0
  return Math.round((solvedCount.value / totalChallengesCount.value) * 100)
})

// Dynamic category progress based on available vs solved challenges
const categoriesProgress = computed(() => {
  const groups = [
    { key: 'Web - Injection', label: 'Injections SQL & Backend', icon: 'terminal' },
    { key: 'Web - Client-Side', label: 'Client-Side (XSS & CSRF)', icon: 'browser' },
    { key: 'Web - API & Auth', label: 'API, IDOR & Jetons JWT', icon: 'key' },
    { key: 'Web - Server-Side', label: 'Server-Side (SSRF & Metadata)', icon: 'server' },
    { key: 'Web - Cryptographie', label: 'Crypto Web (Padding Oracle)', icon: 'lock' },
  ]

  return groups.map((g) => {
    const totalInCat = mockChallenges.filter((c) => c.category === g.key).length
    const solvedInCat = userStore.solvedChallenges.filter((c) => c.category === g.key).length
    const percent = totalInCat > 0 ? Math.round((solvedInCat / totalInCat) * 100) : 0

    return {
      name: g.label,
      total: totalInCat,
      solved: solvedInCat,
      percent,
      icon: g.icon
    }
  })
})
</script>

<template>
  <div class="space-y-10 font-inter text-slate-100 py-4">
    <!-- ========================================== -->
    <!-- 1. HERO PROFIL & INFORMATIONS JOUEUR       -->
    <!-- ========================================== -->
    <section class="relative bg-[#162545]/50 border border-[#333f59] rounded-xl p-6 sm:p-8 backdrop-blur-md shadow-2xl">
      <!-- Tech Corner Brackets -->
      <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
      <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
      <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
      <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
        <!-- Identity / Avatar & Details -->
        <div class="flex items-center gap-6">
          <!-- Cyber Avatar -->
          <div class="relative">
            <div class="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-gradient-to-tr from-[#004e7a] via-[#162545] to-[#7ec8ff] p-[2px] shadow-lg shadow-[#004e7a]/30">
              <div class="w-full h-full bg-[#0a1a2f] rounded-[14px] flex flex-col items-center justify-center font-mono">
                <span class="text-2xl sm:text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-[#7ec8ff] to-white">
                  0x
                </span>
                <span class="text-[9px] uppercase tracking-widest text-[#7ec8ff]">HACKER</span>
              </div>
            </div>
            <!-- Online status badge -->
            <span class="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 border-2 border-[#0a1a2f] rounded-full animate-pulse" title="Session active"></span>
          </div>

          <!-- User Details -->
          <div class="space-y-1.5">
            <div class="flex items-center gap-3">
              <h1 class="text-2xl sm:text-3xl font-black text-white font-inter tracking-tight">
                {{ userStore.username }}
              </h1>
              <span class="px-2.5 py-0.5 rounded-full bg-[#004e7a]/40 border border-[#7ec8ff]/40 text-[#7ec8ff] font-mono text-[10px] font-bold uppercase tracking-wider">
                Auditeur V1
              </span>
            </div>

            <div class="text-xs font-mono text-slate-400 flex items-center gap-2">
              <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
              </svg>
              <span>{{ userStore.email }}</span>
            </div>

            <div class="text-[11px] font-mono text-slate-500 flex items-center gap-2 pt-0.5">
              <span>Membre inscrit le {{ userStore.joinedAt }}</span>
              <span>•</span>
              <span class="text-emerald-400 font-semibold">Traefik Reverse-Proxy Connecté</span>
            </div>
          </div>
        </div>

        <!-- 3 Key Metric Cards -->
        <div class="grid grid-cols-3 gap-3 sm:gap-4 font-rajdhani">
          <!-- Metric 1: Total Score -->
          <div class="bg-[#0a1a2f]/80 border border-[#333f59] rounded-xl p-4 text-center sm:min-w-[120px] shadow">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Score Total</div>
            <div class="text-2xl sm:text-3xl font-black text-[#ffcc00] font-mono mt-1">
              {{ userStore.score }}
            </div>
            <div class="text-[10px] text-slate-500 font-mono mt-0.5">points</div>
          </div>

          <!-- Metric 2: Rank -->
          <div class="bg-[#0a1a2f]/80 border border-[#333f59] rounded-xl p-4 text-center sm:min-w-[120px] shadow">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Rang Global</div>
            <div class="text-2xl sm:text-3xl font-black text-[#7ec8ff] font-mono mt-1">
              #{{ userStore.rank || 42 }}
            </div>
            <div class="text-[10px] text-emerald-400 font-mono mt-0.5">Top 5% promo</div>
          </div>

          <!-- Metric 3: Completion Rate -->
          <div class="bg-[#0a1a2f]/80 border border-[#333f59] rounded-xl p-4 text-center sm:min-w-[120px] shadow">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Complétion Web</div>
            <div class="text-2xl sm:text-3xl font-black text-white font-mono mt-1">
              {{ completionRate }}%
            </div>
            <div class="text-[10px] text-slate-400 font-mono mt-0.5">
              {{ solvedCount }} / {{ totalChallengesCount }} défis
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- 2. PROGRESSION PAR CATÉGORIE WEB           -->
    <!-- ========================================== -->
    <section class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-[#ff3e3e]"></span>
            <h2 class="text-xs font-bold text-[#ff3e3e] uppercase tracking-wider font-rajdhani">
              Matrice de Compétences
            </h2>
          </div>
          <h3 class="text-xl sm:text-2xl font-black text-white font-inter tracking-tight">
            Progression par Domaine Web HTTPS
          </h3>
        </div>
        <span class="text-xs font-mono text-slate-400 bg-[#162545] px-3 py-1 rounded border border-[#333f59]">
          Périmètre V1 Traefik
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="cat in categoriesProgress"
          :key="cat.name"
          class="bg-[#162545]/40 border border-[#333f59] rounded-xl p-5 backdrop-blur-sm space-y-3"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <div class="w-7 h-7 rounded bg-[#0a1a2f] border border-[#333f59] flex items-center justify-center text-[#7ec8ff]">
                <svg v-if="cat.icon === 'terminal'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <svg v-else-if="cat.icon === 'browser'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <svg v-else-if="cat.icon === 'key'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
                <svg v-else-if="cat.icon === 'server'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <span class="text-sm font-bold text-white font-rajdhani">{{ cat.name }}</span>
            </div>

            <div class="text-xs font-mono font-bold text-slate-300">
              <span class="text-[#7ec8ff]">{{ cat.solved }}</span> / {{ cat.total }}
              <span class="text-slate-500 font-normal ml-1">({{ cat.percent }}%)</span>
            </div>
          </div>

          <!-- Progress Bar Container -->
          <div class="w-full h-2 rounded-full bg-[#0a1a2f] border border-[#333f59]/80 overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-[#004e7a] to-[#7ec8ff] transition-all duration-700 ease-out rounded-full"
              :style="{ width: `${cat.percent}%` }"
            ></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- 3. HISTORIQUE DES FLAGS & INSTANCES ACTIVES -->
    <!-- ========================================== -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- Left Column (8 cols): Solved Flags History -->
      <div class="lg:col-span-8 space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-[#7ec8ff]"></span>
            <h3 class="text-lg font-black text-white font-inter tracking-tight">
              Historique des Flags Validés
            </h3>
          </div>
          <span class="text-xs font-mono text-emerald-400 font-bold">
            {{ solvedCount }} défis validés
          </span>
        </div>

        <div class="relative bg-[#162545]/40 border border-[#333f59] rounded-xl overflow-hidden backdrop-blur-sm">
          <!-- Tech Brackets Accents -->
          <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
          <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
          <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
          <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

          <div class="overflow-x-auto">
            <table class="w-full text-left font-rajdhani border-collapse">
              <thead>
                <tr class="border-b border-[#333f59] text-xs font-bold uppercase tracking-wider text-slate-400 bg-[#0a1a2f]/40">
                  <th class="py-3 px-4">Défi Web Résolu</th>
                  <th class="py-3 px-4 hidden sm:table-cell">Catégorie</th>
                  <th class="py-3 px-4 text-center">Points</th>
                  <th class="py-3 px-4 text-right">Horodatage</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#333f59]/40 text-sm">
                <tr
                  v-for="flag in userStore.solvedChallenges"
                  :key="flag.id"
                  class="hover:bg-[#162545]/80 transition-colors"
                >
                  <!-- Title & Success Icon -->
                  <td class="py-3.5 px-4 font-bold text-white">
                    <div class="flex items-center gap-2">
                      <svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                      </svg>
                      <span class="font-mono text-xs sm:text-sm">{{ flag.title }}</span>
                    </div>
                  </td>

                  <!-- Category Badge -->
                  <td class="py-3.5 px-4 hidden sm:table-cell">
                    <span class="px-2 py-0.5 rounded border text-[11px] font-mono" :class="flag.badgeColor">
                      {{ flag.category }}
                    </span>
                  </td>

                  <!-- Points -->
                  <td class="py-3.5 px-4 text-center font-mono font-bold text-[#ffcc00]">
                    +{{ flag.points }} pts
                  </td>

                  <!-- Timestamp -->
                  <td class="py-3.5 px-4 text-right font-mono text-xs text-slate-400">
                    {{ flag.solvedAt }}
                  </td>
                </tr>

                <tr v-if="userStore.solvedChallenges.length === 0">
                  <td colspan="4" class="py-8 text-center text-slate-500 font-mono text-xs">
                    Aucun flag validé pour le moment. Explorez le catalogue de défis pour débuter.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column (4 cols): Active Instances & Fast Navigation -->
      <div class="lg:col-span-4 space-y-6">
        <!-- Active Instances Box -->
        <div class="relative bg-[#162545]/50 border border-[#333f59] rounded-xl p-6 backdrop-blur-sm space-y-5">
          <!-- Tech Brackets Accents -->
          <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
          <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
          <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
          <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

          <div class="flex items-center justify-between border-b border-[#333f59]/60 pb-3">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider font-rajdhani flex items-center gap-2">
              <span class="w-2 h-2 bg-[#7ec8ff]"></span>
              Mes Instances Actives
            </h3>
            <span class="text-[10px] font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
              DOCKER SWARM
            </span>
          </div>

          <!-- Quota Indicator -->
          <div class="space-y-2">
            <div class="flex items-center justify-between text-xs font-mono">
              <span class="text-slate-400">QUOTA DISPONIBLE</span>
              <span class="text-[#7ec8ff] font-bold">1 / 2 slots occupés</span>
            </div>
            <div class="w-full h-2 rounded bg-[#0a1a2f] border border-[#333f59] overflow-hidden">
              <div class="h-full bg-gradient-to-r from-[#004e7a] to-[#7ec8ff] w-1/2"></div>
            </div>
          </div>

          <!-- Active Instance Summary Card -->
          <div class="bg-[#0a1a2f]/80 border border-[#333f59] rounded-lg p-3 space-y-2 text-xs font-mono">
            <div class="flex items-center justify-between text-[11px]">
              <span class="text-white font-bold truncate">SQL Injection — Blind</span>
              <span class="text-emerald-400 font-bold flex items-center gap-1 shrink-0">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                EN LIGNE
              </span>
            </div>
            <div class="text-[10px] text-[#7ec8ff] truncate">
              https://a9f3b8c1.chal.ctf.upjv.local
            </div>
          </div>

          <p class="text-[11px] text-slate-400 font-inter leading-relaxed">
            Chaque conteneur dispose d'un sous-domaine chiffré HTTPS Traefik et d'une durée de vie de 60 min (extensible jusqu'à 3h).
          </p>

          <!-- Direct Link to Challenges -->
          <RouterLink
            to="/challenges"
            class="w-full bg-[#004e7a] hover:bg-[#004e7a]/80 text-white border border-[#7ec8ff]/60 hover:border-[#7ec8ff] font-rajdhani font-bold py-2.5 rounded-lg text-xs tracking-wider uppercase transition-all shadow flex items-center justify-center gap-2"
          >
            <span>Gérer mes conteneurs</span>
            <svg class="w-4 h-4 text-[#7ec8ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </RouterLink>
        </div>

        <!-- Security & Audit Info Card -->
        <div class="bg-[#162545]/30 border border-[#333f59] rounded-xl p-5 space-y-3 font-mono text-xs">
          <div class="flex items-center gap-2 text-slate-300 font-bold text-xs uppercase font-rajdhani">
            <svg class="w-4 h-4 text-[#7ec8ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>Intégrité de Session</span>
          </div>
          <div class="text-[11px] text-slate-400 leading-relaxed font-inter">
            Authentification via jeton Bearer JWT signé HMAC-SHA256. Vos soumissions de flags sont horodatées et vérifiées par le backend FastAPI.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
