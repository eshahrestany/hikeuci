<template>
  <nav :class="['w-full text-stone shadow-md font-montserrat bg-midnight']">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex justify-between h-16 items-center">
        <router-link to="/" class="text-uci-gold font-semibold text-xl tracking-wide hover:text-uci-blue transition-colors">
          Hiking Club @ UCI
        </router-link>

        <button
          @click="open = !open"
          :aria-expanded="open"
          aria-label="Toggle navigation"
          aria-controls="mobile-nav"
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

        <ul class="hidden md:flex space-x-8">
          <li v-for="item in items" :key="item.name">
            <router-link
              :to="item.href"
              :class="navLinkClasses(item)"
              @click="open = false"
            >
              {{ item.name }}
            </router-link>
          </li>
        </ul>
      </div>

      <transition name="fade-slide">
        <ul
          v-if="open"
          id="mobile-nav"
          class="md:hidden mt-2 space-y-2 pb-4 border-t border-stone/40"
        >
          <li v-for="item in items" :key="item.name">
            <router-link
              :to="item.href"
              :class="mobileNavLinkClasses(item)"
              @click="open = false"
            >
              {{ item.name }}
            </router-link>
          </li>
        </ul>
      </transition>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  overlayNavbar: {
    type: Boolean,
    default: false,
  },
})

const items = [
  { name: 'Home',       href: '/' },
  { name: 'Officer Login',      href: '/login' },
]

const open = ref(false)
const route = useRoute()

type NavItem = { href: string }

function isActive(item: NavItem) {
  if (item.href.includes('#')) {
    const [, hash] = item.href.split('#')
    return route.path === '/' && route.hash === `#${hash}`
  }
  return route.path === item.href
}

function navLinkClasses(item: NavItem) {
  const base = 'font-medium transition-colors duration-200'
  // Active: gold text with underline to indicate current page
  const active = 'text-uci-gold underline underline-offset-4'
  const inactive = 'hover:text-uci-gold'
  return [base, isActive(item) ? active : inactive].join(' ')
}

function mobileNavLinkClasses(item: NavItem) {
  const base = 'block w-full py-2 px-4 rounded-lg transition-colors duration-200'
  // Active: gold text with subtle background highlight
  const active = 'text-uci-gold bg-uci-blue/10'
  const inactive = 'hover:bg-uci-blue/20 hover:text-uci-gold'
  return [base, isActive(item) ? active : inactive].join(' ')
}
</script>
