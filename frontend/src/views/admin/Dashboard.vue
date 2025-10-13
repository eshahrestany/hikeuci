<template>
  <section class="px-0 py-4 sm:p-6 overflow-x-hidden">
    <Card class="max-w-4xl mx-auto md:space-y-6 border-0 sm:border-1">
      <CardHeader class="flex items-center">
        <CardTitle class="text-2xl">Upcoming Hike</CardTitle>
        <Button size="sm" class="ml-auto" @click="loadUpcoming"><RefreshCcw/>Refresh data</Button>
      </CardHeader>
      <hr class="h-px mx-6 bg-gray-200 border-0 dark:bg-gray-700"/>
      <CardContent>
        <ActiveHikeTimeline
          v-if="response.status ==='awaiting_vote_start' || response.status ==='voting' || response.status === 'signup' || response.status === 'waiver'"
          class="mb-6"
          :has-vote="response.has_vote"
          :current-phase="response.phase"
          :timestamps="response.timeline"
        />

        <!-- special/error content -->
        <div v-if="loading">
          <Skeleton class="h-6 w-3/5 mb-4"/>
          <Skeleton class="space-y-2">
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-4/5"/>
            <Skeleton class="h-4 w-2/3"/>
          </Skeleton>
        </div>
        <div v-else-if="response.status === 'awaiting_vote_start'" class="text-white">Hike set, awaiting vote start at {{ response.vote_start }}</div>
        <div v-else-if="response.status === 'error'" class="text-red-500">Could not fetch hike data from the server</div>

        <!-- hike phase-specific content -->
        <div v-else-if="response.status === null"><SetHikePanel/></div>
        <VotingPhase v-else-if="response.status === 'voting'" :voting-data="response"/>
        <SignupPhase v-else-if="response.status === 'signup'" :signup-data="response"/>
        <WaiverPhase v-else-if="response.status === 'waiver'" :waiver-data="response"/>
      </CardContent>
    </Card>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/lib/auth.js'

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import ActiveHikeTimeline from '@/components/admin/ActiveHikeTimeline.vue'
import SetHikePanel from '@/components/admin/SetHikePanel.vue'
import VotingPhase from "@/components/admin/VotingPhase.vue"
import SignupPhase from "@/components/admin/SignupPhase.vue"
import WaiverPhase from "@/components/admin/WaiverPhase.vue"
import {RefreshCcw} from 'lucide-vue-next'


const { fetchWithAuth } = useAuth()

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

</script>
