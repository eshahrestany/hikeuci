<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

import NavBar from '../../components/public/Navbar.vue'
import Hero from '../../components/public/Hero.vue'
import About from '../../components/public/AboutSection.vue'
import MembershipInfo from '../../components/public/MembershipInfo.vue'
import Leadership from '../../components/public/Leadership.vue'
import Footer from '../../components/public/Footer.vue'
import {Button} from '@/components/ui/button'
import { ChevronDown } from 'lucide-vue-next'

import bg from '@/assets/bg.jpg'

// Parallax offset for desktop
const parallaxY = ref(0)
// Tune this: more negative = stronger effect
const PARALLAX_FACTOR = -0.18

const showScrollHint = ref(true)

function onScroll() {
  const y = window.scrollY || document.documentElement.scrollTop || 0
  parallaxY.value = y * PARALLAX_FACTOR
  updateHintVisibility()
}

function updateHintVisibility() {
  // show only when truly at the top
  showScrollHint.value = (window.scrollY || document.documentElement.scrollTop || 0) <= 2
}

function scrollSlightly() {
  window.scrollBy({
    top: Math.round(window.innerHeight * 0.3),
    left: 0,
    behavior: 'smooth',
  })
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<template>
  <main class="relative isolate overflow-hidden">
    <!-- Mobile: keep original fixed background -->
    <div
        class="absolute inset-0 md:hidden bg-fixed bg-cover bg-center"
        :style="`background-image:url(${bg});`"
        aria-hidden="true"
    />

    <!-- Desktop: real parallax via translateY -->
    <div class="hidden md:block absolute inset-0 overflow-hidden" aria-hidden="true">
      <img
          :src="bg"
          alt=""
          class="w-full min-h-[130%] object-cover will-change-transform select-none pointer-events-none"
          :style="`transform: translate3d(0, ${parallaxY}px, 0) scale(1.12);`"
      />
    </div>

    <!-- Content stays above background -->
    <div class="relative z-10">
      <NavBar/>
      <Hero />
      <About />
      <MembershipInfo />
      <Leadership />
      <Footer />
    </div>
  </main>

  <transition name="fade-down">
    <Button
        v-if="showScrollHint"
        @click="scrollSlightly"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 rounded-full
           bg-white/50 backdrop-blur px-4 py-3 shadow-lg hover:bg-white active:scale-95 transition"
    >
      <ChevronDown class="w-6 h-6" />
    </Button>
  </transition>
</template>
