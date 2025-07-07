<template>
  <NavBar />
  <section class="min-h-[calc(100vh-8rem)] bg-stone/50 text-midnight flex flex-col items-center py-20 px-4">
    <div class="max-w-5xl w-full">
      <h1 class="text-4xl font-bold font-montserrat text-uci-gold drop-shadow-md mb-6">Member Portal</h1>

      <div class="bg-black/60 backdrop-blur p-6 rounded-lg shadow-lg border border-stone/30 text-stone">
        <p class="mb-4">Welcome, <span class="font-semibold text-uci-blue">{{ authState.user?.name }}</span>!</p>

        <p class="mb-8">This is a placeholder for the member portal content. Replace this section with upcoming events, member-only resources, and more.</p>

        <button
          @click="signOutAndReturn"
          class="inline-flex items-center px-4 py-2 bg-uci-blue hover:bg-uci-blue/80 text-white rounded-lg transition-colors"
        >
          Sign Out
        </button>
      </div>
    </div>
  </section>
  <Footer />
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../lib/auth.js'
import NavBar from "../components/Navbar.vue"
import Footer from "../components/Footer.vue"

const router = useRouter()
const { state: authState, signOut } = useAuth()

function signOutAndReturn() {
  signOut()
  router.replace('/login')
}
</script>

<style scoped>
/***** Relying on Tailwind for styling *****/
</style> 