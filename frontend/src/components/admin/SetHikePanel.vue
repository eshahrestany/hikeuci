<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useColorMode } from '@vueuse/core'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Skeleton } from '@/components/ui/skeleton'
import { Input } from '@/components/ui/input'
import { Table, TableHead, TableRow, TableHeader, TableCell, TableBody } from '@/components/ui/table'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import {useAuth} from "@/lib/auth.js";
const { postWithAuth, fetchWithAuth } = useAuth()

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

// Compute the defaults from "now" in the user's local tz
function computeDefaultSchedule(now = new Date()) {
  // For vote flow: signup = first upcoming Tuesday @ 00:00
  const signupStart  = nextWeekdayAt(now, 2, 0, 0, 0, 0)  // Tue

  // For signup flow: waiver = first upcoming Thursday @ 00:00
  const waiverStart  = nextWeekdayAt(now, 4, 0, 0, 0, 0)  // Thu

  // Hike: first upcoming Saturday @ 08:00
  const hikeDate     = nextWeekdayAt(now, 6, 8, 0, 0, 0)  // Sat 08:00

  return { signupStart, waiverStart, hikeDate }
}



// trails state
const trailsLoading = ref(false)
const trailsError = ref('')
const trails = ([])

const search = ref('')

// selection state
const selectedTrailIds = ref([]) // for 'vote' (max 3)
const selectedTrailId = ref(null) // for 'signup'

// fetch all trails from /api/trails
async function fetchTrails() {
  trailsLoading.value = true
  trailsError.value = ''
  try {
    const res = await fetchWithAuth('/api/trails')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    // keep only what we show, but retain id for form posting
    trails.value = data.map((t) => ({
      id: t.id,
      name: t.name,
      location: t.location,
      difficulty: t.difficulty
    }))
  } catch (e) {
    trailsError.value = e?.message ?? 'Failed to load trails'
  } finally {
    trailsLoading.value = false
  }
}

const filteredTrails = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return trails.value
  return trails.value.filter(t => {
    const name = (t.name ?? '').toLowerCase()
    const loc  = (t.location ?? '').toLowerCase()
    const diff = String(t.difficulty ?? '').toLowerCase()
    return name.includes(q) || loc.includes(q) || diff.includes(q)
  })
})

function toggleSelectVote(id) {
  const i = selectedTrailIds.value.indexOf(id)
  if (i >= 0) {
    selectedTrailIds.value.splice(i, 1)
  } else if (selectedTrailIds.value.length < 3) {
    selectedTrailIds.value.push(id)
  }
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
    flow: mode.value,  // 'vote' | 'signup'
    timezone: tz,
    waiver_date: toIsoWithOffset(form.waiverStart),
    hike_date:   toIsoWithOffset(form.hikeDate),
  }

  if (mode.value === 'vote') {
    base.signup_date = toIsoWithOffset(form.signupStart)
    base.vote_trail_ids = [...selectedTrailIds.value]
  } else {
    base.trail_id = selectedTrailId.value
  }
  return base
}


async function submit() {
  // guard — don’t trust the button state alone
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
function isAfter(a, b) { return a.getTime() > b.getTime() }

const LABELS = {
  signupStart: 'Signup start',
  waiverStart: 'Waiver start',
  hikeDate: 'Hike date',
}

const validation = computed(() => {
  const msgs = []
  const now = new Date()
  const voteMode = mode.value === 'vote'

  // Build the ordered timeline:
  // - vote flow: signup → waiver → hike
  // - signup flow: waiver → hike
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

  // required
  for (const [key, d] of ordered) {
    if (!d) msgs.push(`${LABELS[key]} is required`)
  }

  if (!msgs.length) {
    // future
    for (const [key, d] of ordered) {
      if (!(d.getTime() > now.getTime())) msgs.push(`${LABELS[key]} must be in the future`)
    }
    // strictly increasing
    for (let i = 1; i < ordered.length; i++) {
      const [pk, pv] = ordered[i - 1]
      const [ck, cv] = ordered[i]
      if (!(cv.getTime() > pv.getTime())) msgs.push(`${LABELS[ck]} must be after ${LABELS[pk]}`)
    }
  }

  // trail selection rules
  if (voteMode) {
    if (selectedTrailIds.value.length !== 3) msgs.push('Select exactly 3 trails for voting')
  } else {
    if (selectedTrailId.value == null) msgs.push('Select 1 trail')
  }

  return { valid: msgs.length === 0, messages: msgs }
})

const isFormValid = computed(() => validation.value.valid)


// if the user flips flow, clear selection to avoid mismatches
watch(mode, (m) => {
  selectedTrailIds.value = []
  selectedTrailId.value = null
})

watch(showSetNextHike, (open) => {
  if (open) fetchTrails()
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

    <p class="text-sm">These time values will be submitted to the server as the timezone America/Los_Angeles</p>

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

  <!-- Loading / error -->
  <div v-if="trailsLoading" class="grid gap-3 md:grid-cols-2">
    <Skeleton class="h-10 w-full rounded-md" />
    <Skeleton class="h-10 w-full rounded-md" />
    <Skeleton v-if="mode === 'vote'" class="h-10 w-full rounded-md" />
    <p class="text-xs text-muted-foreground col-span-full">Loading trails…</p>
  </div>
  <p v-else-if="trailsError" class="text-sm text-red-500">{{ trailsError }}</p>

  <!-- Table + search -->
  <div v-else class="space-y-2">
    <div class="flex items-center justify-between gap-3">
      <Input
        v-model="search"
        class="max-w-md"
        placeholder="Search name, location, difficulty…"
      />
      <p class="text-xs text-muted-foreground">
        <template v-if="mode === 'vote'">{{ selectedTrailIds.length }}/3 selected</template>
        <template v-else>{{ selectedTrailId ? '1/1 selected' : '0/1 selected' }}</template>
      </p>
    </div>

    <Table class="mt-2">
      <TableHeader>
        <TableRow>
          <TableHead class="w-12">Select</TableHead>
          <TableHead>Name</TableHead>
          <TableHead>Location</TableHead>
          <TableHead>Difficulty</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="t in filteredTrails" :key="t.id">
          <TableCell>
            <template v-if="mode === 'vote'">
              <input
                type="checkbox"
                :checked="selectedTrailIds.includes(t.id)"
                @change="toggleSelectVote(t.id)"
                :disabled="!selectedTrailIds.includes(t.id) && selectedTrailIds.length >= 3"
              />
            </template>
            <template v-else>
              <input
                type="radio"
                name="trail"
                :value="t.id"
                :checked="selectedTrailId === t.id"
                @change="selectedTrailId = t.id"
              />
            </template>
          </TableCell>
          <TableCell class="font-medium">{{ t.name }}</TableCell>
          <TableCell>{{ t.location || '—' }}</TableCell>
          <TableCell>{{ t.difficulty ?? '—' }}</TableCell>
        </TableRow>

        <TableRow v-if="!filteredTrails.length">
          <TableCell colspan="4" class="text-center text-sm text-muted-foreground py-6">
            No trails match your search.
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <!-- hidden fields so the form "has" ids internally for later posting -->
    <input type="hidden" name="selectedTrailId" :value="selectedTrailId || ''">
    <input type="hidden" name="selectedTrailIds" :value="JSON.stringify(selectedTrailIds)">
  </div>
</div>

    <!-- submit button -->
    <div class="flex items-center justify-end gap-3">
      <p v-if="!isFormValid" class="text-xs text-red-500 mr-auto">
        {{ validation.messages[0] }}
      </p>
      <Button variant="ghost" @click="resetAndClose">Cancel</Button>
      <Button :disabled="!isFormValid" @click="submit">Submit</Button>
    </div>
  </div>
</template>
