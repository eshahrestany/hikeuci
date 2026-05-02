<template>
  <div class="rounded-xl border bg-card shadow-sm px-4 py-3 space-y-3">
    <!-- Header -->
    <div class="flex items-center gap-2">
      <UtensilsCrossed class="h-4 w-4 text-muted-foreground flex-shrink-0" />
      <span class="text-sm font-semibold leading-none">After-hike Food Interest</span>
      <span class="ml-auto text-xs font-semibold tabular-nums text-muted-foreground">
        {{ totalFood }} / {{ totalSignups }}
        <span class="font-normal">({{ overallPct }}%)</span>
      </span>
    </div>

    <!-- Warning banner -->
    <div
      v-if="showWarning"
      class="flex items-start gap-2 rounded-md border px-3 py-2 bg-amber-500/10 border-amber-500/30"
    >
      <TriangleAlert class="h-3.5 w-3.5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-px" />
      <p class="text-xs text-amber-700 dark:text-amber-400 leading-snug">{{ warningMessage }}</p>
    </div>

    <!-- Rows -->
    <div class="space-y-2.5">
      <!-- Passengers -->
      <div v-if="passengersTotal > 0" class="space-y-1">
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center gap-1.5 text-muted-foreground">
            <UserCheck class="h-3.5 w-3.5" />
            <span>Passengers</span>
          </div>
          <span class="tabular-nums font-medium">
            {{ passengersFoodPct }}%
            <span class="text-muted-foreground font-normal">({{ passengersFood }}/{{ passengersTotal }})</span>
          </span>
        </div>
        <div class="h-1.5 rounded-full bg-border overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="passengersFoodPct < 30 ? 'bg-muted-foreground/50' : 'bg-primary'"
            :style="{ width: passengersFoodPct + '%' }"
          />
        </div>
      </div>

      <!-- Drivers -->
      <div v-if="driversTotal > 0" class="space-y-1">
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center gap-1.5 text-muted-foreground">
            <Car class="h-3.5 w-3.5" />
            <span>Drivers</span>
          </div>
          <span class="tabular-nums font-medium">
            {{ driversFoodPct }}%
            <span class="text-muted-foreground font-normal">({{ driversFood }}/{{ driversTotal }})</span>
          </span>
        </div>
        <div class="h-1.5 rounded-full bg-border overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="driversFoodPct < 30 ? 'bg-muted-foreground/50' : 'bg-primary'"
            :style="{ width: driversFoodPct + '%' }"
          />
        </div>
      </div>

      <!-- Self-transport -->
      <div v-if="selfTotal > 0" class="space-y-1">
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center gap-1.5 text-muted-foreground">
            <PersonStanding class="h-3.5 w-3.5" />
            <span>Self-transport</span>
          </div>
          <span class="tabular-nums font-medium">
            {{ selfFoodPct }}%
            <span class="text-muted-foreground font-normal">({{ selfFood }}/{{ selfTotal }})</span>
          </span>
        </div>
        <div class="h-1.5 rounded-full bg-border overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="selfFoodPct < 30 ? 'bg-muted-foreground/50' : 'bg-primary'"
            :style="{ width: selfFoodPct + '%' }"
          />
        </div>
      </div>

      <p v-if="totalSignups === 0" class="text-xs text-muted-foreground">No signups yet.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { UtensilsCrossed, TriangleAlert, UserCheck, Car, PersonStanding } from 'lucide-vue-next'

const props = defineProps({
  users: { type: Array, required: true },
})

function pct(num, total) {
  return total === 0 ? 0 : Math.round((num / total) * 100)
}

const passengersTotal = computed(() => props.users.filter(u => u.transport_type === 'passenger').length)
const passengersFood  = computed(() => props.users.filter(u => u.transport_type === 'passenger' && u.food_interest).length)
const passengersFoodPct = computed(() => pct(passengersFood.value, passengersTotal.value))

const driversTotal = computed(() => props.users.filter(u => u.transport_type === 'driver').length)
const driversFood  = computed(() => props.users.filter(u => u.transport_type === 'driver' && u.food_interest).length)
const driversFoodPct = computed(() => pct(driversFood.value, driversTotal.value))

const selfTotal = computed(() => props.users.filter(u => u.transport_type === 'self').length)
const selfFood  = computed(() => props.users.filter(u => u.transport_type === 'self' && u.food_interest).length)
const selfFoodPct = computed(() => pct(selfFood.value, selfTotal.value))

const totalSignups = computed(() => props.users.length)
const totalFood    = computed(() => props.users.filter(u => u.food_interest).length)
const overallPct   = computed(() => pct(totalFood.value, totalSignups.value))

// Warn when the gap between passenger and driver food interest is >= 30 points
// and both groups have at least 2 members (too few makes percentages meaningless).
const showWarning = computed(() =>
  passengersTotal.value >= 2 &&
  driversTotal.value >= 2 &&
  Math.abs(passengersFoodPct.value - driversFoodPct.value) >= 30
)

const warningMessage = computed(() => {
  if (!showWarning.value) return ''
  if (passengersFoodPct.value > driversFoodPct.value) {
    return `${passengersFoodPct.value}% of passengers want food after the hike, but only ${driversFoodPct.value}% of drivers do — post-hike lunch coordination may be difficult.`
  }
  return `${driversFoodPct.value}% of drivers want food after the hike, but only ${passengersFoodPct.value}% of passengers do — lunch turnout may be lower than drivers expect.`
})
</script>
