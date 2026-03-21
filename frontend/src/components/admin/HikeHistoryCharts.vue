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
})

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
    selfTransport: h.num_confirmed - h.num_drivers - h.num_passengers,
    waitlisted: h.num_waitlisted,
  }))
)

const transportConfig = {
  drivers: { label: 'Drivers', color: 'hsl(221, 83%, 53%)' },
  passengers: { label: 'Passengers', color: 'hsl(262, 83%, 58%)' },
  selfTransport: { label: 'Self-Transport', color: 'hsl(25, 95%, 53%)' },
  waitlisted: { label: 'Waitlisted', color: 'hsl(0, 84%, 60%)' },
}

const transportTooltip = componentToString(transportConfig, ChartTooltipContent, {
  labelFormatter: (i) => transportData.value[i]?.label ?? '',
})

// Difficulty colors
const difficultyColors = [
  'hsl(142, 71%, 45%)',  // Easy - green
  'hsl(45, 93%, 47%)',   // Moderate - yellow
  'hsl(25, 95%, 53%)',   // Difficult - orange
  'hsl(0, 84%, 60%)',    // Very Difficult - red
]

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

// Attendance rate by difficulty
const attendanceByDifficultyData = computed(() => {
  const buckets = {}
  for (const h of sortedHikes.value) {
    if (h.trail_difficulty == null) continue
    const label = difficulties[h.trail_difficulty] || 'Unknown'
    if (!buckets[label]) buckets[label] = { label, confirmed: 0, checked_in: 0, difficulty: h.trail_difficulty }
    buckets[label].confirmed += h.num_confirmed
    buckets[label].checked_in += h.num_checked_in
  }
  return Object.values(buckets)
    .sort((a, b) => a.difficulty - b.difficulty)
    .map(b => ({
      label: b.label,
      attendance: b.confirmed > 0 ? Math.round((b.checked_in / b.confirmed) * 100) : 0,
    }))
})

const attendanceByDifficultyConfig = {
  attendance: { label: 'Attendance %', color: 'hsl(142, 71%, 45%)' },
}

const attendanceByDifficultyTooltip = componentToString(attendanceByDifficultyConfig, ChartTooltipContent, {
  labelFormatter: (i) => attendanceByDifficultyData.value[i]?.label ?? '',
})

// Capacity utilization over time
// (num_passengers) / passenger_capacity * 100
// Over 100% means there was a waitlist
const capacityData = computed(() =>
  sortedHikes.value
    .filter(h => h.passenger_capacity > 0)
    .map(h => {
      const demand = h.num_passengers + h.num_waitlisted
      const utilization = Math.round((demand / h.passenger_capacity) * 100)
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
  <div v-if="sortedHikes.length >= 2" class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
    <!-- Signups Over Time -->
    <div class="border rounded-md p-4">
      <h3 class="text-lg font-bold mb-3">Signups</h3>
      <ChartContainer :config="signupsOverTimeConfig" class="h-48 aspect-auto" cursor>
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
    <div class="border rounded-md p-4">
      <h3 class="text-lg font-bold mb-3">Attendance Rate</h3>
      <ChartContainer :config="attendanceConfig" class="h-48 aspect-auto" cursor>
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
    <div class="border rounded-md p-4">
      <h3 class="text-lg font-bold mb-3">Transport Breakdown</h3>
      <ChartContainer :config="transportConfig" class="h-48 aspect-auto" cursor>
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
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(221, 83%, 53%)" /> Drivers</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(262, 83%, 58%)" /> Passengers</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(25, 95%, 53%)" /> Self</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded-sm" style="background: hsl(0, 84%, 60%)" /> Waitlisted</span>
      </div>
    </div>
    <!-- Capacity Utilization Over Time -->
    <div class="border rounded-md p-4">
      <h3 class="text-lg font-bold mb-3">Capacity Utilization</h3>
      <ChartContainer :config="capacityConfig" class="h-48 aspect-auto" cursor>
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
    <div class="border rounded-md p-4">
      <h3 class="text-lg font-bold mb-3">Signups by Difficulty</h3>
      <ChartContainer :config="signupsByDifficultyConfig" class="h-48 aspect-auto" cursor>
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

    <!-- Attendance Rate by Difficulty -->
    <div class="border rounded-md p-4">
      <h3 class="text-lg font-bold mb-3">Attendance by Difficulty</h3>
      <ChartContainer :config="attendanceByDifficultyConfig" class="h-48 aspect-auto" cursor>
        <VisXYContainer :data="attendanceByDifficultyData" :y-domain="[0, 100]">
          <VisStackedBar
            :x="(_, i) => i"
            :y="[(d) => d.attendance]"
            :color="attendanceByDifficultyData.map((d, i) => difficultyColors[i] || 'hsl(221, 83%, 53%)')"
            :bar-padding="0.35"
            :rounded-corners="2"
          />
          <VisAxis
            type="x"
            :tick-line="false"
            :domain-line="false"
            :grid-line="false"
            :num-ticks="attendanceByDifficultyData.length"
            :tick-format="(i) => attendanceByDifficultyData[i]?.label ?? ''"
          />
          <VisAxis
            type="y"
            :num-ticks="4"
            :tick-line="false"
            :domain-line="false"
            :tick-format="(d) => `${d}%`"
          />
          <ChartTooltip />
          <ChartCrosshair :template="attendanceByDifficultyTooltip" color="hsl(142, 71%, 45%)" />
        </VisXYContainer>
      </ChartContainer>
    </div>
  </div>
</template>
