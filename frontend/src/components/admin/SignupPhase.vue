<script setup>
import { Badge } from '@/components/ui/badge'
import SignupStats from "@/components/admin/SignupStats.vue"
import SignupTable from "@/components/admin/SignupTable.vue"
import Link from "@/components/common/Link.vue"

const props = defineProps({
  signupData: { type: Object, required: true }
})
const emit = defineEmits(['refresh'])
</script>

<template>
  <p class="flex justify-center items-center font-semibold text-xl mb-6">
    Current Phase:
    <Badge class="text-md ml-2">Signup</Badge>
  </p>
  <div class="md:grid grid-cols-2 gap-4">
    <div class="text-center text-lg font-semibold underline">
      <Link size="20" :to="signupData.trail_alltrails_url" :text="signupData.trail_name" :new-tab="true"/>
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

  <SignupTable
    mode="signup"
    :users="signupData.users"
    :current-trail-id="signupData.trail_id"
    @switched="emit('refresh')"
    @cancelled="emit('refresh')"
  />
</template>
