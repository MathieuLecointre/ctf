import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(7) // Initial mockup count
  const notifications = ref([
    {
      id: 1,
      title: '🩸 FIRST BLOOD',
      message: 'Ghost_Protocol a validé Buffer Overflow x86 !',
      timestamp: 'Il y a 5 min',
      category: 'FIRST_BLOOD'
    },
    {
      id: 2,
      title: 'FLAG VALIDÉ',
      message: '0xDEADBEEF a résolu SQL Injection — Blind.',
      timestamp: 'Il y a 12 min',
      category: 'FLAG_SOLVED'
    }
  ])

  // Toast floating notification
  const activeToast = ref(null)
  let toastTimer = null

  function addNotification(notif) {
    unreadCount.value++
    notifications.value.unshift(notif)

    // Trigger toast notification
    activeToast.value = notif

    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => {
      activeToast.value = null
    }, 5000)
  }

  function dismissToast() {
    activeToast.value = null
    if (toastTimer) clearTimeout(toastTimer)
  }

  function markAllRead() {
    unreadCount.value = 0
  }

  return {
    unreadCount,
    notifications,
    activeToast,
    addNotification,
    dismissToast,
    markAllRead
  }
})
