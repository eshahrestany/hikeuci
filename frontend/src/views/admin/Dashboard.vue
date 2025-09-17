<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarTrigger />
    <SidebarInset>
      <section class="p-6">
        <h1 class="text-3xl text-white font-bold mb-3">HikeUCI Dashboard</h1>
        <hr class="h-px mb-8 bg-gray-200 border-0 dark:bg-gray-700" />
        <Card class="max-w-4xl mx-auto space-y-6">
          <CardHeader>
            <CardTitle class="text-2xl">Upcoming Hike</CardTitle>
            <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
          </CardHeader>
          <CardContent>
            <ActiveHikeTimeline class="mb-6"
              v-if="response.status ==='awaiting_vote_start' || response.status ==='voting' || response.status === 'signup' || response.status === 'waiver'"
              :has-vote="response.has_vote"
              :current-phase="response.phase"
              :timestamps="response.timeline"
            />

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
            <div v-else-if="response.status === null">
              <SetHikePanel/>
            </div>

            <div v-else-if="response.status === 'awaiting_vote_start'" class="text-white">Hike set, awaiting vote start at {{ response.vote_start }}</div>

            <div v-else-if="response.status === 'error'" class="text-red-500">Could not fetch hike data from the server</div>

            <VotingPhase v-else-if="response.status === 'voting'" :voting-data="response"/>

            <SignupPhase v-else-if="response.status === 'signup'" :signup-data="response"/>

            <WaiverPhase v-else-if="response.status === 'waiver'" :waiver-data="response"/>

          </CardContent>
        </Card>
      </section>
    </SidebarInset>
  </SidebarProvider>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/lib/auth.js'

import AppSidebar from '@/components/admin/AppSidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar/index.js'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/index.js'
import { Skeleton } from '@/components/ui/skeleton/index.js'
import ActiveHikeTimeline from '@/components/admin/ActiveHikeTimeline.vue'
import SetHikePanel from '@/components/admin/SetHikePanel.vue'
import VotingPhase from "@/components/admin/VotingPhase.vue"
import SignupPhase from "@/components/admin/SignupPhase.vue"
import WaiverPhase from "@/components/admin/WaiverPhase.vue"


const { state: signOut, fetchWithAuth } = useAuth()
const router = useRouter()

const loading = ref(true)
const response = ref({ status: 'error', candidates: [], users: [], trail_id: null, trail_name: '' })

async function loadUpcoming() {
  loading.value = true
  try {
    const res = await fetchWithAuth('/api/admin/upcoming')
    response.value = await res.json()
  } catch {
    response.value = { status: 'error', candidates: [], users: [], trail_id: null, trail_name: '' }
  } finally {
    loading.value = false
  }
}

onMounted(loadUpcoming)

function signOutAndReturn() { signOut(); router.replace('/login') }

</script>
