<script setup>
import SignupStats from "@/components/admin/SignupStats.vue"
import SignupTable from "@/components/admin/SignupTable.vue"
import Link from "@/components/common/Link.vue"

const props = defineProps({
  signupData: { type: Object, required: true }
})
const emit = defineEmits(['refresh'])
</script>

<template>
  <div class="space-y-6">
    <!-- Trail info + stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Trail card -->
      <div class="overflow-hidden rounded-xl border bg-card shadow-sm">
        <div class="relative h-40 overflow-hidden bg-muted">
          <img
            class="h-full w-full object-cover"
            :src="`/api/images/uploads/${signupData.trail_id}`"
            :alt="`${signupData.trail_name}`"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div class="absolute bottom-3 left-3 right-3">
            <Link
              size="16"
              class="text-white font-semibold text-base hover:underline"
              :to="signupData.trail_alltrails_url"
              :text="signupData.trail_name"
              :new-tab="true"
            />
          </div>
        </div>
      </div>

      <!-- Stats -->
      <SignupStats
        :users="signupData.users"
        :passenger-capacity="signupData.passenger_capacity"
        :hike-date="signupData.timeline?.hike_date"
      />
    </div>

    <!-- Hikers table -->
    <SignupTable
      mode="signup"
      :users="signupData.users"
      :current-trail-id="signupData.trail_id"
      @switched="emit('refresh')"
      @cancelled="emit('refresh')"
      @changed="emit('refresh')"
    />
  </div>
</template>
