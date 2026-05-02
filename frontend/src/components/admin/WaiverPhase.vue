<template>
  <div class="space-y-6">
    <!-- Trail info + stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Trail card -->
      <div class="overflow-hidden rounded-xl border bg-card shadow-sm">
        <div class="relative h-40 overflow-hidden bg-muted">
          <img
            class="h-full w-full object-cover"
            :src="`/api/images/uploads/${waiverData.trail_id}`"
            :alt="`${waiverData.trail_name}`"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div class="absolute bottom-3 left-3 right-3">
            <p class="text-white font-semibold text-base leading-tight">{{ waiverData.trail_name }}</p>
          </div>
        </div>
        <div class="px-3 py-2 border-t flex items-center gap-4">
          <Link v-if="waiverData.trail_alltrails_url" :to="waiverData.trail_alltrails_url" text="AllTrails" :new-tab="true" :size="12"/>
          <RouterLink :to="{ name: 'Trail Detail', params: { trailId: String(waiverData.trail_id) } }" class="text-xs text-blue-400 hover:underline">Trail info</RouterLink>
        </div>
      </div>

      <!-- Stats -->
      <SignupStats
        :users="waiverData.users"
        :passenger-capacity="waiverData.passenger_capacity"
        :over-capacity-passengers="waiverData.over_capacity_passengers"
        :hike-date="waiverData.timeline?.hike_date"
      />
    </div>

    <!-- Food interest -->
    <FoodInterestCard :users="waiverData.users" />

    <!-- Hikers tabs -->
    <Tabs default-value="selected">
      <TabsList class="h-9 rounded-lg bg-muted p-1 w-fit">
        <TabsTrigger value="selected" class="rounded-md px-4 text-sm">
          Selected Hikers
        </TabsTrigger>
        <TabsTrigger value="waitlisted" class="rounded-md px-4 text-sm">
          Waitlisted
        </TabsTrigger>
      </TabsList>

      <TabsContent value="selected" class="mt-4">
        <SignupTable
          mode="waiver"
          :users="waiverData.users"
          :current-trail-id="waiverData.trail_id"
          @switched="emit('refresh')"
          @cancelled="emit('refresh')"
          @changed="emit('refresh')"
        />
      </TabsContent>

      <TabsContent value="waitlisted" class="mt-4">
        <WaitlistTable :waitlist-data="waitlist_data"/>
      </TabsContent>
    </Tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import SignupStats from "@/components/admin/SignupStats.vue"
import SignupTable from "@/components/admin/SignupTable.vue"
import WaitlistTable from "@/components/admin/WaitlistTable.vue"
import FoodInterestCard from "@/components/admin/FoodInterestCard.vue"
import { useAuth } from "@/lib/auth.js"
import Link from "@/components/common/Link.vue"

const { fetchWithAuth } = useAuth()

const props = defineProps({ waiverData: { type: Object, required: true } })
const emit = defineEmits(['refresh'])
const waitlist_data = ref([])

async function loadWaitlist() {
  const res = await fetchWithAuth('/api/admin/waitlist')
  if (!res.ok) return
  const users = await res.json()
  waitlist_data.value = users.sort((a, b) => a.waitlist_pos - b.waitlist_pos)
}

onMounted(loadWaitlist)
watch(() => props.waiverData, loadWaitlist)
</script>
