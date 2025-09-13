<template>
  <div class="space-y-4 mb-4">
    <p>Signups: <strong>{{ numCheckedInSignups }}</strong> checked in / <strong>{{ numSignups }}</strong> total</p>
    <p>Passengers: <strong>{{ numCheckedInPassengers }}</strong> checked in / <strong>{{ numPassengers }}</strong> total</p>
    <p>Drivers: <strong>{{ numCheckedInDrivers }}</strong> checked in / <strong>{{ numDrivers }}</strong> total</p>
    <p>Self-transports: <strong>{{ numCheckedInSelf }}</strong> checked in / <strong>{{ numSelf }}</strong> total</p>
    <p>Passenger Capacity: <strong>{{ passengerCapacity }}</strong> </p>

    <!-- Capacity Indicator -->
    <div class="flex items-center space-x-3">
      <Progress v-model="barWidth" :max="100" class="flex-1 [&_[data-slot=progress]]:bg-gray-200"
            :class="overCapacity
        ? '[&_[data-slot=progress-indicator]]:bg-red-500'
        : '[&_[data-slot=progress-indicator]]:bg-primary'"/>
      <span class="text-sm font-medium">{{ percentCapacity }}%</span>
    </div>
    <p v-if="overCapacity">Waitlisted Passengers: <strong>{{ waitlistedPassengers }}</strong> </p>
  </div>
</template>

<script setup>
import {computed, ref} from 'vue'
import { Progress } from '@/components/ui/progress'

const props = defineProps({
  users:             { type: Array, required: true },
  passengerCapacity: { type: Number, required: true }
})

const numSignups = computed(() => props.users.length)
const numCheckedInSignups = computed(() =>
    props.users.filter(u => u.is_checked_in === true).length
)
const numPassengers = computed(() =>
    props.users.filter(u => u.transport_type === 'passenger').length
)
const numCheckedInPassengers = computed(() =>
    props.users.filter(u => (u.transport_type === 'passenger' && u.is_checked_in === true)).length
)
const numDrivers = computed(() =>
    props.users.filter(u => u.transport_type === 'driver').length
)
const numCheckedInDrivers = computed(() =>
    props.users.filter(u => (u.transport_type === 'driver' && u.is_checked_in === true)).length
)
const numSelf = computed(() =>
    props.users.filter(u => u.transport_type === 'self').length
)
const numCheckedInSelf = computed(() =>
    props.users.filter(u => (u.transport_type === 'self' && u.is_checked_in === true)).length
)

let percentCapacity = 0
let overCapacity = false
const barWidth = ref(0)
if (props.passengerCapacity === 0) {
  percentCapacity = 0
  barWidth.value = 0
} else {
  percentCapacity = ((numPassengers.value / props.passengerCapacity) * 100).toFixed(2)
  if (percentCapacity > 100 ) {
    overCapacity = true
    barWidth.value = 100
  } else {
    barWidth.value = Math.round(percentCapacity)
  }
}

const waitlistedPassengers = computed(() => {
  return numPassengers.value - props.passengerCapacity > 0
    ? numPassengers.value - props.passengerCapacity
    : 0
})
</script>
