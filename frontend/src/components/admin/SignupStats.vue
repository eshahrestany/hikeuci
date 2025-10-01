<template>
  <div>
    <p class="text-center text-lg font-semibold underline mb-2">Signup & Attendance Statistics</p>
    <div class="space-y-2 md:space-y-3 border-1 px-2 py-3 mb-2 rounded-md">
      <p><span class="underline font-semibold">Signups (total):</span> <span class="font-bold">{{ numCheckedInSignups }}</span> checked in / <span class="font-bold">{{ numSignups }}</span> signed up</p>
      <p><span class="underline font-semibold">Passengers:</span> <span class="font-bold">{{ numCheckedInPassengers }}</span> checked in / <span class="font-bold">{{ numPassengers }}</span> signed up</p>
      <p><span class="underline font-semibold">Drivers:</span> <span class="font-bold">{{ numCheckedInDrivers }}</span> checked in / <span class="font-bold">{{ numDrivers }}</span> signed up</p>
      <p><span class="underline font-semibold">Self-transports:</span> <span class="font-bold">{{ numCheckedInSelf }}</span> checked in / <span class="font-bold">{{ numSelf }}</span> signed up</p>
      <p><span class="underline font-semibold">Capacity:</span> <span class="font-bold">{{ passengerCapacity}}</span> passengers</p>
      <!-- Capacity Indicator -->
      <div class="flex items-center space-x-3">
        <Progress v-model="barWidth" :max="100" class="flex-1 [&_[data-slot=progress]]:bg-gray-200"
              :class="overCapacity
          ? '[&_[data-slot=progress-indicator]]:bg-red-500'
          : '[&_[data-slot=progress-indicator]]:bg-primary'"/>
        <span class="text-xs md:text-sm font-medium">{{ percentCapacity }}%</span>
      </div>
      <p v-if="overCapacity"><span class="underline font-semibold">Waitlisted:</span> <span class="font-bold">{{ }}</span>{{ waitlistedPassengers }} passengers</p>
      <p v-if="confirmedOverCapacity" class="text-sm text-red-600 font-semibold">Warning: There are {{ confirmedOverCapacity }} confirmed passengers over capacity.</p>
    </div>
  </div>
</template>

<script setup>
import {computed, ref} from 'vue'
import {Progress} from '@/components/ui/progress'

const props = defineProps({
  users: {type: Array, required: true},
  passengerCapacity: {type: Number, required: true},
  overCapacityPassengers: {type: Number, required: false, default: 0}
})

console.log(props)

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

const confirmedOverCapacity = computed(() =>
    props.overCapacityPassengers || 0
)

let percentCapacity = 0
let overCapacity = false
const barWidth = ref(0)
if (props.passengerCapacity === 0) {
  percentCapacity = 0
  barWidth.value = 0
} else {
  percentCapacity = ((numPassengers.value / props.passengerCapacity) * 100).toFixed(2)
  if (percentCapacity > 100) {
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