<template>
  <NavBar :overlayNavbar="true"/>
  <section class="relative min-h-screen flex items-center justify-center text-stone overflow-hidden px-4">
    <!-- Background image -->
    <div class="absolute inset-0 bg-cover bg-center" :style="{ backgroundImage: `url(${background})` }" aria-hidden="true"></div>
    <!-- Overlay for readability -->
    <div class="absolute inset-0 bg-black/50 pointer-events-none" aria-hidden="true"></div>

    <div class="relative z-10 w-full max-w-md bg-black/30 backdrop-blur p-8 rounded-lg shadow-lg border border-stone/30">
      <h1 class="text-3xl font-bold font-montserrat text-uci-gold mb-6 text-center">Member Portal Sign-In</h1>

      <!-- Google button placeholder -->
      <div id="g_id_signin" class="flex justify-center"></div>

      <p v-if="error" class="mt-4 text-red-400 text-center">{{ error }}</p>
    </div>
  </section>
  <Footer />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../lib/auth.js'
import NavBar from "../components/Navbar.vue"
import Footer from "../components/Footer.vue"

// Background photo reused from Hero component
import background from "../assets/hiking_bg.jpg"

const router = useRouter()
const { setUser } = useAuth()
const error = ref(null)

function decodeJwt(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload
  } catch (e) {
    return null
  }
}

function handleCredentialResponse(response) {
  const payload = decodeJwt(response.credential)
  if (!payload || !payload.email) {
    error.value = 'Invalid Google response. Please try again.'
    return
  }

  if (!payload.email.endsWith('@uci.edu')) {
    error.value = 'Please sign in with your uci.edu account.'
    return
  }

  // Store minimal user info. A production app should verify the token server-side.
  setUser({
    email: payload.email,
    name: payload.name,
    picture: payload.picture,
    idToken: response.credential,
  })

  router.replace('/portal')
}

onMounted(() => {
  // Google script should already be loaded via index.html. Wait until it exists.
  const interval = setInterval(() => {
    // eslint-disable-next-line no-undef
    if (window.google && window.google.accounts && window.google.accounts.id) {
      clearInterval(interval)
      // eslint-disable-next-line no-undef
      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        hd: 'uci.edu',
        prompt: 'select_account',
        callback: handleCredentialResponse,
      })
      // eslint-disable-next-line no-undef
      window.google.accounts.id.renderButton(
        document.getElementById('g_id_signin'),
        { theme: 'outline', size: 'large', width: 280 }
      )
    }
  }, 200)
})
</script>

<style scoped>
/***** No additional styles needed: relying on Tailwind *****/
</style> 