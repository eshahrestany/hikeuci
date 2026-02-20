<template>
  <p class="flex justify-center items-center font-semibold text-xl mb-6">
    Current Phase:
    <Badge class="text-md ml-2">Waiver</Badge>
  </p>
  <div class="md:grid grid-cols-2 gap-4">
    <div class="text-center text-lg font-semibold underline">
      <Link size="20" :to="waiverData.trail_alltrails_url" :text="waiverData.trail_name" :new-tab="true"/>
      <img
          class="mt-2 w-auto object-cover rounded-md mb-2"
          :src="`/api/images/uploads/${waiverData.trail_id}`"
          :alt="`image of ${ waiverData.trail_name}`"
      />
      <Button variant="outline" size="sm" class="mt-1 no-underline" @click="showSwitchModal = true">
        <ArrowLeftRight class="h-4 w-4"/>
        Switch Trail
      </Button>
    </div>
    <SignupStats
        :users="waiverData.users"
        :passenger-capacity="waiverData.passenger_capacity"
        :over-capacity-passengers="waiverData.over_capacity_passengers"
    />
  </div>
  <Tabs default-value="selected">
    <TabsList class="grid w-fit grid-cols-2">
      <TabsTrigger value="selected">
        Selected Hikers
      </TabsTrigger>
      <TabsTrigger value="waitlisted">
        Waitlisted Hikers
      </TabsTrigger>
    </TabsList>
    <TabsContent value="selected">
      <SignupTable mode="waiver" :users="props.waiverData.users"/>
    </TabsContent>
    <TabsContent value="waitlisted">
      <WaitlistTable :waitlist-data="waitlist_data"/>
    </TabsContent>
  </Tabs>

  <SwitchTrailModal
    v-if="showSwitchModal"
    :current-trail-id="waiverData.trail_id"
    phase="waiver"
    @switched="emit('refresh')"
    @close="showSwitchModal = false"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowLeftRight } from 'lucide-vue-next'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import SignupStats from "@/components/admin/SignupStats.vue"
import SignupTable from "@/components/admin/SignupTable.vue"
import WaitlistTable from "@/components/admin/WaitlistTable.vue"
import SwitchTrailModal from "@/components/admin/SwitchTrailModal.vue"
import { useAuth } from "@/lib/auth.js"
import Link from "@/components/common/Link.vue"

const { fetchWithAuth } = useAuth()

const props = defineProps({waiverData: {type: Object, required: true}})
const emit = defineEmits(['refresh'])
const waitlist_data = ref([])
const showSwitchModal = ref(false)

async function loadWaitlist() {
  const res = await fetchWithAuth('/api/admin/waitlist')
  if (!res.ok) return
  const users = await res.json()
  waitlist_data.value = users.sort((a, b) => a.waitlist_pos - b.waitlist_pos)
}

onMounted(loadWaitlist)
</script>
