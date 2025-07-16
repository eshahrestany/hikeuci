<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarTrigger />
    <SidebarInset>
      <section class="p-6">
        <Card class="max-w-xl mx-auto">
          <template #header>
            <CardHeader>
              <CardTitle>Upcoming Hike</CardTitle>
            </CardHeader>
          </template>
          <CardContent>
            <!-- Loading Skeleton -->
            <div v-if="loading">
              <Skeleton class="h-6 w-3/5 mb-4" />
              <Skeleton class="space-y-2">
                <Skeleton class="h-4 w-full" />
                <Skeleton class="h-4 w-4/5" />
                <Skeleton class="h-4 w-2/3" />
              </Skeleton>
            </div>

            <!-- No Upcoming Hike -->
            <div v-else-if="!upcoming">
              <p class="text-center text-sm text-gray-500 mb-4">No upcoming hikes found.</p>
              <Button variant="outline" class="block mx-auto">Set Next Hike</Button>
            </div>

            <!-- Upcoming Hike Display -->
            <div v-else>
              <p class="font-semibold text-lg">{{ upcoming.name }}</p>
              <p class="text-sm text-gray-600 mb-2">Date: {{ formatDate(upcoming.date) }}</p>
              <p class="text-sm mb-4">Phase: <span class="capitalize">{{ upcoming.phase }}</span></p>
              <!-- Placeholder for phase-specific UI -->
              <p class="text-xs text-gray-500">(UI for '{{ upcoming.phase }}' phase goes here)</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </SidebarInset>
  </SidebarProvider>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../lib/auth.js'

import AppSidebar from '@/components/AppSidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'

// API response spec:
// GET /api/upcoming
// Response: { upcoming: null } OR
//           { upcoming: { id: number; name: string; date: string (ISO 8601); phase: 'voting' | 'signup' | 'waiver' } }

const { state: authState, signOut, fetchWithAuth } = useAuth()
const router = useRouter()

const loading = ref(true)
const upcoming = ref(null)

function formatDate(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadUpcoming() {
  loading.value = true
  try {
    const res = await fetchWithAuth('/api/upcoming')
    if (!res.ok) throw new Error('Failed to fetch')
    const data = await res.json()
    upcoming.value = data.upcoming
  } catch (e) {
    console.error('Error loading upcoming hike:', e)
    upcoming.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUpcoming()
})

function signOutAndReturn() {
  signOut()
  router.replace('/login')
}
</script>

<style scoped>
/* Add any page-specific styling here */
</style>
