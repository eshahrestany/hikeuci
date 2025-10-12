<script setup>
import { Badge } from '@/components/ui/badge'
import SignupStats from "@/components/admin/SignupStats.vue"
import SignupTable from "@/components/admin/SignupTable.vue";

const props = defineProps({
  signupData: { type: Object, required: true }
})

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

  <SignupTable mode="signup" :users="signupData.users"/>
</template>
