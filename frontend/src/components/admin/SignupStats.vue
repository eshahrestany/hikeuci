<template>
  <div class="space-y-4 mb-4">
    <p>Total Signups: {{ numSignups }}</p>
    <p>Passengers: {{ numPassengers }}</p>
    <p>Drivers: {{ numDrivers }}</p>
    <p>Self-transports: {{ numSelf }}</p>
    <p>Passenger Capacity: {{ passengerCapacity }}</p>

    <!-- Capacity Indicator -->
    <div class="flex items-center space-x-3">
      <Progress v-model="barWidth" :max="100" class="flex-1 [&_[data-slot=progress]]:bg-gray-200"
            :class="overCapacity
        ? '[&_[data-slot=progress-indicator]]:bg-red-500'
        : '[&_[data-slot=progress-indicator]]:bg-primary'"/>
      <span class="text-sm font-medium">{{ percentCapacity }}%</span>
    </div>
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
const numPassengers = computed(() =>
  props.users.filter(u => u.transport_type === 'passenger').length
)
const numDrivers = computed(() =>
  props.users.filter(u => u.transport_type === 'driver').length
)
const numSelf = computed(() =>
  props.users.filter(u => u.transport_type === 'self').length
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
</script>
