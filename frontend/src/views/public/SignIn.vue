<template>
  <div class="public-layout">
    <NavBar :overlayNavbar="true"/>
    <section class="relative min-h-screen flex items-center justify-center overflow-hidden px-4">
      <div class="absolute inset-0 bg-cover bg-center" :style="{ backgroundImage: `url(${background})` }" aria-hidden="true"></div>
      <div class="pg-scrim" aria-hidden="true"></div>
      <div
        class="relative z-10 w-full max-w-md p-8 rounded-3xl border"
        style="
          background: rgba(8,16,34,0.45);
          backdrop-filter: blur(28px) saturate(1.5);
          -webkit-backdrop-filter: blur(28px) saturate(1.5);
          border-color: rgba(255,255,255,0.18);
          box-shadow: inset 0 1px 0 rgba(255,255,255,0.32), 0 30px 70px -20px rgba(0,0,0,0.65);
        "
      >
        <h1 class="text-3xl font-bold font-montserrat mb-2 text-center" style="color:#f5f7fb">Officer Sign-In</h1>
        <p class="text-sm font-montserrat mb-6 text-center" style="color:#c8d0de">For hiking club officers only.</p>
        <div id="g_id_signin" class="flex justify-center"></div>
        <p v-if="error" class="mt-4 text-red-400 text-center text-sm">{{ error }}</p>
      </div>
    </section>
    <Footer />
  </div>
</template>

<script setup>
  import { onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '../../lib/auth.js'
  import NavBar from "../../components/public/Navbar.vue"
  import Footer from "../../components/public/Footer.vue"
  import background from "../../assets/bg_2.jpg"

  const router = useRouter()
  const { state, setAuthFromResponse } = useAuth()
  const error = ref(null)

  async function handleCredentialResponse(response) {
    try {
      // 1) Send the Google ID token to the backend
      const res = await fetch(`/api/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken: response.credential })
      })
      const body = await res.json().catch(() => null)

      if (!res.ok) {
        throw new Error(body?.error || 'Server error when attempting to log in')
      }
      if (!body) {
        throw new Error('Server error when attempting to log in')
      }

      // 2) Backend sent back JWT + refresh token
      setAuthFromResponse(body)

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