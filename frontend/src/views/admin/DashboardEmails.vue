<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/lib/auth.js'
import { useRealtime } from '@/lib/realtime.js'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Mail } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import EmailHikePicker from '@/components/admin/EmailHikePicker.vue'
import EmailCampaignTabs from '@/components/admin/EmailCampaignTabs.vue'
import EmailTaskTable from '@/components/admin/EmailTaskTable.vue'
import ActiveHikePanel from '@/components/admin/ActiveHikePanel.vue'

const VALID_TYPES = ['voting', 'signup', 'waiver', 'waitlist']

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

async function loadCampaigns({ background = false } = {}) {
  if (!hikeId.value) {
    campaigns.value = []
    return
  }
  if (!background) campaignsLoading.value = true
  try {
    const res = await fetchWithAuth(`/api/admin/email-campaigns/hikes/${hikeId.value}/campaigns`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    campaigns.value = await res.json()
    const types = campaigns.value.map(c => c.type)
    if (!campaignType.value || !types.includes(campaignType.value)) {
      campaignType.value = types[0] ?? null
    }
    syncHikeAndType()
  } catch (e) {
    console.error(e)
    toast.error('Failed to load campaigns')
  } finally {
    if (!background) campaignsLoading.value = false
  }
}

watch(hikeId, () => { loadCampaigns() })
watch(campaignType, syncHikeAndType)

const topics = computed(() => {
  const t = []
  if (hikeId.value) t.push(`email-campaigns:hike:${hikeId.value}`)
  if (activeCampaign.value?.id) t.push(`campaign:${activeCampaign.value.id}`)
  return t
})
useRealtime(topics, {
  campaign_started:   () => loadCampaigns(),
  campaign_progress:  () => loadCampaigns({ background: true }),
  campaign_completed: () => { loadCampaigns(); refreshTick.value += 1 },
  tasks_updated:      { debounceMs: 0, fn: () => { loadCampaigns({ background: true }); refreshTick.value += 1 } },
})

onMounted(async () => {
  await Promise.all([loadHikes(), loadActiveHike()])
  await loadCampaigns()
})

const stats = computed(() => activeCampaign.value?.counts || { total: 0, pending: 0, sent: 0, failed: 0 })
</script>

<template>
  <section class="p-4 md:p-6">
    <Card class="mx-auto">
      <CardHeader class="pb-3">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Mail class="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle class="text-xl">Email Campaigns</CardTitle>
            <p class="text-xs text-muted-foreground mt-0.5">Track and manage member email delivery</p>
          </div>
        </div>
      </CardHeader>
      <hr class="h-px mx-6 bg-border border-0" />

      <CardContent class="pt-5 space-y-6">
        <!-- Hike picker -->
        <div class="flex flex-wrap items-center gap-3">
          <Label class="text-sm text-muted-foreground whitespace-nowrap">Hike</Label>
          <Skeleton v-if="hikesLoading" class="h-9 w-[320px]" />
          <EmailHikePicker v-else-if="hikes.length" :hikes="hikes" v-model="hikeId" />
          <Badge
            v-if="isCurrent"
            variant="outline"
            class="bg-green-600/10 text-green-700 dark:text-green-400 border-green-600/30"
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

        <!-- Loading -->
        <div v-if="hikesLoading" class="space-y-4">
          <Skeleton class="h-10 w-full max-w-xl" />
          <Skeleton class="h-32 w-full" />
        </div>

        <!-- Empty state -->
        <div v-else-if="!hikes.length" class="py-12 text-center text-muted-foreground">
          <Mail class="h-8 w-8 mx-auto mb-3 opacity-30" />
          <p>No email campaigns yet.</p>
          <p class="text-sm mt-1">They appear after the first vote, signup, or waiver send.</p>
        </div>

        <!-- Error -->
        <div v-else-if="loadError" class="py-8 text-center">
          <p class="text-destructive">{{ loadError }}</p>
          <Button variant="outline" size="sm" class="mt-3" @click="loadHikes">Retry</Button>
        </div>

        <template v-else>
          <Skeleton v-if="campaignsLoading" class="h-10 w-full max-w-md" />
          <template v-else-if="campaigns.length">
            <EmailCampaignTabs :campaigns="campaigns" v-model="campaignType" />

            <!-- Stats row -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="rounded-lg border bg-muted/30 px-3 py-2.5 text-center">
                <p class="text-xs text-muted-foreground mb-0.5">Total</p>
                <p class="text-xl font-bold tabular-nums">{{ stats.total }}</p>
              </div>
              <div class="rounded-lg border bg-amber-500/10 border-amber-500/20 px-3 py-2.5 text-center">
                <p class="text-xs text-amber-700 dark:text-amber-400 mb-0.5">Pending</p>
                <p class="text-xl font-bold tabular-nums text-amber-700 dark:text-amber-400">{{ stats.pending }}</p>
              </div>
              <div class="rounded-lg border bg-green-500/10 border-green-500/20 px-3 py-2.5 text-center">
                <p class="text-xs text-green-700 dark:text-green-400 mb-0.5">Sent</p>
                <p class="text-xl font-bold tabular-nums text-green-700 dark:text-green-400">{{ stats.sent }}</p>
              </div>
              <div class="rounded-lg border bg-red-500/10 border-red-500/20 px-3 py-2.5 text-center">
                <p class="text-xs text-red-700 dark:text-red-400 mb-0.5">Failed</p>
                <p class="text-xl font-bold tabular-nums text-red-700 dark:text-red-400">{{ stats.failed }}</p>
              </div>
            </div>

            <EmailTaskTable
              v-if="activeCampaign"
              :campaign-id="activeCampaign.id"
              :campaign-type="activeCampaign.type"
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
