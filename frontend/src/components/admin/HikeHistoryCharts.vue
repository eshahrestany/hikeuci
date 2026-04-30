<script setup>
import { computed } from 'vue'
import { VisXYContainer, VisLine, VisArea, VisAxis, VisStackedBar, VisGroupedBar, VisBulletLegend } from '@unovis/vue'
import { difficulties } from '@/lib/common.js'
import {
  ChartContainer,
  ChartCrosshair,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
} from '@/components/ui/chart'

const props = defineProps({
  hikes: { type: Array, required: true },
  attendanceFrequency: { type: Object, default: null },
})

const emit = defineEmits(['select-frequency'])

function formatShortDate(isoStr) {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' })
}

// Sort hikes chronologically for charts
const sortedHikes = computed(() =>
  [...props.hikes]
    .filter(h => h.status !== 'cancelled')
    .sort((a, b) => new Date(a.hike_date) - new Date(b.hike_date))
)

// Signups over time chart data
const signupsOverTimeData = computed(() =>
  sortedHikes.value.map(h => ({
    label: formatShortDate(h.hike_date),
    confirmed: h.num_confirmed,
    checked_in: h.num_checked_in,
  }))
)

const signupsOverTimeConfig = {
  confirmed: { label: 'Signups', color: 'hsl(221, 83%, 53%)' },
  checked_in: { label: 'Checked In', color: 'hsl(142, 71%, 45%)' },
}

const signupsOverTimeTooltip = componentToString(signupsOverTimeConfig, ChartTooltipContent, {
  labelFormatter: (i) => signupsOverTimeData.value[i]?.label ?? '',
})

// Attendance chart data
const attendanceData = computed(() =>
  sortedHikes.value.map(h => ({
    label: formatShortDate(h.hike_date),
    attendance: Math.round(h.attendance_rate * 100),
    noShow: Math.round((1 - h.attendance_rate) * 100),
  }))
)

const attendanceConfig = {
  attendance: { label: 'Attendance %', color: 'hsl(142, 71%, 45%)' },
  noShow: { label: 'No-Show %', color: 'hsl(0, 84%, 60%)' },
}

const attendanceTooltip = componentToString(attendanceConfig, ChartTooltipContent, {
  labelFormatter: (i) => attendanceData.value[i]?.label ?? '',
})

// Transport breakdown chart data
const transportData = computed(() =>
  sortedHikes.value.map(h => ({
    label: formatShortDate(h.hike_date),
    drivers: h.num_drivers,
    passengers: h.num_passengers,
    selfTransport: Math.max(0, h.num_confirmed - h.num_drivers - h.num_passengers),
    waitlisted: h.num_waitlisted,
  }))
)

const transportConfig = {
  drivers: { label: 'Drivers', color: 'hsl(220, 100%, 78%)' },
  passengers: { label: 'Passengers', color: 'hsl(275, 83%, 58%)' },
  selfTransport: { label: 'Self-Transport', color: 'hsl(25, 95%, 53%)' },
  waitlisted: { label: 'Waitlisted', color: 'hsl(0, 84%, 60%)' },
}

const transportTooltip = componentToString(transportConfig, ChartTooltipContent, {
  labelFormatter: (i) => transportData.value[i]?.label ?? '',
})

// Signups by difficulty (grouped bar: signups vs checked in)
const signupsByDifficultyData = computed(() => {
  const buckets = {}
  for (const h of sortedHikes.value) {
    if (h.trail_difficulty == null) continue
    const label = difficulties[h.trail_difficulty] || 'Unknown'
    if (!buckets[label]) buckets[label] = { label, signups: 0, checked_in: 0, difficulty: h.trail_difficulty }
    buckets[label].signups += h.num_confirmed
    buckets[label].checked_in += h.num_checked_in
  }
  return Object.values(buckets).sort((a, b) => a.difficulty - b.difficulty)
})

const signupsByDifficultyConfig = {
  signups: { label: 'Signups', color: 'hsl(221, 83%, 53%)' },
  checked_in: { label: 'Checked In', color: 'hsl(142, 71%, 45%)' },
}

const signupsByDifficultyTooltip = componentToString(signupsByDifficultyConfig, ChartTooltipContent, {
  labelFormatter: (i) => signupsByDifficultyData.value[i]?.label ?? '',
})

// Attendance frequency distribution
const frequencyData = computed(() => {
  if (!props.attendanceFrequency?.distribution?.length) return []
  const rows = props.attendanceFrequency.distribution.map(d => ({
    label: `${d.hikes_attended}`,
    members: d.num_members,
  }))
  const zeroCount = props.attendanceFrequency.zero_count ?? 0
  if (zeroCount > 0) rows.unshift({ label: '0', members: zeroCount })
  return rows
})

const frequencyConfig = {
  members: { label: 'Members', color: 'hsl(221, 83%, 53%)' },
}

const frequencyTooltip = componentToString(frequencyConfig, ChartTooltipContent, {
  labelFormatter: (i) => {
    const n = frequencyData.value[i]?.label
    return n ? `${n} hike${n === '1' ? '' : 's'}` : ''
  },
})

// Capacity utilization over time
// checked-in passengers / checked-in driver capacity * 100
const capacityData = computed(() =>
  sortedHikes.value
    .filter(h => h.checked_in_capacity > 0)
    .map(h => {
      const utilization = Math.round((h.num_checked_in_passengers / h.checked_in_capacity) * 100)
      return {
        label: formatShortDate(h.hike_date),
        utilization,
      }
    })
)

const capacityConfig = {
  utilization: { label: 'Capacity %', color: 'hsl(262, 83%, 58%)' },
}

const capacityTooltip = componentToString(capacityConfig, ChartTooltipContent, {
  labelFormatter: (i) => capacityData.value[i]?.label ?? '',
})
</script>

<template>
  <div v-if="sortedHikes.length >= 2" class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6 min-w-0">
    <!-- Signups Over Time -->
    <div class="rounded-lg border bg-card p-4 min-w-0 overflow-hidden">
      <h3 class="text-sm font-semibold mb-3 text-foreground">Signups</h3>
      <ChartContainer :config="signupsOverTimeConfig" class="h-48 w-full" cursor>
        <VisXYContainer :data="signupsOverTimeData">
          <VisArea
            :x="(_, i) => i"
            :y="(d) => d.confirmed"
            color="hsl(221, 83%, 53%)"
            :opacity="0.1"
          />
          <VisLine
            :x="(_, i) => i"
            :y="(d) => d.confirmed"
            color="hsl(221, 83%, 53%)"
            :line-width="2"
          />
          <VisArea
            :x="(_, i) => i"
            :y="(d) => d.checked_in"
            color="hsl(142, 71%, 45%)"
            :opacity="0.15"
          />
          <VisLine
            :x="(_, i) => i"
            :y="(d) => d.checked_in"
            color="hsl(142, 71%, 45%)"
            :line-width="2"
          />
          <VisAxis
            type="x"
            :tick-line="false"
            :domain-line="false"
            :grid-line="false"
            :num-ticks="Math.min(signupsOverTimeData.length, 6)"
            :tick-format="(i) => signupsOverTimeData[i]?.label ?? ''"
          />
          <VisAxis
            type="y"
            :num-ticks="4"
            :tick-line="false"
            :domain-line="false"
          />
          <ChartTooltip />
          <ChartCrosshair :template="signupsOverTimeTooltip" color="hsl(221, 83%, 53%)" />
        </VisXYContainer>
      </ChartContainer>
    </div>

    <!-- Attendance Rate Over Time -->
    <div class="rounded-lg border bg-card p-4 min-w-0 overflow-hidden">
      <h3 class="text-sm font-semibold mb-3 text-foreground">Attendance Rate</h3>
      <ChartContainer :config="attendanceConfig" class="h-48 w-full" cursor>
        <VisXYContainer :data="attendanceData" :y-domain="[0, 100]">
          <VisArea
            :x="(_, i) => i"
            :y="(d) => d.noShow"
            color="hsl(0, 84%, 60%)"
            :opacity="0.1"
          />
          <VisLine
            :x="(_, i) => i"
            :y="(d) => d.noShow"
            color="hsl(0, 84%, 60%)"
            :line-width="2"
          />
          <VisArea
            :x="(_, i) => i"
            :y="(d) => d.attendance"
            color="hsl(142, 71%, 45%)"
            :opacity="0.15"
          />
          <VisLine
            :x="(_, i) => i"
            :y="(d) => d.attendance"
            color="hsl(142, 71%, 45%)"
            :line-width="2"
          />
          <VisAxis
            type="x"
            :tick-line="false"
            :domain-line="false"
            :grid-line="false"
            :num-ticks="Math.min(attendanceData.length, 6)"
            :tick-format="(i) => attendanceData[i]?.label ?? ''"
          />
          <VisAxis
            type="y"
            :num-ticks="4"
            :tick-line="false"
            :domain-line="false"
            :tick-format="(d) => `${d}%`"
          />
          <ChartTooltip />
          <ChartCrosshair :template="attendanceTooltip" color="hsl(142, 71%, 45%)" />
        </VisXYContainer>
      </ChartContainer>
    </div>

    <!-- Transport Breakdown -->
    <div class="rounded-lg border bg-card p-4 min-w-0 overflow-hidden">
      <h3 class="text-sm font-semibold mb-3 text-foreground">Transport Breakdown</h3>
      <ChartContainer :config="transportConfig" class="h-48 w-full" cursor>
        <VisXYContainer :data="transportData">
          <VisStackedBar
            :x="(_, i) => i"
            :y="[(d) => d.drivers, (d) => d.passengers, (d) => d.selfTransport, (d) => d.waitlisted]"
            :color="['hsl(220,100%,78%)', 'hsl(275,83%,58%)', 'hsl(25, 95%, 53%)', 'hsl(0, 84%, 60%)']"
            :bar-padding="0.35"
            :rounded-corners="2"
          />
          <VisAxis
            type="x"
            :tick-line="false"
            :domain-line="false"
            :grid-line="false"
            :num-ticks="Math.min(transportData.length, 6)"
            :tick-format="(i) => transportData[i]?.label ?? ''"
          />
          <VisAxis
            type="y"
            :num-ticks="4"
            :tick-line="false"
            :domain-line="false"
          />
          <ChartTooltip />
          <ChartCrosshair :template="transportTooltip" color="hsl(221, 83%, 53%)" />
        </VisXYContainer>
      </ChartContainer>
      <div class="flex flex-wrap gap-3 mt-2 text-xs text-muted-foreground justify-center">
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(220, 100%, 78%)" /> Drivers</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(275, 83%, 58%)" /> Passengers</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(25, 95%, 53%)" /> Self</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(0, 84%, 60%)" /> Waitlisted</span>
      </div>
    </div>
    <!-- Capacity Utilization Over Time -->
    <div class="rounded-lg border bg-card p-4 min-w-0 overflow-hidden">
      <h3 class="text-sm font-semibold mb-3 text-foreground">Capacity Utilization</h3>
      <ChartContainer :config="capacityConfig" class="h-48 w-full" cursor>
        <VisXYContainer :data="capacityData">
          <VisArea
            :x="(_, i) => i"
            :y="(d) => d.utilization"
            color="hsl(262, 83%, 58%)"
            :opacity="0.15"
          />
          <VisLine
            :x="(_, i) => i"
            :y="(d) => d.utilization"
            color="hsl(262, 83%, 58%)"
            :line-width="2"
          />
          <VisLine
            :x="(_, i) => i"
            :y="() => 100"
            color="hsl(0, 0%, 50%)"
            :line-width="1"
            :line-dash-array="[4, 4]"
          />
          <VisAxis
            type="x"
            :tick-line="false"
            :domain-line="false"
            :grid-line="false"
            :num-ticks="Math.min(capacityData.length, 6)"
            :tick-format="(i) => capacityData[i]?.label ?? ''"
          />
          <VisAxis
            type="y"
            :num-ticks="4"
            :tick-line="false"
            :domain-line="false"
            :tick-format="(d) => `${d}%`"
          />
          <ChartTooltip />
          <ChartCrosshair :template="capacityTooltip" color="hsl(262, 83%, 58%)" />
        </VisXYContainer>
      </ChartContainer>
    </div>

    <!-- Signups by Difficulty -->
    <div class="rounded-lg border bg-card p-4 min-w-0 overflow-hidden">
      <h3 class="text-sm font-semibold mb-3 text-foreground">Signups by Difficulty</h3>
      <ChartContainer :config="signupsByDifficultyConfig" class="h-48 w-full" cursor>
        <VisXYContainer :data="signupsByDifficultyData">
          <VisGroupedBar
            :x="(_, i) => i"
            :y="[(d) => d.signups, (d) => d.checked_in]"
            :color="['hsl(221, 83%, 53%)', 'hsl(142, 71%, 45%)']"
            :bar-padding="0.35"
            :rounded-corners="2"
          />
          <VisAxis
            type="x"
            :tick-line="false"
            :domain-line="false"
            :grid-line="false"
            :num-ticks="signupsByDifficultyData.length"
            :tick-format="(i) => signupsByDifficultyData[i]?.label ?? ''"
          />
          <VisAxis
            type="y"
            :num-ticks="4"
            :tick-line="false"
            :domain-line="false"
          />
          <ChartTooltip />
          <ChartCrosshair :template="signupsByDifficultyTooltip" color="hsl(221, 83%, 53%)" />
        </VisXYContainer>
      </ChartContainer>
      <div class="flex flex-wrap gap-3 mt-2 text-xs text-muted-foreground justify-center">
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(221, 83%, 53%)" /> Signups</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(142, 71%, 45%)" /> Checked In</span>
      </div>
    </div>

    <!-- Hiker Frequency Distribution -->
    <div v-if="frequencyData.length" class="rounded-lg border bg-card p-4 min-w-0 overflow-hidden">
      <h3 class="text-lg font-bold mb-1">Hiker Frequency</h3>
      <p v-if="attendanceFrequency" class="text-xs text-muted-foreground mb-3">
        {{ Math.round(attendanceFrequency.repeat_rate * 100) }}% repeat rate
        ({{ attendanceFrequency.total_members }} unique hikers)
      </p>
      <ChartContainer :config="frequencyConfig" class="h-48 w-full" cursor>
        <VisXYContainer :data="frequencyData">
          <VisStackedBar
            :x="(_, i) => i"
            :y="[(d) => d.members]"
            :color="['hsl(221, 83%, 53%)']"
            :bar-padding="0.35"
            :rounded-corners="2"
          />
          <VisAxis
            type="x"
            :tick-line="false"
            :domain-line="false"
            :grid-line="false"
            :num-ticks="frequencyData.length"
            :tick-format="() => ''"
          />
          <VisAxis
            type="y"
            :num-ticks="4"
            :tick-line="false"
            :domain-line="false"
          />
          <ChartTooltip />
          <ChartCrosshair :template="frequencyTooltip" color="hsl(221, 83%, 53%)" />
        </VisXYContainer>
      </ChartContainer>
      <div class="flex justify-between mt-1 px-6">
        <button
          v-for="d in frequencyData"
          :key="d.label"
          class="flex-1 text-center text-xs py-1.5 rounded-sm cursor-pointer transition-colors text-muted-foreground hover:bg-muted hover:text-foreground"
          @click="emit('select-frequency', parseInt(d.label))"
        >
          {{ d.label }}x
          <span class="block text-[10px] opacity-70">{{ d.members }}</span>
        </button>
      </div>
      <p class="text-[10px] text-muted-foreground text-center mt-0.5">Hikes attended (click to view)</p>
    </div>
  </div>
</template>
