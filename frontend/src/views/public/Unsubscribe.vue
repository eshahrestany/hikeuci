<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const state = ref('loading') // 'loading' | 'success' | 'error'
const memberName = ref('')
const errorMessage = ref('')

onMounted(async () => {
  // route.query.token may be absent if QP-encoded `=3D` confused the URL parser;
  // fall back to parsing window.location.search directly.
  let token = route.query.token
  if (!token) {
    const raw = new URLSearchParams(window.location.search).get('token')
    token = raw || ''
  }
  // Strip leading QP artifact: `=3D` decodes to `=`, so `=3D1.hex` → `1.hex`
  if (token.startsWith('3D')) {
    token = token.slice(2)
  }
  if (!token) {
    state.value = 'error'
    errorMessage.value = 'Missing unsubscribe token. Please use the link from your email.'
    return
  }

  try {
    const res = await fetch('/api/unsubscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })
    const data = await res.json()
    if (res.ok && data.success) {
      memberName.value = data.name
      state.value = 'success'
    } else {
      state.value = 'error'
      errorMessage.value = data.error || 'Something went wrong. Please try again.'
    }
  } catch {
    state.value = 'error'
    errorMessage.value = 'Network error. Please check your connection and try again.'
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
      <div v-if="state === 'loading'" class="space-y-3">
        <div class="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
        <p class="text-gray-500 text-sm">Processing your request...</p>
      </div>

      <div v-else-if="state === 'success'" class="space-y-4">
        <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
          <svg class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 class="text-xl font-semibold text-gray-900">You've been unsubscribed</h1>
        <p class="text-gray-500 text-sm">
          Hi {{ memberName }}, you won't receive future Hiking Club at UCI emails.
        </p>
        <p class="text-gray-400 text-xs">
          Changed your mind? Email us at
          <a href="mailto:hikingclub@uci.edu" class="text-blue-500 underline">hikingclub@uci.edu</a>
          and we'll add you back.
        </p>
      </div>

      <div v-else class="space-y-4">
        <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto">
          <svg class="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h1 class="text-xl font-semibold text-gray-900">Unsubscribe failed</h1>
        <p class="text-gray-500 text-sm">{{ errorMessage }}</p>
        <p class="text-gray-400 text-xs">
          Need help? Contact us at
          <a href="mailto:hikingclub@uci.edu" class="text-blue-500 underline">hikingclub@uci.edu</a>
        </p>
      </div>
    </div>
  </div>
</template>
