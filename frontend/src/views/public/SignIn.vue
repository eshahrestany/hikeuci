<template>
  <NavBar :overlayNavbar="true"/>
  <section class="relative min-h-screen flex items-center justify-center text-stone overflow-hidden px-4">
    <div class="absolute inset-0 bg-cover bg-center" :style="{ backgroundImage: `url(${background})` }" aria-hidden="true"></div>
    <div class="absolute inset-0 bg-black/50 pointer-events-none" aria-hidden="true"></div>
    <div class="relative z-10 w-full max-w-md bg-black/30 backdrop-blur p-8 rounded-lg shadow-lg border border-stone/30">
      <h1 class="text-3xl font-bold font-montserrat text-uci-gold mb-2 text-center">Officer Sign-In</h1>
      <h1 class="text-md font-montserrat text-white mb-3 text-center">For hiking club officers only.</h1>
      <div id="g_id_signin" class="flex justify-center"></div>
      <p v-if="error" class="mt-4 text-red-400 text-center">{{ error }}</p>
    </div>
  </section>
  <Footer />
</template>

<script setup>
  import { onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '../../lib/auth.js'
  import NavBar from "../../components/public/Navbar.vue"
  import Footer from "../../components/public/Footer.vue"
  import background from "../../assets/hiking_bg.jpg"

  const router = useRouter()
  const { state, setUser } = useAuth()
  const error = ref(null)

  async function handleCredentialResponse(response) {
    try {
      // 1) Send the Google ID token to the backend
      const res = await fetch(`/api/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken: response.credential })
      })
      const body = await res.json()

      if (!res.ok) {
        // backend will send { error: "..." }
        throw new Error(body.error || 'Authentication failed')
      }

      // 2) Backend sent back JWT
      setUser({ token: body.token })

      console.log('✅ Logged in, user state is now:', state.user)
      router.replace('/admin')
    }
    catch (err) {
      console.error(err)
      error.value = err.message
    }
  }

  onMounted(() => {
    const interval = setInterval(() => {
      if (window.google?.accounts?.id) {
        clearInterval(interval)
        window.google.accounts.id.initialize({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          prompt: 'select_account',
          callback: handleCredentialResponse,
        })
        window.google.accounts.id.renderButton(
          document.getElementById('g_id_signin'),
          { theme: 'outline', size: 'large', width: 280 }
        )
      }
    }, 200)
  })
</script>

<style scoped>

</style> 