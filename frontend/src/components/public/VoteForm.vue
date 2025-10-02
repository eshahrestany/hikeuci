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

function difficultyColor(dif) {
  const colorDict = {
    "Easy": "text-green-600",
    "Moderate": "text-yellow-400",
    "Difficult": "text-orange-500",
    "Very Difficult": "text-red-500"
  }
  return colorDict[dif]
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
    loading.value = true
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
    await loadVote()       // refresh counts + selection
    voteSaved.value = true // flash success state
  } catch (e) {
    error.value = e.message || 'Failed to submit vote'
  } finally {
    loading.value = false
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
    <div class="absolute inset-0"></div>
    <div class="relative mx-auto max-w-5xl px-4">
      <Card class="bg-white border">
        <CardHeader class="p-6">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-9 w-2/3 mx-auto"/>
            <div class="space-y-2">
              <Skeleton class="h-4 w-full"/>
              <Skeleton class="h-4 w-2/3"/>
            </div>
          </div>
          <template v-else>
            <h1 class="text-center text-3xl font-bold text-uci-blue tracking-tight sm:text-4xl font-montserrat">
              {{ pageTitle }}
            </h1>
            <p v-if="hikeName || endsAt" class="text-center text-sm text-stone-600 mt-2">
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
            <div
                class="grid grid-cols-1 md:grid-cols-3 gap-6"
            >
              <div
                  v-for="t in trails"
                  :key="t.id"
                  class="group relative overflow-hidden rounded-2xl border border-stone-200 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5"
                  :class="{'bg-white': alreadyVoted && userVoteTrailId !== t.id, 'bg-blue-200': alreadyVoted && userVoteTrailId === t.id}"
              >
                <div class="aspect-[16/10] w-full overflow-hidden bg-stone-100 hover:scale-[1.05]">
                  <img
                      :src="imageUrl(t.id)"
                      :alt="t.name"
                      class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                      loading="lazy"
                  />
                </div>

                <div class="p-4">
                  <div class="flex items-start justify-between gap-3">
                    <div>
                      <h3 class="text-lg font-bold text-midnight">{{ t.name }}</h3>
                      <p class="text-sm text-stone-600">{{ t.location }}</p>
                    </div>
                  </div>

                  <div class="mt-3 grid grid-cols-2 gap-2 text-sm">
                    <div class="rounded-lg bg-stone-50 px-3 py-2 border border-stone-200">
                      <p class="text-xs uppercase tracking-wide text-stone-500">Length</p>
                      <p class="font-medium text-midnight">
                        {{ t.length_mi != null ? `${Number(t.length_mi).toFixed(1)} mi` : '—' }}
                      </p>
                    </div>
                    <div class="rounded-lg bg-stone-50 px-3 py-2 border border-stone-200">
                      <p class="text-xs uppercase tracking-wide text-stone-500">Est. time</p>
                      <p class="font-medium text-midnight">
                        <template v-if="t.estimated_time_hr != null">
                          <template v-if="t.estimated_time_hr == 1">
                            1 hour
                          </template>
                          <template v-else>
                            {{ t.estimated_time_hr }} hours
                          </template>
                        </template>
                        <template v-else>—</template>
                      </p>
                    </div>
                  </div>
                  <div class="mt-2 text-lg font-semibold" :class="difficultyColor(t.difficulty)">
                    {{ t.difficulty }}
                  </div>

                  <!-- Results display when already voted -->
                  <div v-if="alreadyVoted" class="mt-4">
                    <div class="flex items-center justify-between text-xs text-stone-600 mb-1">
                      <span>Votes: {{ countFor(t.id) }} / {{ totalVotes }}</span>
                      <span class="font-semibold text-midnight">{{ percentFor(t.id) }}%</span>
                    </div>
                    <div class="w-full h-3 rounded-full bg-stone-100 border border-stone-200 overflow-hidden">
                      <div
                          class="h-full bg-uci-blue transition-all duration-500"
                          :style="{ width: percentFor(t.id) + '%' }"
                      />
                    </div>
                  </div>

                  <div v-if="userVoteTrailId !== t.id" class="mt-4 flex">
                    <Button
                        type="button"
                        class="inline-flex items-center justify-center gap-2 rounded-xl border px-4 py-2 text-sm bg-uci-blue text-white hover:bg-uci-blue/90 font-semibold transition focus:outline-none disabled:opacity-60 disabled:cursor-not-allowed"
                        @click="submitVote(t.id)"
                    >
                      <span>
                        <template v-if="!alreadyVoted">Vote</template>
                        <template v-else>Change vote to this</template>
                      </span>
                    </Button>
                  </div>
                  <div v-else class="inline-flex items-center justify-center gap-2 rounded-xl border bg-uci-gold/50 mt-4 px-4 py-2 text-sm font-semibold">
                    You voted for this
                  </div>
                </div>
              </div>
            </div>
            <div v-if="voteSaved" class="text-lg font-bold text-center text-emerald-600">Vote saved</div>
            <div class="pt-2 text-center text-sm text-stone-600">
              You can change your vote anytime before voting closes.
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </section>
</template>
