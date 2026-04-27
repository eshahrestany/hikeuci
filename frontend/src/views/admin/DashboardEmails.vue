<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/lib/auth.js'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { RefreshCw } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import EmailHikePicker from '@/components/admin/EmailHikePicker.vue'
import EmailCampaignTabs from '@/components/admin/EmailCampaignTabs.vue'
import EmailTaskTable from '@/components/admin/EmailTaskTable.vue'
import ActiveHikePanel from '@/components/admin/ActiveHikePanel.vue'

const VALID_TYPES = ['voting', 'signup', 'waiver', 'waitlist']
const POLL_MS = 5000

const { fetchWithAuth } = useAuth()
const route = useRoute()
const router = useRouter()

const hikes = ref([])
const hikesLoading = ref(true)
const campaigns = ref([])
const campaignsLoading = ref(false)
const loadError = ref('')
const activeHike = ref(null)

const hikeId = ref(route.query.hike ? parseInt(route.query.hike) : null)
const campaignType = ref(VALID_TYPES.includes(route.query.type) ? route.query.type : null)
const refreshTick = ref(0)

const activeCampaign = computed(() =>
  campaigns.value.find(c => c.type === campaignType.value) || null
)
const isInProgress = computed(() => activeCampaign.value?.in_progress === true)
const isCurrent = computed(() =>
  !!(activeHike.value && hikeId.value && activeHike.value.id === hikeId.value)
)
const existingTypes = computed(() => campaigns.value.map(c => c.type))

function syncHikeAndType() {
  const next = { ...route.query }
  next.hike = hikeId.value ? String(hikeId.value) : undefined
  next.type = campaignType.value || undefined
  router.replace({ query: next })
}

async function loadHikes() {
  hikesLoading.value = true
  loadError.value = ''
  try {
    const res = await fetchWithAuth('/api/admin/email-campaigns/hikes')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    hikes.value = await res.json()
    if (!hikeId.value || !hikes.value.some(h => h.id === hikeId.value)) {
      hikeId.value = hikes.value[0]?.id ?? null
    }
  } catch (e) {
    console.error(e)
    loadError.value = 'Failed to load hikes.'
    toast.error('Failed to load hikes')
  } finally {
    hikesLoading.value = false
  }
}

async function loadActiveHike() {
  try {
    const res = await fetchWithAuth('/api/admin/upcoming')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const body = await res.json()
    if (body.status === null || !body.hike_id) {
      activeHike.value = null
    } else {
      activeHike.value = {
        id: body.hike_id,
        has_vote: body.has_vote,
        phase: body.phase,
        timeline: body.timeline,
      }
    }
  } catch (e) {
    console.error('Failed to load active hike:', e)
    activeHike.value = null
  }
}

async function loadCampaigns() {
  if (!hikeId.value) {
    campaigns.value = []
    return
  }
  campaignsLoading.value = true
  try {
    const res = await fetchWithAuth(`/api/admin/email-campaigns/hikes/${hikeId.value}/campaigns`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    campaigns.value = await res.json()
    // Pick a sensible default: keep current type if it exists for this hike, else first.
    const types = campaigns.value.map(c => c.type)
    if (!campaignType.value || !types.includes(campaignType.value)) {
      campaignType.value = types[0] ?? null
    }
    syncHikeAndType()
  } catch (e) {
    console.error(e)
    toast.error('Failed to load campaigns')
  } finally {
    campaignsLoading.value = false
  }
}

function refresh() {
  loadCampaigns()
  loadActiveHike()
  refreshTick.value += 1
}

let pollInterval = null
function startPolling() {
  stopPolling()
  pollInterval = setInterval(() => {
    if (document.visibilityState !== 'visible') return
    if (!isInProgress.value) return
    refresh()
  }, POLL_MS)
}
function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

watch(hikeId, () => { loadCampaigns() })
watch(campaignType, syncHikeAndType)
watch(isInProgress, (val) => {
  if (val) startPolling()
  else stopPolling()
})

onMounted(async () => {
  await Promise.all([loadHikes(), loadActiveHike()])
  await loadCampaigns()
  if (isInProgress.value) startPolling()
})
onUnmounted(stopPolling)

const stats = computed(() => activeCampaign.value?.counts || { total: 0, pending: 0, sent: 0, failed: 0 })
</script>

<template>
  <section class="p-6">
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <div class="flex flex-wrap items-center justify-between gap-4">
          <CardTitle class="text-2xl">Email Campaigns</CardTitle>
          <Button
            variant="outline"
            size="sm"
            :disabled="hikesLoading || !hikeId"
            @click="refresh"
          >
            <RefreshCw class="h-4 w-4 mr-1" />
            Refresh
          </Button>
        </div>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>

      <CardContent class="space-y-6">
        <!-- Hike picker -->
        <div class="flex flex-wrap items-center gap-3">
          <Label class="text-sm text-muted-foreground whitespace-nowrap">Hike</Label>
          <Skeleton v-if="hikesLoading" class="h-9 w-[320px]" />
          <EmailHikePicker
            v-else-if="hikes.length"
            :hikes="hikes"
            v-model="hikeId"
          />
          <Badge
            v-if="isCurrent"
            variant="outline"
            class="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
          >
            Current
          </Badge>
        </div>

        <!-- Active hike panel -->
        <ActiveHikePanel
          v-if="isCurrent && activeHike"
          :active-hike="activeHike"
          :existing-types="existingTypes"
        />

        <!-- Loading initial state -->
        <div v-if="hikesLoading" class="space-y-4">
          <Skeleton class="h-10 w-full max-w-xl" />
          <Skeleton class="h-32 w-full" />
        </div>

        <!-- No campaigns at all across the system -->
        <div v-else-if="!hikes.length" class="py-12 text-center text-muted-foreground">
          <p>No email campaigns yet.</p>
          <p class="text-sm mt-1">They appear after the first vote, signup, or waiver send.</p>
        </div>

        <!-- Error -->
        <div v-else-if="loadError" class="py-8 text-center">
          <p class="text-destructive">{{ loadError }}</p>
          <Button variant="outline" size="sm" class="mt-3" @click="loadHikes">Retry</Button>
        </div>

        <!-- Campaign tabs + body -->
        <template v-else>
          <Skeleton v-if="campaignsLoading" class="h-10 w-full max-w-md" />
          <template v-else-if="campaigns.length">
            <EmailCampaignTabs :campaigns="campaigns" v-model="campaignType" />

            <!-- Stats row -->
            <div class="flex flex-wrap gap-2">
              <Badge variant="outline" class="px-3 py-1">
                Total: <span class="ml-1 font-semibold">{{ stats.total }}</span>
              </Badge>
              <Badge
                variant="outline"
                class="px-3 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
              >
                Pending: <span class="ml-1 font-semibold">{{ stats.pending }}</span>
              </Badge>
              <Badge
                variant="outline"
                class="px-3 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
              >
                Sent: <span class="ml-1 font-semibold">{{ stats.sent }}</span>
              </Badge>
              <Badge
                variant="outline"
                class="px-3 py-1 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
              >
                Failed: <span class="ml-1 font-semibold">{{ stats.failed }}</span>
              </Badge>
            </div>

            <!-- Task table -->
            <EmailTaskTable
              v-if="activeCampaign"
              :campaign-id="activeCampaign.id"
              :refresh-tick="refreshTick"
            />
          </template>
          <p v-else class="py-8 text-center text-muted-foreground">
            This hike has no email campaigns yet.
          </p>
        </template>
      </CardContent>
    </Card>
  </section>
</template>
