<script setup>
import { ref } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowLeftRight } from 'lucide-vue-next'
import SignupStats from "@/components/admin/SignupStats.vue"
import SignupTable from "@/components/admin/SignupTable.vue"
import Link from "@/components/common/Link.vue"
import SwitchTrailModal from "@/components/admin/SwitchTrailModal.vue"

const props = defineProps({
  signupData: { type: Object, required: true }
})
const emit = defineEmits(['refresh'])

const showSwitchModal = ref(false)
</script>

<template>
  <div class="flex justify-between items-center mb-6">
    <p class="flex items-center font-semibold text-xl">
      Current Phase:
      <Badge class="text-md ml-2">Signup</Badge>
    </p>
    <Button variant="outline" size="sm" @click="showSwitchModal = true">
      <ArrowLeftRight class="h-4 w-4"/>
      Switch Trail
    </Button>
  </div>
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

  <SignupTable mode="signup" :users="signupData.users"/>

  <SwitchTrailModal
    v-if="showSwitchModal"
    :current-trail-id="signupData.trail_id"
    phase="signup"
    @switched="emit('refresh')"
    @close="showSwitchModal = false"
  />
</template>
