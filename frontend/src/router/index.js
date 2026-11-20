import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChallengesView from '../views/ChallengesView.vue'
import ScoreboardView from '../views/ScoreboardView.vue'
import AuthView from '../views/AuthView.vue'

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
  ],
})

export default router
