<script setup>
import { reactive, computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import SignupStats from "@/components/admin/SignupStats.vue"
import {ChevronDown, ChevronRight} from "lucide-vue-next";

const props = defineProps({
  signupData: { type: Object, required: true }
})

const show = reactive({
  passengers: false,
  drivers: false,
  self: false
})

const passengers = computed(() =>
  props.signupData.users
    .filter(u => u.transport_type === 'passenger')
    .map(u => u.name)
)

const drivers = computed(() =>
  props.signupData.users
    .filter(u => u.transport_type === 'driver')
    .map(u => u.name)
)

const selfTransports = computed(() =>
  props.signupData.users
    .filter(u => u.transport_type === 'self')
    .map(u => u.name)
)
</script>

<template>
  <p class="flex justify-center items-center font-semibold text-xl mb-6">
    Current Phase:
    <Badge class="text-md ml-2">Signup</Badge>
  </p>
  <div class="md:grid grid-cols-2 gap-4">
    <div class="text-center text-lg font-semibold underline">
      Trail: {{ signupData.trail_name }}
      <img
        class="mt-2 w-auto object-cover rounded-md mb-2"
        :src="`/api/images/uploads/${signupData.trail_id}`"
        :alt="`image of ${ signupData.trail_name}`"
      />
    </div>
    <SignupStats
      :users="signupData.users"
      :passenger-capacity="signupData.passenger_capacity"
    />
  </div>

  <!-- expandable lists -->
  <div class="text-center text-lg font-semibold py-2">Signed-up member list:</div>
  <div class="grid grid-cols-3 gap-4">
    <div class="mx-auto">
      <Button variant="outline" @click="show.passengers = !show.passengers">
        <ChevronDown v-if="show.passengers"/>
        <ChevronRight v-else />
        {{ show.passengers ? 'Hide Passengers' : 'See Passengers' }}
      </Button>
      <ul v-if="show.passengers" class="list-disc list-inside text-sm ml-4 mt-2">
        <li v-for="(name, idx) in passengers" :key="idx">{{ name }}</li>
      </ul>
    </div>

    <div class="mx-auto">
      <Button variant="outline" @click="show.drivers = !show.drivers">
        <ChevronDown v-if="show.drivers"/>
        <ChevronRight v-else />
        {{ show.drivers ? 'Hide Drivers' : 'See Drivers' }}
      </Button>
      <ul v-if="show.drivers" class="list-disc list-inside text-sm ml-4 mt-2">
        <li v-for="(name, idx) in drivers" :key="idx">{{ name }}</li>
      </ul>
    </div>

    <div class="mx-auto">
      <Button variant="outline" @click="show.self = !show.self">
        <ChevronDown v-if="show.self"/>
        <ChevronRight v-else />
        {{ show.self ? 'Hide Self-Transports' : 'See Self-Transports' }}
      </Button>
      <ul v-if="show.self" class="list-disc list-inside text-sm ml-4 mt-2">
        <li v-for="(name, idx) in selfTransports" :key="idx">{{ name }}</li>
      </ul>
    </div>
  </div>
</template>
