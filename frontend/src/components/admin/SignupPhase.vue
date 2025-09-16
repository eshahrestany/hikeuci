<script setup>
import { reactive, computed } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
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
  <div>
    <p class="flex justify-center items-center font-semibold text-xl mb-2">
      Current Phase:
      <Badge class="text-md ml-2">Signup</Badge>
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
        <div class="space-y-2 align-top">
            <Button variant="link" @click="show.passengers = !show.passengers">
              <ChevronDown v-if="show.passengers"/>
              <ChevronRight v-else />
              {{ show.passengers ? 'Hide Passengers' : 'See Passengers' }}
            </Button>
            <ul v-if="show.passengers" class="list-disc list-inside text-sm ml-4">
              <li v-for="(name, idx) in passengers" :key="idx">{{ name }}</li>
            </ul>
          <Button variant="link" @click="show.drivers = !show.drivers">
            <ChevronDown v-if="show.drivers"/>
            <ChevronRight v-else />
            {{ show.drivers ? 'Hide Drivers' : 'See Drivers' }}
          </Button>
          <ul v-if="show.drivers" class="list-disc list-inside text-sm ml-4">
            <li v-for="(name, idx) in drivers" :key="idx">{{ name }}</li>
          </ul>

          <Button variant="link" @click="show.self = !show.self">
            <ChevronDown v-if="show.self"/>
            <ChevronRight v-else />
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
