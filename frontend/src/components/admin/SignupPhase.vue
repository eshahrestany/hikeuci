<script setup>
import { reactive, computed } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import SignupStats from "@/components/admin/SignupStats.vue"

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
    .map(u => `${u.first_name} ${u.last_name}`)
)

const drivers = computed(() =>
  props.signupData.users
    .filter(u => u.transport_type === 'driver')
    .map(u => `${u.first_name} ${u.last_name}`)
)

const selfTransports = computed(() =>
  props.signupData.users
    .filter(u => u.transport_type === 'self')
    .map(u => `${u.first_name} ${u.last_name}`)
)
</script>

<template>
  <div>
    <p class="font-semibold text-xl mb-2">
      Current Phase:
      <Badge class="text-md">Signup</Badge>
    </p>
    <Card>
      <CardHeader>
        <img
          class="h-36 w-full object-cover rounded-md mb-2"
          :src="`/api/images/uploads/${signupData.trail_id}.png`"
          :alt="signupData.trail_name"
        />
        <CardTitle>{{ signupData.trail_name }}</CardTitle>
      </CardHeader>
      <CardContent>
        <!-- summary + bar -->
        <SignupStats
          :users="signupData.users"
          :passenger-capacity="signupData.passenger_capacity"
        />

        <!-- expandable lists -->
        <div class="space-y-2">
          <Button variant="link" @click="show.passengers = !show.passengers">
            {{ show.passengers ? 'Hide Passengers' : 'See Passengers' }}
          </Button>
          <ul v-if="show.passengers" class="list-disc list-inside text-sm ml-4">
            <li v-for="(name, idx) in passengers" :key="idx">{{ name }}</li>
          </ul>

          <Button variant="link" @click="show.drivers = !show.drivers">
            {{ show.drivers ? 'Hide Drivers' : 'See Drivers' }}
          </Button>
          <ul v-if="show.drivers" class="list-disc list-inside text-sm ml-4">
            <li v-for="(name, idx) in drivers" :key="idx">{{ name }}</li>
          </ul>

          <Button variant="link" @click="show.self = !show.self">
            {{ show.self ? 'Hide Self-Transports' : 'See Self-Transports' }}
          </Button>
          <ul v-if="show.self" class="list-disc list-inside text-sm ml-4">
            <li v-for="(name, idx) in selfTransports" :key="idx">{{ name }}</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
