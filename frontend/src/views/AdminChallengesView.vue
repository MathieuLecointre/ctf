<script setup>
import { ref, computed } from 'vue'
import { mockChallenges } from '../data/mockChallenges'
import challengeService from '../services/challengeService'
import { useNotificationStore } from '../stores/notificationStore'

const notifStore = useNotificationStore()

// State: Challenges list (reactive local copy for instant CRUD manipulation)
const challengesList = ref([...mockChallenges])
const searchQuery = ref('')
const selectedCategory = ref('ALL')

// Modal & Form State
const isModalOpen = ref(false)
const isEditMode = ref(false)
const isDeleteConfirmOpen = ref(false)
const challengeToDelete = ref(null)
const isSubmitting = ref(false)

const formErrors = ref({})

const defaultFormData = {
  id: '',
  title: '',
  category: 'Web - Injection',
  categoryCode: 'WEB',
  points: 25,
  difficulty: 2,
  description: '',
  flag: 'CTF{votre_flag_ici}',
  dockerImage: 'ctf/web-app:1.0',
  author: 'Admin'
}

const formData = ref({ ...defaultFormData })

const categories = [
  'Web - Injection',
  'Web - Client-Side',
  'Web - API & Auth',
  'Web - Server-Side',
  'Web - Cryptographie'
]

// Docker Whitelist Regex: strictly requires starting with 'ctf/'
const DOCKER_IMAGE_REGEX = /^ctf\/[a-z0-9\-_]+(:[a-z0-9.\-_]+)?$/
const FLAG_REGEX = /^CTF\{[A-Za-z0-9_\-!@#$%^&*+=?]+\}$/

// Filtered Challenges List
const filteredChallenges = computed(() => {
  return challengesList.value.filter((chal) => {
    const matchesSearch =
      chal.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      chal.dockerImage?.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCat = selectedCategory.value === 'ALL' || chal.category === selectedCategory.value
    return matchesSearch && matchesCat
  })
})

// Open Modal for Create
const openCreateModal = () => {
  isEditMode.value = false
  formData.value = {
    ...defaultFormData,
    id: `chal-${Date.now().toString(36)}`,
    flag: `CTF{web_flag_${Math.random().toString(36).substring(2, 8)}}`,
    dockerImage: 'ctf/web-new-service:1.0'
  }
  formErrors.value = {}
  isModalOpen.value = true
}

// Open Modal for Edit
const openEditModal = (chal) => {
  isEditMode.value = true
  formData.value = {
    id: chal.id,
    title: chal.title,
    category: chal.category,
    categoryCode: chal.categoryCode || 'WEB',
    points: chal.points,
    difficulty: chal.difficulty,
    description: chal.description,
    flag: chal.flag || 'CTF{flag_placeholder}',
    dockerImage: chal.dockerImage || `ctf/${chal.id}:1.0`,
    author: chal.author || 'Admin'
  }
  formErrors.value = {}
  isModalOpen.value = true
}

// Validate Form
const validateForm = () => {
  const errors = {}

  if (!formData.value.title.trim()) {
    errors.title = 'Le titre du défi est obligatoire.'
  }

  if (!formData.value.description.trim()) {
    errors.description = 'La description technique est requise.'
  }

  if (!formData.value.points || formData.value.points < 5) {
    errors.points = 'Attribuez au moins 5 points.'
  }

  // Flag format validation: CTF{...}
  if (!FLAG_REGEX.test(formData.value.flag.trim())) {
    errors.flag = 'Le flag doit respecter le format CTF{...} sans espaces.'
  }

  // Docker Image Security Rule: Whitelist enforced
  const image = formData.value.dockerImage.trim()
  if (!image) {
    errors.dockerImage = "L'image Docker est obligatoire."
  } else if (!image.startsWith('ctf/')) {
    errors.dockerImage = "Règle de sécurité orchestrateur : l'image doit obligatoirement commencer par 'ctf/' (ex: ctf/web-sqli:1.0)."
  } else if (!DOCKER_IMAGE_REGEX.test(image)) {
    errors.dockerImage = 'Format d\'image Docker invalide (utilisez des minuscules, chiffres, tirets et un tag optionnel ex: ctf/web-app:1.0).'
  }

  formErrors.value = errors
  return Object.keys(errors).length === 0
}

// Handle Form Submission
const handleSubmit = async () => {
  if (!validateForm()) return

  isSubmitting.value = true

  try {
    const payload = {
      ...formData.value,
      targetSubdomain: formData.value.title.toLowerCase().replace(/[^a-z0-9]/g, '-'),
      targetUrl: `https://${Math.random().toString(36).substring(2, 10)}.chal.ctf.upjv.local`,
      borderAccent: 'border-emerald-500/80',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
    }

    if (isEditMode.value) {
      // Update
      await challengeService.updateChallenge(payload.id, payload)
      const index = challengesList.value.findIndex((c) => c.id === payload.id)
      if (index !== -1) {
        challengesList.value[index] = { ...challengesList.value[index], ...payload }
      }
      notifStore.addNotification({
        id: Date.now(),
        title: 'DÉFI MODIFIÉ',
        category: 'FLAG_SOLVED',
        message: `Le défi "${payload.title}" a été mis à jour avec succès.`,
        timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
      })
    } else {
      // Create
      const created = await challengeService.createChallenge(payload)
      challengesList.value.unshift(created)
      notifStore.addNotification({
        id: Date.now(),
        title: 'NOUVEAU DÉFI CRÉÉ',
        category: 'FLAG_SOLVED',
        message: `Le défi "${payload.title}" (${payload.dockerImage}) a été ajouté au catalogue.`,
        timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
      })
    }

    isModalOpen.value = false
  } catch (err) {
    notifStore.addNotification({
      id: Date.now(),
      title: 'ERREUR ADMIN',
      category: 'FIRST_BLOOD',
      message: 'Erreur lors de l\'enregistrement du défi.',
      timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    })
  } finally {
    isSubmitting.value = false
  }
}

// Delete Confirmation
const promptDelete = (chal) => {
  challengeToDelete.value = chal
  isDeleteConfirmOpen.value = true
}

const confirmDelete = async () => {
  if (!challengeToDelete.value) return

  const targetId = challengeToDelete.value.id
  const targetTitle = challengeToDelete.value.title

  try {
    await challengeService.deleteChallenge(targetId)
    challengesList.value = challengesList.value.filter((c) => c.id !== targetId)

    notifStore.addNotification({
      id: Date.now(),
      title: 'DÉFI SUPPRIMÉ',
      category: 'FIRST_BLOOD',
      message: `Le défi "${targetTitle}" a été retiré du catalogue.`,
      timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    })
  } finally {
    isDeleteConfirmOpen.value = false
    challengeToDelete.value = null
  }
}
</script>

<template>
  <div class="space-y-8 font-inter text-slate-100 py-4">
    <!-- ========================================== -->
    <!-- 1. HEADER ADMIN                            -->
    <!-- ========================================== -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#333f59]/60 pb-6">
      <div class="space-y-1">
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-[#ff3e3e] animate-pulse"></span>
          <span class="text-xs font-bold text-[#ff3e3e] uppercase tracking-wider font-rajdhani">
            Console d'Administration
          </span>
          <span class="text-slate-600">•</span>
          <span class="px-2 py-0.5 rounded bg-[#ffcc00]/20 text-[#ffcc00] border border-[#ffcc00]/40 text-[10px] font-mono font-bold">
            RESTREINT ROOT
          </span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white font-inter">
          Administration // Catalogue V1 (Web HTTPS)
        </h1>
        <p class="text-xs text-slate-400 font-mono">
          Gestion du cycle de vie des conteneurs Docker autorisés (whitelist ctf/*) et routage Traefik
        </p>
      </div>

      <!-- Action: Create Challenge Button -->
      <button
        type="button"
        class="bg-gradient-to-r from-[#004e7a] to-[#7ec8ff] hover:from-[#004e7a]/90 hover:to-[#7ec8ff]/90 text-white font-rajdhani font-bold px-5 py-2.5 rounded-lg text-sm uppercase tracking-wider shadow-lg shadow-[#004e7a]/30 transition-all flex items-center justify-center gap-2 cursor-pointer shrink-0"
        @click="openCreateModal"
      >
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
        </svg>
        <span>+ Nouveau Défi</span>
      </button>
    </div>

    <!-- ========================================== -->
    <!-- 2. CONTROLS: FILTERS & STATS               -->
    <!-- ========================================== -->
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
      <!-- Search Input -->
      <div class="md:col-span-6 relative">
        <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 pointer-events-none">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher par titre ou image Docker (ex: ctf/web-...)"
          class="w-full bg-[#162545]/70 border border-[#333f59] focus:border-[#7ec8ff] text-white placeholder-slate-500 rounded-lg pl-9 pr-4 py-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
        />
      </div>

      <!-- Category Filter -->
      <div class="md:col-span-4">
        <select
          v-model="selectedCategory"
          class="w-full bg-[#162545]/70 border border-[#333f59] focus:border-[#7ec8ff] text-slate-200 rounded-lg px-3 py-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
        >
          <option value="ALL">Toutes les catégories Web</option>
          <option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat }}
          </option>
        </select>
      </div>

      <!-- Stats Pill -->
      <div class="md:col-span-2 text-right">
        <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#162545] border border-[#333f59] text-xs font-mono text-slate-300">
          <span class="text-[#7ec8ff] font-bold">{{ filteredChallenges.length }}</span> défis
        </span>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 3. TABLEAU DE GESTION DES DÉFIS            -->
    <!-- ========================================== -->
    <div class="relative bg-[#162545]/40 border border-[#333f59] rounded-xl overflow-hidden backdrop-blur-sm">
      <!-- Tech Corner Brackets -->
      <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
      <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
      <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
      <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

      <div class="overflow-x-auto">
        <table class="w-full text-left font-rajdhani border-collapse">
          <thead>
            <tr class="border-b border-[#333f59] text-xs font-bold uppercase tracking-wider text-slate-400 bg-[#0a1a2f]/60">
              <th class="py-3.5 px-4">Titre du Défi</th>
              <th class="py-3.5 px-4">Catégorie</th>
              <th class="py-3.5 px-4 text-center">Difficulté</th>
              <th class="py-3.5 px-4 text-center">Points</th>
              <th class="py-3.5 px-4">Image Docker (VM 2)</th>
              <th class="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#333f59]/40 text-sm">
            <tr
              v-for="chal in filteredChallenges"
              :key="chal.id"
              class="hover:bg-[#162545]/70 transition-colors"
            >
              <!-- Title & ID -->
              <td class="py-3.5 px-4">
                <div class="font-bold text-white font-mono text-xs sm:text-sm">
                  {{ chal.title }}
                </div>
                <div class="text-[10px] font-mono text-slate-500">
                  ID: {{ chal.id }}
                </div>
              </td>

              <!-- Category -->
              <td class="py-3.5 px-4">
                <span class="px-2 py-0.5 rounded border text-[11px] font-mono" :class="chal.badgeColor || 'text-blue-400 bg-blue-500/10 border-blue-500/30'">
                  {{ chal.category }}
                </span>
              </td>

              <!-- Difficulty -->
              <td class="py-3.5 px-4 text-center text-[#ffcc00] font-mono text-xs font-bold">
                <span class="tracking-widest">
                  <template v-for="star in 5" :key="star">
                    {{ star <= chal.difficulty ? '★' : '☆' }}
                  </template>
                </span>
              </td>

              <!-- Points -->
              <td class="py-3.5 px-4 text-center font-mono font-bold text-[#7ec8ff]">
                {{ chal.points }} pts
              </td>

              <!-- Docker Image with Whitelist Badge -->
              <td class="py-3.5 px-4">
                <div class="flex items-center gap-1.5 font-mono text-xs">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <code class="px-2 py-0.5 rounded bg-[#0a1a2f] border border-[#333f59] text-emerald-400 font-bold">
                    {{ chal.dockerImage || `ctf/${chal.id}:1.0` }}
                  </code>
                </div>
              </td>

              <!-- Actions (Edit & Delete) -->
              <td class="py-3.5 px-4 text-right">
                <div class="flex items-center justify-end gap-2 font-rajdhani text-xs font-bold uppercase">
                  <!-- Edit Button -->
                  <button
                    type="button"
                    class="px-2.5 py-1 rounded border border-[#333f59] bg-[#0a1a2f] hover:border-[#7ec8ff] text-slate-300 hover:text-[#7ec8ff] transition-all cursor-pointer"
                    title="Modifier ce défi"
                    @click="openEditModal(chal)"
                  >
                    Éditer
                  </button>

                  <!-- Delete Button -->
                  <button
                    type="button"
                    class="px-2.5 py-1 rounded border border-[#ff3e3e]/40 bg-[#ff3e3e]/10 hover:bg-[#ff3e3e]/20 text-[#ff3e3e] transition-all cursor-pointer"
                    title="Supprimer ce défi"
                    @click="promptDelete(chal)"
                  >
                    Supprimer
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="filteredChallenges.length === 0">
              <td colspan="6" class="py-12 text-center text-slate-500 font-mono text-xs">
                Aucun défi ne correspond aux critères de recherche.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 4. MODAL FORM: CRÉATION / ÉDITION          -->
    <!-- ========================================== -->
    <div
      v-if="isModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto"
    >
      <div class="relative w-full max-w-2xl bg-[#162545] border-2 border-[#333f59] rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6 my-8 font-inter">
        <!-- Tech Corner Accents -->
        <span class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white pointer-events-none"></span>
        <span class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white pointer-events-none"></span>
        <span class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white pointer-events-none"></span>
        <span class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white pointer-events-none"></span>

        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-[#333f59]/60 pb-4">
          <div class="space-y-1">
            <span class="text-[10px] font-mono text-[#7ec8ff] uppercase tracking-wider">
              {{ isEditMode ? 'MODIFICATION DE DÉFI' : 'CRÉATION DE NOUVEAU CONTENEUR' }}
            </span>
            <h2 class="text-xl font-black uppercase text-white font-inter">
              {{ isEditMode ? `Éditer : ${formData.title}` : 'Configurer un Défi Web HTTPS' }}
            </h2>
          </div>
          <button
            type="button"
            class="text-slate-400 hover:text-white p-1 rounded transition-colors"
            @click="isModalOpen = false"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form Body -->
        <form class="space-y-4 text-xs font-mono" @submit.prevent="handleSubmit">
          <!-- Row 1: Title & Category -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="block text-slate-300 uppercase tracking-wider font-bold">
                Titre du Défi *
              </label>
              <input
                v-model="formData.title"
                type="text"
                placeholder="ex: XSS Reflected via Search"
                class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
              />
              <span v-if="formErrors.title" class="text-[#ff3e3e] text-[10px]">
                {{ formErrors.title }}
              </span>
            </div>

            <div class="space-y-1">
              <label class="block text-slate-300 uppercase tracking-wider font-bold">
                Catégorie Web *
              </label>
              <select
                v-model="formData.category"
                class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
              >
                <option v-for="cat in categories" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
            </div>
          </div>

          <!-- Row 2: Difficulty & Points -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="block text-slate-300 uppercase tracking-wider font-bold">
                Difficulté (1 à 5 étoiles)
              </label>
              <select
                v-model.number="formData.difficulty"
                class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-[#ffcc00] font-bold px-3 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
              >
                <option :value="1">★☆☆☆☆ (1 - Débutant)</option>
                <option :value="2">★★☆☆☆ (2 - Facile)</option>
                <option :value="3">★★★☆☆ (3 - Intermédiaire)</option>
                <option :value="4">★★★★☆ (4 - Avancé)</option>
                <option :value="5">★★★★★ (5 - Expert)</option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="block text-slate-300 uppercase tracking-wider font-bold">
                Points attribués *
              </label>
              <input
                v-model.number="formData.points"
                type="number"
                min="5"
                max="500"
                step="5"
                class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
              />
              <span v-if="formErrors.points" class="text-[#ff3e3e] text-[10px]">
                {{ formErrors.points }}
              </span>
            </div>
          </div>

          <!-- Technical Description -->
          <div class="space-y-1">
            <label class="block text-slate-300 uppercase tracking-wider font-bold">
              Description Technique (Scénario, Vulnérabilité, Indices) *
            </label>
            <textarea
              v-model="formData.description"
              rows="4"
              placeholder="Expliquez le contexte technique, la cible, et les contraintes sans donner directement la solution..."
              class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all font-inter text-xs leading-relaxed"
            ></textarea>
            <span v-if="formErrors.description" class="text-[#ff3e3e] text-[10px]">
              {{ formErrors.description }}
            </span>
          </div>

          <!-- Flag Solution -->
          <div class="space-y-1">
            <div class="flex items-center justify-between">
              <label class="block text-slate-300 uppercase tracking-wider font-bold">
                Flag Secret Validant *
              </label>
              <span class="text-[10px] text-slate-500">Format strict: CTF{...}</span>
            </div>
            <input
              v-model="formData.flag"
              type="text"
              placeholder="CTF{example_flag_here}"
              class="w-full bg-[#0a1a2f] border border-[#333f59] focus:border-[#7ec8ff] text-[#7ec8ff] font-bold px-3 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
            />
            <span v-if="formErrors.flag" class="text-[#ff3e3e] text-[10px]">
              {{ formErrors.flag }}
            </span>
          </div>

          <!-- DOCKER IMAGE WITH STRICT WHITELIST RULE -->
          <div class="space-y-1 p-3.5 bg-[#0a1a2f] border-2 rounded-xl" :class="formErrors.dockerImage ? 'border-[#ff3e3e]' : 'border-[#333f59]'">
            <div class="flex items-center justify-between">
              <label class="block text-slate-200 uppercase tracking-wider font-bold flex items-center gap-2">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span>Image Docker (Whitelist Orchestrateur VM 2) *</span>
              </label>
              <span class="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                OBLIGATOIRE: ctf/*
              </span>
            </div>

            <input
              v-model="formData.dockerImage"
              type="text"
              placeholder="ctf/nom-du-defi:1.0"
              class="w-full bg-[#162545] border border-[#333f59] focus:border-[#7ec8ff] text-emerald-300 font-bold px-3 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#7ec8ff] transition-all"
            />

            <!-- Error message if whitelist rule violated -->
            <p v-if="formErrors.dockerImage" class="text-[#ff3e3e] text-[11px] font-semibold mt-1 flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ formErrors.dockerImage }}</span>
            </p>
            <p v-else class="text-[10px] text-slate-400 mt-0.5">
              L'orchestrateur Docker Swarm rejette tout conteneur ne démarrant pas par le préfixe <code class="text-white">ctf/</code>.
            </p>
          </div>

          <!-- Modal Actions -->
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-[#333f59]/60 font-rajdhani font-bold text-xs uppercase tracking-wider">
            <button
              type="button"
              class="px-4 py-2.5 rounded-lg border border-[#333f59] bg-[#0a1a2f] text-slate-300 hover:text-white transition-colors cursor-pointer"
              @click="isModalOpen = false"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="px-6 py-2.5 rounded-lg bg-gradient-to-r from-[#004e7a] to-[#7ec8ff] text-white hover:opacity-90 transition-all shadow-lg shadow-[#004e7a]/30 cursor-pointer disabled:opacity-50"
            >
              {{ isSubmitting ? 'Traitement...' : (isEditMode ? 'Mettre à jour' : 'Enregistrer le Défi') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 5. MODAL CONFIRMATION SUPPRESSION          -->
    <!-- ========================================== -->
    <div
      v-if="isDeleteConfirmOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
    >
      <div class="relative w-full max-w-md bg-[#162545] border-2 border-[#ff3e3e] rounded-2xl p-6 shadow-2xl space-y-4 font-inter text-center">
        <div class="w-12 h-12 rounded-full bg-[#ff3e3e]/20 border border-[#ff3e3e]/50 flex items-center justify-center mx-auto text-[#ff3e3e]">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </div>

        <h3 class="text-lg font-black uppercase text-white font-inter">
          Confirmer la suppression
        </h3>

        <p class="text-xs text-slate-300 font-mono">
          Êtes-vous sûr de vouloir supprimer définitivement le défi
          <span class="text-[#ff3e3e] font-bold">"{{ challengeToDelete?.title }}"</span> ?
          Cette action désinstanciera les conteneurs associés.
        </p>

        <div class="flex items-center justify-center gap-3 pt-3 font-rajdhani font-bold text-xs uppercase tracking-wider">
          <button
            type="button"
            class="px-4 py-2 rounded-lg border border-[#333f59] bg-[#0a1a2f] text-slate-300 hover:text-white transition-colors cursor-pointer"
            @click="isDeleteConfirmOpen = false"
          >
            Annuler
          </button>
          <button
            type="button"
            class="px-5 py-2 rounded-lg bg-[#ff3e3e] hover:bg-[#ff3e3e]/90 text-white transition-colors cursor-pointer shadow-lg shadow-[#ff3e3e]/30"
            @click="confirmDelete"
          >
            Supprimer Définitivement
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
