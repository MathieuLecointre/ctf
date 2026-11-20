<script setup>
import { useNotificationStore } from '../stores/notificationStore'

const notifStore = useNotificationStore()
</script>

<template>
  <div class="fixed bottom-5 right-5 z-50 max-w-sm w-full pointer-events-none px-4 sm:px-0">
    <Transition
      enter-active-class="transform transition ease-out duration-300"
      enter-from-class="translate-y-4 opacity-0 scale-95"
      enter-to-class="translate-y-0 opacity-100 scale-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="notifStore.activeToast"
        :class="[
          notifStore.activeToast.category === 'FIRST_BLOOD'
            ? 'border-[#ff3e3e] shadow-[#ff3e3e]/20'
            : 'border-[#7ec8ff] shadow-[#7ec8ff]/20',
          'pointer-events-auto relative bg-[#162545]/95 border-2 rounded-xl p-4 shadow-2xl backdrop-blur-md font-inter space-y-2'
        ]"
      >
        <!-- Tech Corner Accents -->
        <span class="absolute top-0 left-0 w-2 h-2 border-t border-l border-white pointer-events-none"></span>
        <span class="absolute top-0 right-0 w-2 h-2 border-t border-r border-white pointer-events-none"></span>
        <span class="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white pointer-events-none"></span>
        <span class="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-white pointer-events-none"></span>

        <!-- Header: Title & Close -->
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <span
              :class="[
                notifStore.activeToast.category === 'FIRST_BLOOD'
                  ? 'bg-[#ff3e3e]'
                  : 'bg-[#7ec8ff]',
                'w-2 h-2 rounded-full animate-ping'
              ]"
            ></span>
            <span
              :class="[
                notifStore.activeToast.category === 'FIRST_BLOOD'
                  ? 'text-[#ff3e3e]'
                  : 'text-[#7ec8ff]',
                'text-xs font-black uppercase tracking-wider font-rajdhani'
              ]"
            >
              {{ notifStore.activeToast.title }}
            </span>
          </div>

          <button
            type="button"
            class="text-slate-400 hover:text-white transition-colors cursor-pointer p-0.5"
            @click="notifStore.dismissToast"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Message Body -->
        <p class="text-xs text-slate-200 leading-relaxed font-mono">
          {{ notifStore.activeToast.message }}
        </p>

        <!-- Footer / Time -->
        <div class="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-[#333f59]/50">
          <span>LIVE FEED CTF</span>
          <span>{{ notifStore.activeToast.timestamp }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>
