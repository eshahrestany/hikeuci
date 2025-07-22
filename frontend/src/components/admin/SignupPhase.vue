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
        <div class="space-y-1 mb-4">
          <p>Total Signups: {{ signupData.num_signups }}</p>
          <p>Passengers: {{ signupData.num_passengers }}</p>
          <p>Drivers: {{ signupData.num_drivers }}</p>
          <p>Passenger Capacity: {{ signupData.passenger_capacity }}</p>
        </div>
        <div class="space-y-2">
          <Button variant="link" @click="show.passengers = !show.passengers">
            {{ show.passengers ? 'Hide Passengers' : 'See Passengers' }}
          </Button>
          <ul v-if="show.passengers" class="list-disc list-inside text-sm ml-4">
            <li v-for="(name, idx) in signupData.passengers" :key="idx">
              {{ name }}
            </li>
          </ul>
          <Button variant="link" @click="show.drivers = !show.drivers">
            {{ show.drivers ? 'Hide Drivers' : 'See Drivers' }}
          </Button>
          <ul v-if="show.drivers" class="list-disc list-inside text-sm ml-4">
            <li v-for="(name, idx) in signupData.drivers" :key="idx">
              {{ name }}
            </li>
          </ul>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const props = defineProps({
  signupData: { type: Object, required: true }
})

const show = reactive({ passengers: false, drivers: false })
</script>
