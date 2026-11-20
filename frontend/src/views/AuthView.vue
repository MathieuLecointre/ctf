<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login') // 'login' | 'register'
const email = ref('darkhack3r@upjv.local')
const password = ref('••••••••••••')
const usernameInput = ref('')
const showPassword = ref(false)
const errorMessage = ref('')

const handleAuth = async () => {
  errorMessage.value = ''

  if (!email.value) {
    errorMessage.value = 'Veuillez saisir votre adresse email.'
    return
  }
  if (!password.value) {
    errorMessage.value = 'Veuillez renseigner votre mot de passe.'
    return
  }

  try {
    await userStore.login({
      email: email.value,
      username: usernameInput.value || email.value.split('@')[0]
    })
    // Redirect to home after successful authentication
    router.push('/')
  } catch (err) {
    errorMessage.value = 'Erreur lors de la tentative de connexion.'
  }
}
</script>

<template>
  <div class="min-h-[75vh] flex items-center justify-center py-8 px-4 font-inter">
    <div class="w-full max-w-md relative">
      <!-- Glow ambient background -->
      <div class="absolute -inset-1 bg-gradient-to-r from-[#004e7a] via-[#7ec8ff]/20 to-[#ff3e3e]/30 rounded-xl blur-lg opacity-40"></div>

      <!-- Auth Card -->
      <div class="relative bg-[#162545]/90 border border-[#333f59] rounded-xl p-8 backdrop-blur-md shadow-2xl space-y-6">
        <!-- Tech Corner Brackets -->
        <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
        <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
        <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
        <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

        <!-- Card Header with Brand -->
        <div class="text-center space-y-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0a1a2f] border border-[#333f59] text-[10px] font-mono text-[#7ec8ff] uppercase tracking-widest">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            PORTAIL AUTHENTIFICATION SECURE
          </div>
          <h1 class="text-2xl font-black text-white font-inter tracking-tight flex items-center justify-center gap-1.5">
            <span>CTF</span>
            <span class="text-[#ff3e3e]">UPJV</span>
          </h1>
          <p class="text-xs text-slate-400 font-mono">
            Accès réservé aux auditeurs et étudiants
          </p>
        </div>

        <!-- Mode Toggle Tabs (Login / Register) -->
        <div class="grid grid-cols-2 p-1 bg-[#0a1a2f] border border-[#333f59] rounded-lg font-rajdhani text-xs font-bold uppercase tracking-wider">
          <button
            type="button"
            :class="[
              activeTab === 'login'
                ? 'bg-[#004e7a] text-white shadow'
                : 'text-slate-400 hover:text-white',
              'py-2 rounded transition-all cursor-pointer'
            ]"
            @click="activeTab = 'login'"
          >
            Connexion
          </button>
          <button
            type="button"
            :class="[
              activeTab === 'register'
                ? 'bg-[#004e7a] text-white shadow'
                : 'text-slate-400 hover:text-white',
              'py-2 rounded transition-all cursor-pointer'
            ]"
            @click="activeTab = 'register'"
          >
            S'inscrire
          </button>
        </div>

        <!-- Error Feedback Message -->
        <div
          v-if="errorMessage"
          class="p-3 bg-[#ff3e3e]/10 border border-[#ff3e3e]/50 rounded text-xs font-mono text-[#ff3e3e] flex items-center gap-2"
        >
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Authentication Form -->
        <form class="space-y-4" @submit.prevent="handleAuth">
          <!-- Username (only for register) -->
          <div v-if="activeTab === 'register'" class="space-y-1.5">
            <label class="block text-xs font-mono uppercase text-slate-300 tracking-wider">
              Pseudo / Handle
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500 font-mono text-sm">
                &gt;
              </span>
              <input
                v-model="usernameInput"
                type="text"
                placeholder="ex: 0xHacker"
                class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white placeholder-slate-600 rounded-lg pl-8 pr-4 py-2.5 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
              />
            </div>
          </div>

          <!-- Email Field -->
          <div class="space-y-1.5">
            <label class="block text-xs font-mono uppercase text-slate-300 tracking-wider">
              Adresse Email UPJV
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </span>
              <input
                v-model="email"
                type="email"
                required
                placeholder="root@u-picardie.fr"
                class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white placeholder-slate-600 rounded-lg pl-9 pr-4 py-2.5 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div class="space-y-1.5">
            <div class="flex items-center justify-between">
              <label class="block text-xs font-mono uppercase text-slate-300 tracking-wider">
                Mot de Passe
              </label>
              <a href="#" class="text-[11px] font-mono text-[#7ec8ff] hover:underline">
                Oublié ?
              </a>
            </div>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </span>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="••••••••••••"
                class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white placeholder-slate-600 rounded-lg pl-9 pr-10 py-2.5 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-300"
                @click="showPassword = !showPassword"
              >
                <svg v-if="!showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Submit Button with animated loader -->
          <button
            type="submit"
            :disabled="userStore.isLoading"
            class="w-full mt-4 bg-gradient-to-r from-[#004e7a] to-[#7ec8ff] hover:from-[#004e7a]/90 hover:to-[#7ec8ff]/90 text-white font-rajdhani font-bold py-3 rounded-lg text-sm uppercase tracking-wider shadow-lg shadow-[#004e7a]/40 transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <!-- Spinner -->
            <svg
              v-if="userStore.isLoading"
              class="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>

            <span>
              {{ userStore.isLoading ? 'Authentification en cours...' : (activeTab === 'login' ? 'Initialiser la Session' : 'Créer un Compte') }}
            </span>
          </button>
        </form>

        <!-- Security Disclaimer -->
        <div class="border-t border-[#333f59]/60 pt-4 text-center">
          <p class="text-[10px] font-mono text-slate-500">
            Connexion chiffrée SSL/TLS • UPJV CTF Platform 2026
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
