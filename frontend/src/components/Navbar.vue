<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'
import { useNotificationStore } from '../stores/notificationStore'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notifStore = useNotificationStore()

const showNotifDropdown = ref(false)

const toggleNotifDropdown = () => {
  showNotifDropdown.value = !showNotifDropdown.value
  if (showNotifDropdown.value) {
    notifStore.markAllRead()
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="w-full bg-[#0a1a2f] border-b border-[#333f59]/60 sticky top-0 z-50 text-white font-inter">
    <!-- Top Bar with Logo & Navigation -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 gap-4">
        <!-- Brand / Logo -->
        <div class="flex items-center gap-6">
          <RouterLink to="/" class="flex items-center space-x-1.5 group select-none">
            <span class="text-2xl font-black tracking-tight text-white font-inter">CTF</span>
            <span class="text-2xl font-black tracking-tight text-[#ff3e3e] font-inter">UPJV</span>
          </RouterLink>

          <!-- Nav Links -->
          <nav class="hidden md:flex items-center space-x-1 font-rajdhani text-sm font-semibold tracking-wider uppercase">
            <RouterLink
              to="/"
              :class="[
                route.path === '/'
                  ? 'text-[#7ec8ff] bg-[#162545] border-b-2 border-[#7ec8ff]'
                  : 'text-slate-300 hover:text-white hover:bg-[#162545]/60',
                'px-3 py-1.5 rounded-t transition-colors'
              ]"
            >
              Accueil
            </RouterLink>
            <RouterLink
              to="/challenges"
              :class="[
                route.path.startsWith('/challenges')
                  ? 'text-[#7ec8ff] bg-[#162545] border-b-2 border-[#7ec8ff]'
                  : 'text-slate-300 hover:text-white hover:bg-[#162545]/60',
                'px-3 py-1.5 rounded-t transition-colors'
              ]"
            >
              Défis
            </RouterLink>
            <RouterLink
              to="/scoreboard"
              :class="[
                route.path.startsWith('/scoreboard')
                  ? 'text-[#7ec8ff] bg-[#162545] border-b-2 border-[#7ec8ff]'
                  : 'text-slate-300 hover:text-white hover:bg-[#162545]/60',
                'px-3 py-1.5 rounded-t transition-colors'
              ]"
            >
              Classement
            </RouterLink>
          </nav>
        </div>

        <!-- Center: Search bar -->
        <div class="flex-1 max-w-md hidden sm:flex items-center justify-center">
          <div class="relative w-full">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </span>
            <input
              type="text"
              placeholder="Rechercher un défi, un joueur..."
              class="w-full py-1.5 pl-9 pr-4 rounded-md bg-white text-slate-900 placeholder-slate-400 text-xs sm:text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#7ec8ff] transition-all"
            />
          </div>
        </div>

        <!-- Right Side: State-dependent Authentication vs Profile -->
        <div class="flex items-center space-x-3">
          <!-- ---------------------------------------- -->
          <!-- AUTHENTICATED STATE                      -->
          <!-- ---------------------------------------- -->
          <template v-if="userStore.isAuthenticated">
            <!-- Notification Bell with dynamic badge & dropdown -->
            <div class="relative">
              <button
                type="button"
                class="relative p-1.5 text-slate-200 hover:text-white hover:bg-[#162545] rounded-lg transition-colors cursor-pointer"
                title="Notifications"
                @click="toggleNotifDropdown"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" />
                </svg>
                <span
                  v-if="notifStore.unreadCount > 0"
                  class="absolute -top-1 -right-1 bg-[#ff3e3e] text-white text-[10px] font-bold min-w-4 h-4 px-1 rounded-full flex items-center justify-center font-inter shadow animate-pulse"
                >
                  {{ notifStore.unreadCount }}
                </span>
              </button>

              <!-- Notifications Dropdown -->
              <div
                v-if="showNotifDropdown"
                class="absolute right-0 mt-2 w-80 bg-[#162545] border border-[#333f59] rounded-xl shadow-2xl z-50 overflow-hidden font-inter"
              >
                <div class="p-3 border-b border-[#333f59] flex items-center justify-between">
                  <span class="text-xs font-bold text-white uppercase font-rajdhani tracking-wider">
                    Événements en direct
                  </span>
                  <span class="text-[10px] font-mono text-[#7ec8ff]">WEBSOCKET LIVE</span>
                </div>
                <div class="max-h-64 overflow-y-auto divide-y divide-[#333f59]/40">
                  <div
                    v-for="item in notifStore.notifications.slice(0, 6)"
                    :key="item.id"
                    class="p-3 hover:bg-[#0a1a2f]/50 transition-colors space-y-1"
                  >
                    <div class="flex items-center justify-between">
                      <span
                        :class="[
                          item.category === 'FIRST_BLOOD' ? 'text-[#ff3e3e]' : 'text-[#7ec8ff]',
                          'text-[11px] font-bold font-rajdhani'
                        ]"
                      >
                        {{ item.title }}
                      </span>
                      <span class="text-[9px] font-mono text-slate-400">{{ item.timestamp }}</span>
                    </div>
                    <p class="text-xs text-slate-300 font-mono line-clamp-2">
                      {{ item.message }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Dynamic Points Badge -->
            <div class="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-transparent text-white font-rajdhani text-sm font-bold tracking-wide">
              <svg class="w-4 h-4 text-[#ffcc00] fill-current" viewBox="0 0 24 24">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
              </svg>
              <span>{{ userStore.score }} pts</span>
            </div>

            <!-- Profile Badge with Username & Rank -->
            <div class="flex items-center gap-2 border border-[#333f59] bg-[#162545]/80 hover:bg-[#162545] px-3 py-1 rounded text-xs font-rajdhani font-semibold text-slate-200 tracking-wider transition-colors">
              <svg class="w-4 h-4 text-[#7ec8ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span class="font-mono font-bold text-white">{{ userStore.username }}</span>
              <span v-if="userStore.rank" class="text-[10px] text-slate-400 font-mono hidden md:inline">
                (#{{ userStore.rank }})
              </span>
            </div>

            <!-- Logout Button -->
            <button
              type="button"
              class="p-1.5 rounded-lg border border-[#333f59] bg-[#162545]/60 hover:bg-[#ff3e3e]/20 text-slate-400 hover:text-[#ff3e3e] hover:border-[#ff3e3e]/60 transition-colors cursor-pointer"
              title="Déconnexion"
              @click="handleLogout"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </template>

          <!-- ---------------------------------------- -->
          <!-- UNAUTHENTICATED STATE                    -->
          <!-- ---------------------------------------- -->
          <template v-else>
            <div class="flex items-center space-x-2 font-rajdhani font-bold text-xs uppercase tracking-wider">
              <RouterLink
                to="/login"
                class="px-4 py-1.5 border border-[#333f59] bg-[#004e7a]/40 hover:bg-[#004e7a] text-slate-200 hover:text-white rounded transition-colors"
              >
                Connexion
              </RouterLink>
              <RouterLink
                to="/login"
                class="px-4 py-1.5 bg-white hover:bg-slate-200 text-slate-900 rounded font-extrabold transition-colors shadow"
              >
                S'inscrire
              </RouterLink>
            </div>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>
