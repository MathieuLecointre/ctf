<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()

// Mock Data for Quick Stats
const quickStats = [
  { value: '128 K', label: 'JOUEURS' },
  { value: '472', label: 'CHALLENGES' },
  { value: '962 K', label: 'FLAGS VALIDÉS' }
]

// Mock Data for Objective of the Day
const dailyObjective = ref({
  title: 'SQL Injection — Blind',
  category: 'WEB SERVEUR',
  badge: 'INSTANCE DOCKER',
  difficultyCurrent: 3,
  difficultyTotal: 5,
  communityProgress: 62,
  points: 40,
  clicks: '2 418'
})

// Mock Data for Category Tracks
const categories = [
  {
    name: 'WEB - SERVEUR',
    challengesCount: 42,
    icon: 'globe'
  },
  {
    name: 'RÉSEAU',
    challengesCount: 36,
    icon: 'wifi'
  },
  {
    name: 'CRYPTANALYSE',
    challengesCount: 28,
    icon: 'key'
  },
  {
    name: 'FORENSIC',
    challengesCount: 31,
    icon: 'fingerprint'
  },
  {
    name: 'CRACKME',
    challengesCount: 19,
    icon: 'chip'
  },
  {
    name: 'PROGRAMMATION',
    challengesCount: 25,
    icon: 'code'
  }
]

// Mock Data for Weekly Leaderboard (5 players matching mockup)
const leaderboard = [
  { rank: '01', username: 'DEADBEEF', score: '1 840', isCurrent: false },
  { rank: '02', username: 'DEADBEEF', score: '1 745', isCurrent: false },
  { rank: '03', username: 'DEADBEEF', score: '1 600', isCurrent: false },
  { rank: '04', username: 'DEADBEEF', score: '1 340', isCurrent: false },
  { rank: '36', username: 'darkhack3r - VOUS', score: '750', isCurrent: true }
]
</script>

<template>
  <div class="space-y-16 py-4 font-inter text-slate-100">
    <!-- ========================================== -->
    <!-- HERO SECTION                               -->
    <!-- ========================================== -->
    <section class="space-y-8">
      <!-- Tag Category -->
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 bg-[#ff3e3e]"></span>
        <span class="text-xs font-bold text-[#ff3e3e] uppercase tracking-wider font-rajdhani">
          Plateforme d'entraînement cybersécurité
        </span>
      </div>

      <!-- Main Title -->
      <div class="space-y-1">
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black uppercase tracking-tight text-white font-inter">
          Entraîne-toi.
        </h1>
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black uppercase tracking-tight text-[#ff3e3e] font-inter">
          Deviens un pro.
        </h1>
      </div>

      <!-- Hero Subtitle -->
      <p class="text-slate-300 text-sm sm:text-base max-w-2xl leading-relaxed">
        Plus de 40 challenges réels — web, cryptographie, forensic, reverse engineering, scénarios complets.<br />
        Instances Docker isolées, indices progressifs, classements mensuels. 100% gratuit, 0% de blabla.
      </p>

      <!-- Action Buttons -->
      <div class="flex flex-wrap items-center gap-4 pt-2 font-rajdhani font-bold text-sm tracking-wider uppercase">
        <RouterLink
          to="/login"
          class="bg-white hover:bg-slate-200 text-slate-950 px-6 py-2.5 rounded shadow transition-all cursor-pointer inline-block"
        >
          Crée un compte
        </RouterLink>
        <RouterLink
          to="/challenges"
          class="bg-[#004e7a]/40 hover:bg-[#004e7a] text-white border border-[#7ec8ff]/40 hover:border-[#7ec8ff] px-6 py-2.5 rounded transition-all flex items-center justify-center cursor-pointer"
        >
          Explorer les défis
        </RouterLink>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-3 gap-6 max-w-lg pt-4 border-t border-[#333f59]/40 font-rajdhani">
        <div v-for="stat in quickStats" :key="stat.label" class="space-y-0.5">
          <div class="text-2xl sm:text-3xl font-black text-white tracking-tight">
            {{ stat.value }}
          </div>
          <div class="text-[11px] font-semibold text-slate-400 tracking-wider">
            {{ stat.label }}
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- OBJECTIF DU JOUR                           -->
    <!-- ========================================== -->
    <section class="relative">
      <div class="relative bg-[#162545]/50 border border-[#333f59] rounded-lg p-6 sm:p-8 backdrop-blur-sm overflow-hidden">
        <!-- Tech Corner Accents (Cyberpunk brackets) -->
        <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
        <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
        <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
        <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

        <!-- Header Tag -->
        <div class="flex items-center gap-2 mb-3">
          <span class="w-2 h-2 bg-[#ff3e3e]"></span>
          <span class="text-xs font-bold text-[#ff3e3e] uppercase tracking-wider font-rajdhani">
            Objectif du jour
          </span>
        </div>

        <!-- Challenge Title -->
        <h2 class="text-2xl sm:text-3xl font-black text-white font-inter tracking-tight mb-2">
          {{ dailyObjective.title }}
        </h2>

        <!-- Sub info -->
        <div class="text-[11px] font-mono tracking-widest text-slate-400 uppercase mb-5">
          {{ dailyObjective.category }} • {{ dailyObjective.badge }}
        </div>

        <!-- Difficulty Bar -->
        <div class="flex items-center gap-3 mb-6">
          <div class="flex items-center gap-1.5">
            <span
              v-for="i in dailyObjective.difficultyTotal"
              :key="i"
              :class="[
                i <= dailyObjective.difficultyCurrent ? 'bg-[#ff3e3e]' : 'bg-[#333f59]',
                'w-6 sm:w-8 h-2 rounded-[2px]'
              ]"
            ></span>
          </div>
          <span class="text-xs font-mono font-bold text-slate-400 ml-2 uppercase">
            Difficulté : {{ dailyObjective.difficultyCurrent }}/{{ dailyObjective.difficultyTotal }}
          </span>
        </div>

        <!-- Community Progress Bar -->
        <div class="space-y-2 mb-6">
          <div class="flex items-center justify-between text-xs font-mono">
            <span class="text-slate-400 tracking-wider">PROGRESSION DE LA COMMUNAUTÉ</span>
            <span class="text-slate-300 font-bold">{{ dailyObjective.communityProgress }}%</span>
          </div>
          <div class="w-full h-2 rounded bg-[#0a1a2f] border border-[#333f59]/80 overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-[#ff3e3e] to-[#ff6b6b] transition-all duration-500"
              :style="{ width: `${dailyObjective.communityProgress}%` }"
            ></div>
          </div>
        </div>

        <!-- Bottom Badges / CTA -->
        <div class="flex flex-wrap items-center gap-3 pt-2 font-rajdhani text-xs font-bold tracking-wider">
          <span class="px-3 py-1.5 rounded bg-[#162545] border border-[#333f59] text-[#7ec8ff]">
            +{{ dailyObjective.points }} PTS
          </span>
          <span class="px-3 py-1.5 rounded bg-[#162545] border border-[#333f59] text-slate-300">
            {{ dailyObjective.clicks }} CLICS
          </span>
          <RouterLink
            to="/challenges"
            class="px-4 py-1.5 rounded border border-[#ff3e3e] text-[#ff3e3e] hover:bg-[#ff3e3e] hover:text-white transition-colors uppercase ml-auto"
          >
            Se mettre au défi
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- PARCOURS D'APPRENTISSAGE                   -->
    <!-- ========================================== -->
    <section class="space-y-6">
      <!-- Section Header -->
      <div class="flex items-end justify-between">
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-[#ff3e3e]"></span>
            <span class="text-xs font-bold text-[#ff3e3e] uppercase tracking-wider font-rajdhani">
              Parcours d'apprentissage
            </span>
          </div>
          <h2 class="text-2xl sm:text-3xl font-black text-white tracking-tight font-inter">
            Choisis ton terrain de jeu
          </h2>
          <p class="text-xs sm:text-sm text-slate-400 max-w-2xl leading-relaxed">
            6 catégories, du niveau débutant à l'expert. Chaque catégorie a sa propre progression, des stats, des badges à débloquer.
          </p>
        </div>
        <RouterLink
          to="/challenges"
          class="hidden sm:flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white font-rajdhani tracking-wider uppercase transition-colors"
        >
          <span>Voir tout</span>
          <svg class="w-4 h-4 text-[#ff3e3e]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </RouterLink>
      </div>

      <!-- Categories Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="cat in categories"
          :key="cat.name"
          class="group relative bg-[#162545]/40 hover:bg-[#162545]/80 border border-[#333f59] hover:border-[#7ec8ff]/60 rounded-lg p-5 transition-all duration-200 cursor-pointer flex items-center gap-5"
        >
          <!-- Icon Box -->
          <div class="w-12 h-12 rounded border border-[#333f59] bg-[#0a1a2f] flex items-center justify-center text-[#7ec8ff] group-hover:border-[#7ec8ff] group-hover:scale-105 transition-all">
            <!-- Globe (Web) -->
            <svg v-if="cat.icon === 'globe'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke-width="1.8" />
              <path stroke-width="1.8" d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
            </svg>
            <!-- Wifi (Network) -->
            <svg v-else-if="cat.icon === 'wifi'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.14 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
            </svg>
            <!-- Key (Crypto) -->
            <svg v-else-if="cat.icon === 'key'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
            <!-- Fingerprint (Forensic) -->
            <svg v-else-if="cat.icon === 'fingerprint'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 004 11m0 0a8.003 8.003 0 0115.357-2m-3.45 13.064A13.924 13.924 0 0112 21a13.924 13.924 0 01-3.907-.557" />
            </svg>
            <!-- Chip / Lock (Crackme) -->
            <svg v-else-if="cat.icon === 'chip'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <rect x="4" y="4" width="16" height="16" rx="2" stroke-width="2" />
              <rect x="9" y="9" width="6" height="6" stroke-width="2" />
              <path stroke-width="2" d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
            </svg>
            <!-- Code (Programmation) -->
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>

          <!-- Content -->
          <div>
            <h3 class="text-base font-bold text-white tracking-wide font-rajdhani group-hover:text-[#7ec8ff] transition-colors">
              {{ cat.name }}
            </h3>
            <span class="text-xs font-mono text-slate-400">
              {{ cat.challengesCount }} DÉFIS
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- LE CLASSEMENT DE LA SEMAINE                -->
    <!-- ========================================== -->
    <section class="space-y-6">
      <!-- Section Header -->
      <div class="flex items-end justify-between">
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-[#ff3e3e]"></span>
            <span class="text-xs font-bold text-[#ff3e3e] uppercase tracking-wider font-rajdhani">
              Communauté
            </span>
          </div>
          <h2 class="text-2xl sm:text-3xl font-black text-white tracking-tight font-inter">
            Le classement de la semaine
          </h2>
        </div>
        <RouterLink
          to="/scoreboard"
          class="hidden sm:flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white font-rajdhani tracking-wider uppercase transition-colors"
        >
          <span>Classement complet</span>
          <svg class="w-4 h-4 text-[#ff3e3e]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </RouterLink>
      </div>

      <!-- Leaderboard Box with Tech Corner Brackets -->
      <div class="relative bg-[#162545]/40 border border-[#333f59] rounded-lg p-4 sm:p-6 backdrop-blur-sm">
        <!-- Tech Corners -->
        <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
        <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
        <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
        <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

        <!-- Table / Rows -->
        <div class="divide-y divide-[#333f59]/60 font-rajdhani">
          <div
            v-for="player in leaderboard"
            :key="player.rank + player.username"
            :class="[
              player.isCurrent
                ? 'bg-[#ff3e3e]/10 border border-[#ff3e3e]/40 rounded my-1 px-4 py-3'
                : 'hover:bg-[#162545]/60 px-4 py-3',
              'flex items-center justify-between transition-colors text-sm sm:text-base font-semibold'
            ]"
          >
            <!-- Rank & Username -->
            <div class="flex items-center gap-6">
              <span
                :class="[
                  player.isCurrent
                    ? 'text-[#ff3e3e]'
                    : player.rank === '01'
                      ? 'text-[#ffcc00]'
                      : 'text-slate-400',
                  'font-mono font-bold w-6'
                ]"
              >
                {{ player.rank }}
              </span>
              <span
                :class="[
                  player.isCurrent ? 'text-[#ff3e3e] font-bold' : 'text-slate-100',
                  'tracking-wide'
                ]"
              >
                {{ player.username }}
              </span>
            </div>

            <!-- Score -->
            <div
              :class="[
                player.isCurrent ? 'text-[#ff3e3e] font-bold' : 'text-slate-300',
                'font-mono font-bold'
              ]"
            >
              {{ player.score }}
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
