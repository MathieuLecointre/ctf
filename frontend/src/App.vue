<script setup>
import { onMounted, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
import ToastNotification from './components/ToastNotification.vue'
import wsService from './services/wsService'
import { useNotificationStore } from './stores/notificationStore'
import { useUserStore } from './stores/userStore'

const notifStore = useNotificationStore()
const userStore = useUserStore()

let unsubscribeWs = null

onMounted(() => {
  // Global WebSocket listener for real-time notifications & user score updates
  unsubscribeWs = wsService.onMessage((event) => {
    if (event.type === 'NOTIFICATION' && event.data) {
      notifStore.addNotification(event.data)
    } else if (event.type === 'SCORE_UPDATE' && event.data) {
      // If the current authenticated user's score was updated, synchronize reactive store
      if (userStore.isAuthenticated && userStore.username === event.data.username) {
        userStore.score += event.data.pointsAdded
      }
    }
  })
})

onUnmounted(() => {
  if (unsubscribeWs) {
    unsubscribeWs()
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#0a1a2f] text-slate-100 font-inter flex flex-col selection:bg-[#7ec8ff]/30 selection:text-white relative">
    <!-- Navbar Component -->
    <Navbar />

    <!-- Main Content Area -->
    <main class="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <RouterView />
    </main>

    <!-- CTF Footer -->
    <Footer />

    <!-- Cyber Floating Toast Notifications -->
    <ToastNotification />
  </div>
</template>
