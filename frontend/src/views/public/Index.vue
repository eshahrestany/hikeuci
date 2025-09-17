<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

import NavBar from '../../components/public/Navbar.vue'
import Hero from '../../components/public/Hero.vue'
import About from '../../components/public/AboutSection.vue'
import MembershipInfo from '../../components/public/MembershipInfo.vue'
import Leadership from '../../components/public/Leadership.vue'
import Footer from '../../components/public/Footer.vue'

import bg from '@/assets/bg.jpg'

// Parallax offset for desktop
const parallaxY = ref(0)
// Tune this: more negative = stronger effect
const PARALLAX_FACTOR = -0.18

function onScroll() {
  const y = window.scrollY || document.documentElement.scrollTop || 0
  parallaxY.value = y * PARALLAX_FACTOR
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
      <NavBar :overlay-navbar="true" />
      <Hero />
      <About />
      <MembershipInfo />
      <Leadership />
      <Footer />
    </div>
  </main>
</template>
