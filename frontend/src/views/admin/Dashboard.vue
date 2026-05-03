<template>
  <div class="hidden"><ThemeToggle/></div>
  <section class="p-4 md:p-6">
    <Card class="max-w-4xl mx-auto">
      <CardHeader class="pb-3">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Mountain class="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle class="text-xl">Current Hike</CardTitle>
            <p class="text-xs text-muted-foreground mt-0.5">Live hike management</p>
          </div>
          <div v-if="response.status && response.status !== 'error'" class="ml-auto">
            <Badge
              v-if="response.status === 'voting'" variant="default"
              class="bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30 border">
              Voting
            </Badge>
            <Badge
              v-else-if="response.status === 'signup'" variant="default"
              class="bg-green-600/15 text-green-700 dark:text-green-400 border-green-600/30 border">
              Signup
            </Badge>
            <Badge
              v-else-if="response.status === 'waiver'" variant="default"
              class="bg-green-500/15 text-green-700 dark:text-green-400 border-green-500/30 border">
              Waiver
            </Badge>
            <Badge
              v-else-if="response.status === 'awaiting_vote_start'" variant="outline"
              class="text-muted-foreground">
              Scheduled
            </Badge>
          </div>
        </div>
      </CardHeader>
      <hr class="h-px mx-6 bg-border border-0"/>
      <CardContent class="pt-5">
        <ActiveHikeTimeline
          v-if="response.status ==='awaiting_vote_start' || response.status ==='voting' || response.status === 'signup' || response.status === 'waiver'"
          class="mb-6"
          :has-vote="response.has_vote"
          :current-phase="response.phase"
          :timestamps="response.timeline"
        />

        <div v-if="loading" class="space-y-3">
          <Skeleton class="h-6 w-3/5"/>
          <Skeleton class="h-4 w-full"/>
          <Skeleton class="h-4 w-4/5"/>
          <Skeleton class="h-4 w-2/3"/>
        </div>
        <div v-else-if="response.status === 'awaiting_vote_start'" class="rounded-lg bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
          Hike scheduled — voting begins at {{ response.vote_start }}
        </div>
        <div v-else-if="response.status === 'error'" class="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive font-medium">
          Could not fetch hike data from the server
        </div>

        <div v-else-if="response.status === null"><SetHikePanel @hike-scheduled="loadUpcoming"/></div>
        <VotingPhase v-else-if="response.status === 'voting'" :voting-data="response"/>
        <SignupPhase v-else-if="response.status === 'signup'" :signup-data="response" @refresh="silentRefresh"/>
        <WaiverPhase v-else-if="response.status === 'waiver'" :waiver-data="response" @refresh="silentRefresh"/>

        <!-- Danger Zone pinned to the bottom -->
        <div
          v-if="['voting','signup','waiver'].includes(response.status)"
          class="mt-8 pt-5 border-t border-border/60 flex justify-end"
        >
          <DangerZoneDrawer
            :phase="response.status"
            :candidates="response.trails"
            :current-trail-id="response.trail_id"
            @swapped="loadUpcoming"
            @switched="loadUpcoming"
            @cancelled="loadUpcoming"
          />
        </div>
      </CardContent>
    </Card>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '@/lib/auth.js'
import { useRealtime } from '@/lib/realtime.js'
import { Mountain } from 'lucide-vue-next'

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import ActiveHikeTimeline from '@/components/admin/ActiveHikeTimeline.vue'
import SetHikePanel from '@/components/admin/SetHikePanel.vue'
import VotingPhase from "@/components/admin/VotingPhase.vue"
import SignupPhase from "@/components/admin/SignupPhase.vue"
import WaiverPhase from "@/components/admin/WaiverPhase.vue"
import DangerZoneDrawer from "@/components/admin/DangerZoneDrawer.vue"
import ThemeToggle from "@/components/admin/ThemeToggle.vue"

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

async function silentRefresh() {
  try {
    const res = await fetchWithAuth('/api/admin/upcoming')
    if (res.ok) response.value = await res.json()
  } catch {}
}

// Surgical patch handlers — mutate only the affected user in place so
// SignupTable rows and SignupStats update reactively without a full reload.
// Null data (backfill on reconnect / tab-regain) falls back to silentRefresh
// so the page does not flash a skeleton.
function patchCheckin(data) {
  if (!data) { silentRefresh(); return }
  const user = response.value?.users?.find(u => u.member_id === data.member_id)
  if (user) user.is_checked_in = data.is_checked_in
}

function patchWaiver(data) {
  if (!data) { silentRefresh(); return }
  const user = response.value?.users?.find(u => u.member_id === data.member_id)
  if (user) user.has_waiver = true
}

async function patchVotes() {
  try {
    const res = await fetchWithAuth('/api/admin/vote-counts')
    if (!res.ok) { silentRefresh(); return }
    const data = await res.json()
    if (!data?.trails || !response.value?.trails) { silentRefresh(); return }
    for (const patch of data.trails) {
      const trail = response.value.trails.find(t => t.trail_id === patch.trail_id)
      if (trail) {
        trail.trail_num_votes = patch.trail_num_votes
        trail.trail_voters = patch.trail_voters
      }
    }
  } catch {
    silentRefresh()
  }
}

const topics = computed(() => response.value?.hike_id ? [`hike:${response.value.hike_id}`] : [])
useRealtime(topics, {
  phase_changed:   () => silentRefresh(),
  roster_updated:  () => silentRefresh(),
  vote_updated:    () => patchVotes(),
  checkin_updated: (data) => patchCheckin(data),
  waiver_updated:  (data) => patchWaiver(data),
})

onMounted(loadUpcoming)
</script>
