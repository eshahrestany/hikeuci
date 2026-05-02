<script setup>
import {ref, computed, onMounted} from 'vue'
import {
  Card,
  CardContent,
  CardHeader
} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import backgroundImage from '@/assets/hiking_bg.jpg'
import {Skeleton} from '@/components/ui/skeleton'
import DifficultyBadge from "@/components/common/DifficultyBadge.vue";
import ElevationChart from "@/components/common/ElevationChart.vue";
import { Check } from 'lucide-vue-next'

/** ---------- State (mirrors SignupForm.vue patterns) ---------- */
const props = defineProps({
  title: {type: String, default: 'Trail Vote'},
})

const pageTitle = ref(props.title)
const loading = ref(true)
const error = ref(null)

const tokenRef = ref('')

const hikeName = ref('')
const endsAt = ref(null) // ISO string if provided
const trails = ref([])   // [{ id, name, location, length_km, est_time_min }, ...]
const counts = ref({})   // { [trailId]: number }
const totalVotes = ref(0)
const userVoteTrailId = ref(null) // null if hasn't voted yet

/** UI flags */
const voteSaved = ref(false)

/** ---------- Derived ---------- */
const alreadyVoted = computed(() => userVoteTrailId.value != null)

/** Format helpers */
function imageUrl(trailId) {
  return `/api/images/uploads/${trailId}`
}

function percentFor(trailId) {
  const t = totalVotes.value || 0
  if (!t) return 0
  const c = counts.value[trailId] || 0
  return Math.round((c / t) * 100)
}

function countFor(trailId) {
  return counts.value[trailId]
}
/** ---------- Fetch + Submit ---------- */
async function loadVote() {
  loading.value = true
  error.value = null
  voteSaved.value = false
  try {
    const res = await fetch(`/api/hike-vote?token=${tokenRef.value}`)
    if (!res.ok) {
      let msg = `HTTP error! status: ${res.status}`
      try {
        const j = await res.json()
        msg = j.error || msg
      } catch {
      }
      throw new Error(msg)
    }
    const data = await res.json()
    endsAt.value = data.ends_at || null
    hikeName.value = data.hike_name || ''
    trails.value = Array.isArray(data.trails) ? data.trails : []
    console.log(trails.value)
    counts.value = data.counts
    totalVotes.value = data.total_votes || Object.values(counts.value).reduce((a, b) => a + b, 0)
    userVoteTrailId.value = data.user_vote_trail_id ?? null
  } catch (e) {
    error.value = e.message || 'Failed to load vote'
  } finally {
    loading.value = false
  }
}

async function submitVote(trailId) {
  try {
    error.value = null
    const res = await fetch(`/api/hike-vote?token=${tokenRef.value}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({trail_id: trailId})
    })
    if (!res.ok) {
      let msg = `HTTP error! status: ${res.status}`
      try {
        const j = await res.json()
        msg = j.error || msg
      } catch {
      }
      throw new Error(msg)
    }
    if (userVoteTrailId.value !== null) {
      // User is changing their vote, decrement old count
      counts.value[userVoteTrailId.value] = (counts.value[userVoteTrailId.value] || 1) - 1
    }
    // Increment new count
    counts.value[trailId] = (counts.value[trailId] || 0) + 1
    totalVotes.value += userVoteTrailId.value === null ? 1 : 0
    userVoteTrailId.value = trailId

    voteSaved.value = true
  } catch (e) {
    error.value = e.message || 'Failed to submit vote'
  }
}

/** ---------- Lifecycle ---------- */
onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    const params = new URLSearchParams(window.location.search)
    const token = params.get('token')
    if (!token) throw new Error('No token provided in URL')
    tokenRef.value = token
    await loadVote()
  } catch (e) {
    error.value = e.message || 'Failed to init'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section
      class="relative bg-cover bg-center py-20 bg-fixed"
      :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <div class="pg-scrim" aria-hidden="true"></div>
    <div class="relative mx-auto max-w-5xl px-4">
      <Card>
        <CardHeader class="p-6">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-9 w-2/3 mx-auto"/>
            <div class="space-y-2">
              <Skeleton class="h-4 w-full"/>
              <Skeleton class="h-4 w-2/3"/>
            </div>
          </div>
          <template v-else>
            <h1 class="text-center text-3xl font-bold tracking-tight sm:text-4xl font-montserrat" style="color:#f5f7fb">
              {{ pageTitle }}
            </h1>
            <p v-if="hikeName || endsAt" class="text-center text-sm mt-2" style="color:#c8d0de">
              <span v-if="hikeName" class="font-medium">{{ hikeName }}</span>
              <span v-if="hikeName && endsAt"> • </span>
              <span v-if="endsAt">Voting ends: {{ new Date(endsAt).toLocaleString() }}</span>
            </p>
          </template>
        </CardHeader>

        <CardContent class="p-6 pt-0">
          <div v-if="loading" class="grid grid-cols-1 gap-5 md:grid-cols-3">
            <Skeleton class="h-64 w-full"/>
            <Skeleton class="h-64 w-full"/>
            <Skeleton class="h-64 w-full"/>
          </div>

          <div v-else-if="error" class="text-red-500 text-center">
            <img
              src="@/assets/petr.png"
              class="mx-auto max-h-[150px] mb-2"
              alt=""
            />
            {{ error }}
          </div>

          <div v-else class="space-y-6">
            <!-- On desktop the grid becomes a subgrid: each card spans 6 explicit rows so
                 every section (image / title / stats / elev-gain / chart / vote) aligns
                 across all three columns regardless of content height. -->
            <div class="grid grid-cols-1 gap-6 md:grid-cols-3 md:gap-x-6 md:gap-y-0">
              <div
                  v-for="t in trails"
                  :key="t.id"
                  class="public-trail-card group relative overflow-hidden rounded-2xl
                         md:row-span-6 md:grid md:grid-rows-subgrid"
                  :class="{'is-selected': alreadyVoted && userVoteTrailId === t.id}"
              >
                <!-- Row 1: Image -->
                <div class="aspect-[16/10] w-full overflow-hidden bg-black/30">
                  <img
                      :src="imageUrl(t.id)"
                      :alt="t.name"
                      class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                      loading="lazy"
                  />
                </div>

                <!-- Row 2: Name + location + difficulty badge -->
                <div class="px-4 pt-4 flex items-start justify-between gap-3">
                  <div>
                    <h3 class="text-lg font-bold" style="color:#f5f7fb">{{ t.name }}</h3>
                    <p class="text-sm" style="color:#c8d0de">{{ t.location }}</p>
                  </div>
                  <DifficultyBadge class="shrink-0" :difficulty="t.difficulty" />
                </div>

                <!-- Row 3: Stats (Length + Est. time) — always 2 cols -->
                <div class="px-4 pt-3">
                  <div class="grid grid-cols-2 gap-2 text-sm">
                    <div class="rounded-lg px-3 py-2 border" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12);">
                      <p class="text-xs uppercase tracking-wide" style="color:#9aa6bb">Length</p>
                      <p class="font-semibold" style="color:#f5f7fb">
                        {{ t.length_mi != null ? `${Number(t.length_mi).toFixed(1)} mi` : '—' }}
                      </p>
                    </div>
                    <div class="rounded-lg px-3 py-2 border" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12);">
                      <p class="text-xs uppercase tracking-wide" style="color:#9aa6bb">Est. time</p>
                      <p class="font-semibold" style="color:#f5f7fb">
                        <template v-if="t.estimated_time_hr != null">{{ t.estimated_time_hr }} hr</template>
                        <template v-else>—</template>
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Row 4: Elevation gain — its own row; empty div when absent so the
                     subgrid row still participates in cross-card height alignment. -->
                <div v-if="t.elevation_gain_ft != null" class="px-4 pt-2">
                  <div class="rounded-lg px-3 py-2 border" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12);">
                    <p class="text-xs uppercase tracking-wide" style="color:#9aa6bb">Elev. gain</p>
                    <p class="font-semibold" style="color:#f5f7fb">{{ t.elevation_gain_ft.toLocaleString() }} ft</p>
                  </div>
                </div>
                <div v-else></div>

                <!-- Row 5: Elevation chart — empty div when absent -->
                <div v-if="t.elevation_data" class="px-4 pt-3">
                  <ElevationChart :elevationData="t.elevation_data" />
                </div>
                <div v-else></div>

                <!-- Row 6: Vote section — pinned to the bottom of its row -->
                <div class="p-4 pt-4 flex flex-col justify-end">
                  <div v-if="alreadyVoted" class="mb-4">
                    <div class="flex items-center justify-between text-xs mb-1.5" style="color:#c8d0de">
                      <span>Votes: {{ countFor(t.id) }} / {{ totalVotes }}</span>
                      <span class="font-semibold" style="color:#f5f7fb">{{ percentFor(t.id) }}%</span>
                    </div>
                    <div class="public-vote-bar w-full h-2.5 rounded-full border overflow-hidden">
                      <div
                          class="public-vote-bar-fill h-full transition-all duration-500"
                          :style="{ width: percentFor(t.id) + '%' }"
                      />
                    </div>
                  </div>

                  <div v-if="userVoteTrailId !== t.id" class="flex">
                    <Button
                        type="button"
                        class="inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm bg-uci-blue text-white font-semibold transition focus:outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                        @click="submitVote(t.id)"
                    >
                      <span>
                        <template v-if="!alreadyVoted">Vote</template>
                        <template v-else>Change vote to this</template>
                      </span>
                    </Button>
                  </div>
                  <div v-else class="public-vote-pill inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold">
                    <Check class="h-4 w-4" />
                    You voted for this
                  </div>
                </div>
              </div>
            </div>
            <div v-if="voteSaved" class="text-lg font-bold text-center" style="color:#7be3a3">Vote saved</div>
            <div class="pt-2 text-center text-sm" style="color:#c8d0de">
              You can change your vote anytime before voting closes.
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </section>
</template>
