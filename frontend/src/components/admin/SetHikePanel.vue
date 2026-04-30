<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useColorMode } from '@vueuse/core'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Input } from '@/components/ui/input'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { useAuth } from "@/lib/auth.js"
import TrailPicker from "@/components/admin/TrailPicker.vue"
import { CalendarPlus, Info } from 'lucide-vue-next'

const { postWithAuth } = useAuth()

const colorMode = useColorMode()
const dark = computed(() => colorMode.value === 'dark')

const showSetNextHike = ref(false)
const mode = ref('vote') // 'vote' | 'signup'

const form = reactive({
  signupStart: null,  // Date
  waiverStart: null,  // Date
  hikeDate: null      // Date
})

const dateTimeFlow = ['calendar', 'time']
const minuteStep = 5

// date helpers
function clone(d) {
  const dt = toDate(d)
  if (!dt) throw new Error('Invalid date for clone()')
  return new Date(dt.getTime())
}

function addDays(d, days) {
  const dt = clone(d)
  dt.setDate(dt.getDate() + days)
  return dt
}
function atTime(d, h = 0, m = 0, s = 0, ms = 0) {
  const dt = clone(d)
  dt.setHours(h, m, s, ms)
  return dt
}
function startOfDay(d) { return atTime(d, 0, 0, 0, 0) }

// Next occurrence of a weekday strictly after `from` (local time)
// targetDow: 0=Sun ... 6=Sat
function nextWeekdayAt(from = new Date(), targetDow, h=0, m=0, s=0, ms=0) {
  const currentDow = from.getDay()
  let delta = (targetDow - currentDow + 7) % 7
  // build candidate at requested clock time
  const candidate = startOfDay(addDays(from, delta))
  candidate.setHours(h, m, s, ms)
  // if it's not strictly in the future, push one week
  if (candidate <= from) candidate.setDate(candidate.getDate() + 7)
  return candidate
}

function computeDefaultSchedule(now = new Date()) {
  // For vote flow: signup = first upcoming Tuesday @ 6pm
  const signupStart = nextWeekdayAt(now, 2, 18, 0, 0, 0)  // Tue 18:00

  // Following Thursday @ 18:00 (2 calendar days later
  const waiverStart = new Date(signupStart);
  waiverStart.setDate(waiverStart.getDate() + 2); // Thu 18:00

  // Following Saturday @ 8:00 (4 calendar days later, adjust hour)
  const hikeDate = new Date(signupStart);
  hikeDate.setDate(hikeDate.getDate() + 4);       // Sat 18:00
  hikeDate.setHours(8, 0, 0, 0);                  // Sat 08:00

  return { signupStart, waiverStart, hikeDate }
}

// trail selection state
const selectedTrail = ref(null)   // single trail object | null  (signup mode)
const selectedTrails = ref([])    // trail object[]              (vote mode)

function onTrailSelect(v) {
  if (mode.value === 'vote') selectedTrails.value = v
  else selectedTrail.value = v
}

function openFormWithDefaults() {
  const { signupStart, waiverStart, hikeDate } = computeDefaultSchedule()
  form.signupStart = signupStart
  form.waiverStart = waiverStart
  form.hikeDate    = hikeDate
  showSetNextHike.value = true
}

function resetAndClose() {
  showSetNextHike.value = false
  mode.value = 'vote'
  form.signupStart = form.waiverStart = form.hikeDate = null
}

function toIsoWithOffset(d) {
  // ISO 8601 with local offset, e.g. 2025-09-20T08:00:00-07:00
  const dt = toDate(d)
  if (!dt) throw new Error('Invalid date for ISO formatting')
  const pad = (n) => String(n).padStart(2, '0')
  const y = dt.getFullYear()
  const m = pad(dt.getMonth() + 1)
  const day = pad(dt.getDate())
  const hh = pad(dt.getHours())
  const mm = pad(dt.getMinutes())
  const ss = pad(dt.getSeconds())
  const off = -dt.getTimezoneOffset()
  const sign = off >= 0 ? '+' : '-'
  const oh = pad(Math.floor(Math.abs(off) / 60))
  const om = pad(Math.abs(off) % 60)
  return `${y}-${m}-${day}T${hh}:${mm}:${ss}${sign}${oh}:${om}`
}

function buildPayload() {
  const tz = 'America/Los_Angeles'
  const base = {
    flow: mode.value,
    timezone: tz,
    waiver_date: toIsoWithOffset(form.waiverStart),
    hike_date:   toIsoWithOffset(form.hikeDate),
  }

  if (mode.value === 'vote') {
    base.signup_date = toIsoWithOffset(form.signupStart)
    base.vote_trail_ids = selectedTrails.value.map(t => t.id)
  } else {
    base.trail_id = selectedTrail.value.id
  }
  return base
}

async function submit() {
  if (!isFormValid.value) {
    console.warn('Form invalid:', validation.value.messages)
    return
  }

  const payload = buildPayload()

  try {
    const res = await postWithAuth('/api/admin/set-hike', payload)
    if (res.ok) {
      window.location.reload()
    } else {
      throw res.error
    }
  } catch (err) {
    console.error('Failed to schedule next hike:', err)
  }
}


// --- validation helpers ---
function toDate(val) {
  if (val instanceof Date) return isNaN(val.getTime()) ? null : val
  if (typeof val === 'number' || typeof val === 'string') {
    const d = new Date(val)
    return isNaN(d.getTime()) ? null : d
  }
  return null
}

const LABELS = {
  signupStart: 'Signup start',
  waiverStart: 'Waiver start',
  hikeDate: 'Hike date',
}

const validation = computed(() => {
  const msgs = []
  const now = new Date()
  const voteMode = mode.value === 'vote'

  const ordered = voteMode
    ? [
        ['signupStart', toDate(form.signupStart)],
        ['waiverStart', toDate(form.waiverStart)],
        ['hikeDate',    toDate(form.hikeDate)],
      ]
    : [
        ['waiverStart', toDate(form.waiverStart)],
        ['hikeDate',    toDate(form.hikeDate)],
      ]

  for (const [key, d] of ordered) {
    if (!d) msgs.push(`${LABELS[key]} is required`)
  }

  if (!msgs.length) {
    for (const [key, d] of ordered) {
      if (!(d.getTime() > now.getTime())) msgs.push(`${LABELS[key]} must be in the future`)
    }
    for (let i = 1; i < ordered.length; i++) {
      const [pk, pv] = ordered[i - 1]
      const [ck, cv] = ordered[i]
      if (!(cv.getTime() > pv.getTime())) msgs.push(`${LABELS[ck]} must be after ${LABELS[pk]}`)
    }
  }

  if (voteMode) {
    if (selectedTrails.value.length !== 3) msgs.push('Select exactly 3 trails for voting')
  } else {
    if (selectedTrail.value == null) msgs.push('Select 1 trail')
  }

  return { valid: msgs.length === 0, messages: msgs }
})

const isFormValid = computed(() => validation.value.valid)

// clear selection when flow changes
watch(mode, () => {
  selectedTrail.value = null
  selectedTrails.value = []
})
</script>

<template>
  <!-- Empty state: no upcoming hike -->
  <div v-if="!showSetNextHike" class="flex flex-col items-center py-10 gap-4">
    <div class="flex h-14 w-14 items-center justify-center rounded-full bg-muted">
      <CalendarPlus class="h-6 w-6 text-muted-foreground" />
    </div>
    <div class="text-center">
      <p class="font-medium">No upcoming hike scheduled</p>
      <p class="text-sm text-muted-foreground mt-1">Set up the next hike to start the registration process</p>
    </div>
    <Button @click="openFormWithDefaults">
      <CalendarPlus class="h-4 w-4" />
      Schedule Next Hike
    </Button>
  </div>

  <!-- Hike setup form -->
  <div v-else class="space-y-6">
    <!-- Mode selector -->
    <div class="space-y-3">
      <Label class="text-sm font-semibold">Flow</Label>
      <RadioGroup v-model="mode" class="flex flex-col sm:flex-row gap-3">
        <label
          for="mode-vote"
          class="flex items-center gap-3 flex-1 rounded-lg border p-3 cursor-pointer transition-colors"
          :class="mode === 'vote' ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'"
        >
          <RadioGroupItem id="mode-vote" value="vote" />
          <div>
            <p class="text-sm font-medium">Start a vote</p>
            <p class="text-xs text-muted-foreground">Members vote on 3 trail options</p>
          </div>
        </label>
        <label
          for="mode-signup"
          class="flex items-center gap-3 flex-1 rounded-lg border p-3 cursor-pointer transition-colors"
          :class="mode === 'signup' ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'"
        >
          <RadioGroupItem id="mode-signup" value="signup" />
          <div>
            <p class="text-sm font-medium">Skip to signup</p>
            <p class="text-xs text-muted-foreground">Go straight to signup phase</p>
          </div>
        </label>
      </RadioGroup>
    </div>

    <div class="rounded-lg bg-muted/40 px-3 py-2 text-xs text-muted-foreground flex items-start gap-2">
      <Info class="h-3.5 w-3.5 mt-0.5 shrink-0" />
      Times are interpreted as PST (America/Los_Angeles), regardless of your local timezone.
    </div>

    <!-- Timestamps -->
    <div class="space-y-3">
      <Label class="text-sm font-semibold">Schedule</Label>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-if="mode === 'vote'" class="space-y-1.5">
          <Label for="signupStart" class="text-xs text-muted-foreground">Signup start</Label>
          <VueDatePicker
            id="signupStart"
            v-model="form.signupStart"
            :is-24="false"
            :dark="dark"
            :flow="dateTimeFlow"
            auto-apply
            :minutes-increment="minuteStep"
            placeholder="Pick date & time"
          />
        </div>

        <div class="space-y-1.5">
          <Label for="waiverStart" class="text-xs text-muted-foreground">Waiver start</Label>
          <VueDatePicker
            id="waiverStart"
            v-model="form.waiverStart"
            :is-24="false"
            :dark="dark"
            :flow="dateTimeFlow"
            auto-apply
            :minutes-increment="minuteStep"
            placeholder="Pick date & time"
          />
        </div>

        <div class="space-y-1.5">
          <Label for="hikeDate" class="text-xs text-muted-foreground">Hike date</Label>
          <VueDatePicker
            id="hikeDate"
            v-model="form.hikeDate"
            :is-24="false"
            :dark="dark"
            :flow="dateTimeFlow"
            auto-apply
            :minutes-increment="minuteStep"
            placeholder="Pick date & time"
          />
        </div>
      </div>
    </div>

    <!-- Trail picker -->
    <div class="space-y-3">
      <Label class="text-sm font-semibold">
        {{ mode === 'vote' ? 'Trails for voting (select 3)' : 'Trail (select 1)' }}
      </Label>
      <TrailPicker
        :mode="mode === 'vote' ? 'multi' : 'single'"
        :max-select="3"
        :model-value="mode === 'vote' ? selectedTrails : selectedTrail"
        @update:model-value="onTrailSelect"
      />
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-end gap-3 pt-2 border-t">
      <p v-if="!isFormValid" class="text-xs text-destructive mr-auto">
        {{ validation.messages[0] }}
      </p>
      <Button variant="ghost" @click="resetAndClose">Cancel</Button>
      <Button :disabled="!isFormValid" @click="submit">
        <CalendarPlus class="h-4 w-4" />
        Schedule Hike
      </Button>
    </div>
  </div>
</template>
