<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-3">
      <!-- Total signups -->
      <div class="rounded-lg border bg-muted/30 px-4 py-3 space-y-2">
        <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Users class="h-3.5 w-3.5" /> Total
        </div>
        <template v-if="showCheckinStats">
          <div class="flex items-end justify-between gap-1">
            <p class="text-2xl font-bold tabular-nums leading-none">
              {{ numCheckedInSignups }}<span class="text-base font-normal text-muted-foreground"> / {{ numSignups }}</span>
            </p>
            <span class="text-xs font-semibold tabular-nums text-muted-foreground mb-0.5">{{ pctSignups }}%</span>
          </div>
          <p class="text-[10px] text-muted-foreground/70">checked in / signed up</p>
          <div class="h-1 rounded-full bg-border overflow-hidden">
            <div class="h-full rounded-full bg-primary transition-all" :style="{ width: pctSignups + '%' }" />
          </div>
        </template>
        <p v-else class="text-2xl font-bold tabular-nums leading-none">{{ numSignups }}</p>
      </div>

      <!-- Drivers -->
      <div class="rounded-lg border bg-muted/30 px-4 py-3 space-y-2">
        <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Car class="h-3.5 w-3.5" /> Drivers
        </div>
        <template v-if="showCheckinStats">
          <div class="flex items-end justify-between gap-1">
            <p class="text-2xl font-bold tabular-nums leading-none">
              {{ numCheckedInDrivers }}<span class="text-base font-normal text-muted-foreground"> / {{ numDrivers }}</span>
            </p>
            <span class="text-xs font-semibold tabular-nums text-muted-foreground mb-0.5">{{ pctDrivers }}%</span>
          </div>
          <p class="text-[10px] text-muted-foreground/70">checked in / signed up</p>
          <div class="h-1 rounded-full bg-border overflow-hidden">
            <div class="h-full rounded-full bg-primary transition-all" :style="{ width: pctDrivers + '%' }" />
          </div>
        </template>
        <p v-else class="text-2xl font-bold tabular-nums leading-none">{{ numDrivers }}</p>
      </div>

      <!-- Passengers -->
      <div class="rounded-lg border bg-muted/30 px-4 py-3 space-y-2">
        <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
          <UserCheck class="h-3.5 w-3.5" /> Passengers
        </div>
        <template v-if="showCheckinStats">
          <div class="flex items-end justify-between gap-1">
            <p class="text-2xl font-bold tabular-nums leading-none">
              {{ numCheckedInPassengers }}<span class="text-base font-normal text-muted-foreground"> / {{ numPassengers }}</span>
            </p>
            <span class="text-xs font-semibold tabular-nums text-muted-foreground mb-0.5">{{ pctPassengers }}%</span>
          </div>
          <p class="text-[10px] text-muted-foreground/70">checked in / signed up</p>
          <div class="h-1 rounded-full bg-border overflow-hidden">
            <div class="h-full rounded-full bg-primary transition-all" :style="{ width: pctPassengers + '%' }" />
          </div>
        </template>
        <p v-else class="text-2xl font-bold tabular-nums leading-none">{{ numPassengers }}</p>
      </div>

      <!-- Self-transport -->
      <div class="rounded-lg border bg-muted/30 px-4 py-3 space-y-2">
        <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
          <PersonStanding class="h-3.5 w-3.5" /> Self-transport
        </div>
        <template v-if="showCheckinStats">
          <div class="flex items-end justify-between gap-1">
            <p class="text-2xl font-bold tabular-nums leading-none">
              {{ numCheckedInSelf }}<span class="text-base font-normal text-muted-foreground"> / {{ numSelf }}</span>
            </p>
            <span class="text-xs font-semibold tabular-nums text-muted-foreground mb-0.5">{{ pctSelf }}%</span>
          </div>
          <p class="text-[10px] text-muted-foreground/70">checked in / signed up</p>
          <div class="h-1 rounded-full bg-border overflow-hidden">
            <div class="h-full rounded-full bg-primary transition-all" :style="{ width: pctSelf + '%' }" />
          </div>
        </template>
        <p v-else class="text-2xl font-bold tabular-nums leading-none">{{ numSelf }}</p>
      </div>
    </div>

    <!-- Capacity bar -->
    <div class="rounded-lg border bg-muted/30 px-4 py-3 space-y-2">
      <div class="flex items-center justify-between text-xs">
        <div class="flex items-center gap-1.5 text-muted-foreground">
          <Gauge class="h-3.5 w-3.5" />
          <span>Passenger capacity</span>
        </div>
        <span
          class="font-semibold tabular-nums"
          :class="overCapacity ? 'text-destructive' : 'text-foreground'"
        >
          {{ numPassengers }} / {{ passengerCapacity }}
          <span class="text-muted-foreground font-normal">({{ percentCapacity }}%)</span>
        </span>
      </div>
      <Progress
        v-model="barWidth"
        :max="100"
        class="h-2"
        :class="overCapacity ? '[&_[data-slot=progress-indicator]]:bg-destructive' : ''"
      />
      <p v-if="waitlistedPassengers > 0" class="text-xs text-muted-foreground">
        {{ waitlistedPassengers }} passenger{{ waitlistedPassengers !== 1 ? 's' : '' }} on waitlist
      </p>
      <p v-if="confirmedOverCapacity" class="text-xs font-semibold text-destructive">
        Warning: {{ confirmedOverCapacity }} confirmed passenger{{ confirmedOverCapacity !== 1 ? 's' : '' }} over capacity
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Progress } from '@/components/ui/progress'
import { Users, Car, UserCheck, PersonStanding, Gauge } from 'lucide-vue-next'

const props = defineProps({
  users: { type: Array, required: true },
  passengerCapacity: { type: Number, required: true },
  overCapacityPassengers: { type: Number, required: false, default: 0 },
  hikeDate: { type: String, default: null },
})

const showCheckinStats = computed(() => {
  if (!props.hikeDate) return false
  const hikeTime = new Date(props.hikeDate).getTime()
  return Date.now() >= hikeTime - 30 * 60 * 1000
})

const numSignups = computed(() => props.users.length)
const numCheckedInSignups = computed(() => props.users.filter(u => u.is_checked_in).length)
const numPassengers = computed(() => props.users.filter(u => u.transport_type === 'passenger').length)
const numCheckedInPassengers = computed(() => props.users.filter(u => u.transport_type === 'passenger' && u.is_checked_in).length)
const numDrivers = computed(() => props.users.filter(u => u.transport_type === 'driver').length)
const numCheckedInDrivers = computed(() => props.users.filter(u => u.transport_type === 'driver' && u.is_checked_in).length)
const numSelf = computed(() => props.users.filter(u => u.transport_type === 'self').length)
const numCheckedInSelf = computed(() => props.users.filter(u => u.transport_type === 'self' && u.is_checked_in).length)
const confirmedOverCapacity = computed(() => props.overCapacityPassengers || 0)

function pct(checked, total) {
  return total === 0 ? 0 : Math.round((checked / total) * 100)
}
const pctSignups   = computed(() => pct(numCheckedInSignups.value,   numSignups.value))
const pctDrivers   = computed(() => pct(numCheckedInDrivers.value,   numDrivers.value))
const pctPassengers = computed(() => pct(numCheckedInPassengers.value, numPassengers.value))
const pctSelf      = computed(() => pct(numCheckedInSelf.value,      numSelf.value))

const percentCapacity = computed(() => {
  if (props.passengerCapacity === 0) return 0
  return ((numPassengers.value / props.passengerCapacity) * 100).toFixed(0)
})
const overCapacity = computed(() => Number(percentCapacity.value) > 100)
const barWidth = computed(() => Math.min(Number(percentCapacity.value), 100))
const waitlistedPassengers = computed(() =>
  Math.max(numPassengers.value - props.passengerCapacity, 0)
)
</script>
