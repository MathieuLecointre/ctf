<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <footer class="w-full bg-[#0a1a2f] border-t border-[#333f59]/60 text-slate-300 font-inter pt-12 pb-6 mt-16">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 4 Columns Grid -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
        <!-- Col 1: Brand Info -->
        <div class="space-y-3">
          <div class="flex items-center space-x-1.5 select-none">
            <span class="text-xl font-black text-white font-inter">CTF</span>
            <span class="text-xl font-black text-[#ff3e3e] font-inter">UPJV</span>
          </div>
          <p class="text-xs text-slate-400 leading-relaxed max-w-xs">
            Plateforme d'entraînement en cybersécurité offensive. Apprends en cassant — éthiquement, gratuitement, depuis 2026.
          </p>
        </div>

        <!-- Col 2: Plateforme -->
        <div>
          <h4 class="text-xs font-bold text-white uppercase tracking-wider mb-3 font-rajdhani">
            Plateforme
          </h4>
          <ul class="space-y-2 text-xs text-slate-400">
            <li>
              <RouterLink to="/challenges" class="hover:text-[#7ec8ff] transition-colors">Défis</RouterLink>
            </li>
            <li>
              <RouterLink to="/scoreboard" class="hover:text-[#7ec8ff] transition-colors">Classement</RouterLink>
            </li>
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Badges</a></li>
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Événements</a></li>
          </ul>
        </div>

        <!-- Col 3: Ressources -->
        <div>
          <h4 class="text-xs font-bold text-white uppercase tracking-wider mb-3 font-rajdhani">
            Ressources
          </h4>
          <ul class="space-y-2 text-xs text-slate-400">
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Documentation</a></li>
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Tutoriels</a></li>
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Glossaire</a></li>
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Outils recommandés</a></li>
          </ul>
        </div>

        <!-- Col 4: Communauté -->
        <div>
          <h4 class="text-xs font-bold text-white uppercase tracking-wider mb-3 font-rajdhani">
            Communauté
          </h4>
          <ul class="space-y-2 text-xs text-slate-400">
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Discord</a></li>
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Forum</a></li>
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Code de conduite</a></li>
            <li><a href="#" class="hover:text-[#7ec8ff] transition-colors">Contact</a></li>
          </ul>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-[#333f59]/40 pt-4 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 font-mono gap-2">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-[#7ec8ff] animate-pulse"></span>
          <span>TOUS LES SYSTÈMES OPÉRATIONNELS</span>
        </div>
        <div class="flex items-center gap-2">
          <span>CTF UPJV © 2026</span>
          <span class="text-[#ff3e3e] font-bold">|</span>
        </div>
      </div>
    </div>
  </footer>
</template>
