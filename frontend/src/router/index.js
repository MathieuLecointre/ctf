import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChallengesView from '../views/ChallengesView.vue'
import ScoreboardView from '../views/ScoreboardView.vue'
import AuthView from '../views/AuthView.vue'
import ProfileView from '../views/ProfileView.vue'
import AdminChallengesView from '../views/AdminChallengesView.vue'
import { useUserStore } from '../stores/userStore'
import { useNotificationStore } from '../stores/notificationStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/challenges',
      name: 'challenges',
      component: ChallengesView,
    },
    {
      path: '/scoreboard',
      name: 'scoreboard',
      component: ScoreboardView,
    },
    {
      path: '/login',
      name: 'login',
      alias: '/auth',
      component: AuthView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true },
    },
    {
      path: '/admin/challenges',
      name: 'admin-challenges',
      component: AdminChallengesView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

/**
 * Global Navigation Guard:
 * 1. Restricts access to routes flagged with requiresAuth (e.g. /profile, /admin/challenges)
 * 2. Restricts access to routes flagged with requiresAdmin (only userStore.isAdmin allowed)
 */
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 1. Authentication check
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    console.warn(`[Router / Guard] Accès refusé à ${to.path}. Redirection vers /login.`)
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // 2. Administrator role check
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    console.warn(`[Router / Guard] Accès refusé à ${to.path}. Privilèges Administrateur requis.`)
    const notifStore = useNotificationStore()
    notifStore.addNotification({
      id: Date.now(),
      title: 'ACCÈS REFUSÉ',
      category: 'FIRST_BLOOD',
      message: 'Zone restreinte : Privilèges Administrateur requis.',
      timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    })
    return next({ name: 'home' })
  }

  next()
})

export default router
