<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Badge } from '@/components/ui/badge'
import { CalendarClock } from 'lucide-vue-next'
import ActiveHikeTimeline from '@/components/admin/ActiveHikeTimeline.vue'

const TYPE_LABEL = { voting: 'Voting', signup: 'Signup', waiver: 'Waiver' }

const props = defineProps({
  activeHike: { type: Object, required: true }, // { id, has_vote, phase, timeline }
  existingTypes: { type: Array, required: true }, // campaign types that already have rows
})

const now = ref(Date.now())
let timer = null
onMounted(() => { timer = setInterval(() => { now.value = Date.now() }, 1000) })
onUnmounted(() => { if (timer) clearInterval(timer) })

const expectedTypes = computed(() =>
  props.activeHike.has_vote ? ['voting', 'signup', 'waiver'] : ['signup', 'waiver']
)

const sendTimes = computed(() => ({
  voting: props.activeHike.timeline?.vote_date,
  signup: props.activeHike.timeline?.signup_date,
  waiver: props.activeHike.timeline?.waiver_date,
}))

const upcoming = computed(() => {
  const existing = new Set(props.existingTypes)
  return expectedTypes.value
    .filter(t => !existing.has(t) && sendTimes.value[t])
    .map(t => ({ type: t, send_at: sendTimes.value[t] }))
})

function formatSendTime(iso) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit',
  })
}

function formatCountdown(iso) {
  const target = new Date(iso).getTime()
  const diff = target - now.value
  if (diff <= 0) return 'any moment now'
  const totalMin = Math.floor(diff / 60000)
  const days = Math.floor(totalMin / 1440)
  const hours = Math.floor((totalMin % 1440) / 60)
  const minutes = totalMin % 60
  const seconds = Math.floor((diff % 60000) / 1000)
  if (days > 0) return `${days}d ${hours}h ${minutes}m`
  if (hours > 0) return `${hours}h ${minutes}m`
  if (minutes > 0) return `${minutes}m ${seconds}s`
  return `${seconds}s`
}
</script>

<template>
  <div class="rounded-lg border bg-muted/30 p-4 space-y-4">
    <ActiveHikeTimeline
      :has-vote="activeHike.has_vote"
      :current-phase="activeHike.phase || ''"
      :timestamps="activeHike.timeline"
    />

    <div v-if="upcoming.length" class="border-t pt-4 space-y-2">
      <div class="flex items-center gap-2">
        <CalendarClock class="h-4 w-4 text-muted-foreground" />
        <h3 class="text-sm font-semibold">Upcoming Email Campaigns</h3>
      </div>
      <div class="space-y-1.5">
        <div
          v-for="c in upcoming"
          :key="c.type"
          class="flex flex-wrap items-center justify-between gap-3 rounded-md border bg-background px-3 py-2 text-sm"
        >
          <div class="flex items-center gap-2 min-w-0">
            <Badge variant="secondary">{{ TYPE_LABEL[c.type] }}</Badge>
            <span class="text-muted-foreground truncate">
              sends {{ formatSendTime(c.send_at) }}
            </span>
          </div>
          <span class="font-mono tabular-nums text-xs text-muted-foreground whitespace-nowrap">
            in {{ formatCountdown(c.send_at) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
