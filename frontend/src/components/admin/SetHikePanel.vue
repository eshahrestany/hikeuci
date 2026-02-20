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

  // Following Saturday @ 10:00 (4 calendar days later, adjust hour)
  const hikeDate = new Date(signupStart);
  hikeDate.setDate(hikeDate.getDate() + 4);       // Sat 18:00
  hikeDate.setHours(10, 0, 0, 0);                  // Sat 10:00

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
  <div v-if="!showSetNextHike">
    <p class="text-center text-sm text-gray-500 mb-4">No upcoming hikes found.</p>
    <Button class="block mx-auto" @click="openFormWithDefaults">Set Next Hike</Button>
  </div>

  <div v-else class="space-y-6">
    <!-- Mode -->
    <div class="space-y-2">
      <Label class="text-sm font-medium">Flow</Label>
      <RadioGroup v-model="mode" class="flex gap-6">
        <div class="flex items-center space-x-2">
          <RadioGroupItem id="mode-vote" value="vote" />
          <Label for="mode-vote" class="cursor-pointer">Start a vote</Label>
        </div>
        <div class="flex items-center space-x-2">
          <RadioGroupItem id="mode-signup" value="signup" />
          <Label for="mode-signup" class="cursor-pointer">Go straight to signup phase</Label>
        </div>
      </RadioGroup>
    </div>

    <p class="text-sm text-stone">Your local timezone will be ignored and the server will interpret these times as PST (America/Los_Angeles)</p>

    <!-- Timestamps -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-if="mode === 'vote'" class="space-y-2">
        <Label for="signupStart">Signup start</Label>
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

      <div class="space-y-2">
        <Label for="waiverStart">Waiver start</Label>
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

      <div class="space-y-2">
        <Label for="hikeDate">Hike date</Label>
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

    <!-- Trails -->
    <div class="space-y-3">
      <Label>
        {{ mode === 'vote' ? 'Trails for voting (choose 3)' : 'Trail (choose 1)' }}
      </Label>
      <TrailPicker
        :mode="mode === 'vote' ? 'multi' : 'single'"
        :max-select="3"
        :model-value="mode === 'vote' ? selectedTrails : selectedTrail"
        @update:model-value="onTrailSelect"
      />
    </div>

    <!-- submit -->
    <div class="flex items-center justify-end gap-3">
      <p v-if="!isFormValid" class="text-xs text-red-500 mr-auto">
        {{ validation.messages[0] }}
      </p>
      <Button variant="ghost" @click="resetAndClose">Cancel</Button>
      <Button :disabled="!isFormValid" @click="submit">Submit</Button>
    </div>
  </div>
</template>
