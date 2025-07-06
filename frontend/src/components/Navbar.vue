<template>
  <nav class="bg-midnight text-stone shadow-md font-montserrat">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex justify-between h-16 items-center">
        <!-- Site / brand name -->
        <a href="/" class="text-uci-gold font-semibold text-xl tracking-wide hover:text-uci-blue transition-colors">Hiking Club @ UCI</a>

        <!-- Mobile menu toggle -->
        <button
          @click="open = !open"
          aria-label="Toggle navigation"
          class="md:hidden focus:outline-none focus:ring-2 focus:ring-uci-gold rounded-lg p-2"
        >
          <svg v-if="!open" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
          <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        <!-- Desktop nav -->
        <ul class="hidden md:flex space-x-8">
          <li v-for="item in items" :key="item.name">
            <a
              :href="item.href"
              :class="navLinkClasses(item)"
            >
              {{ item.name }}
            </a>
          </li>
        </ul>
      </div>

      <!-- Mobile nav -->
      <transition name="fade-slide">
        <ul
          v-if="open"
          class="md:hidden mt-2 space-y-2 pb-4 border-t border-stone/40"
        >
          <li v-for="item in items" :key="item.name">
            <a
              :href="item.href"
              :class="mobileNavLinkClasses(item)"
            >
              {{ item.name }}
            </a>
          </li>
        </ul>
      </transition>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';

// Navigation items; easier to modify centrally
const items = [
  { name: 'Home',            href: '/' },
  { name: 'About Us',        href: '/about' },
  { name: 'Leadership Team', href: '/leadership' },
  { name: 'Useful Links',    href: '/links' },
  { name: 'Login',           href: '/login' },
];

// Mobile menu state
const open = ref(false);

// Current route information
const route = useRoute();

/**
 * Utility: classes for desktop links
 */
function navLinkClasses(item: { href: string }) {
  const base = 'font-medium transition-colors duration-200';
  const active = 'text-white drop-shadow-[0_0_6px_#ffffff]';
  const inactive = 'hover:text-uci-gold';
  return [base, route.path === item.href ? active : inactive].join(' ');
}

/**
 * Utility: classes for mobile links
 */
function mobileNavLinkClasses(item: { href: string }) {
  const base = 'block w-full py-2 px-4 rounded-lg transition-colors duration-200';
  const active = 'text-white drop-shadow-[0_0_6px_#ffffff]';
  const inactive = 'hover:bg-uci-blue/20 hover:text-uci-gold';
  return [base, route.path === item.href ? active : inactive].join(' ');
}
</script>
