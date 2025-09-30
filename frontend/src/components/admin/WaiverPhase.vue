<template>
  <p class="flex justify-center items-center font-semibold text-xl mb-6">
    Current Phase:
    <Badge class="text-md ml-2">Waiver</Badge>
  </p>
  <div class="md:grid grid-cols-2 gap-4">
    <div class="text-center text-lg font-semibold underline">
      Trail: {{ waiverData.trail_name }}
      <img
          class="mt-2 w-auto object-cover rounded-md mb-2"
          :src="`/api/images/uploads/${waiverData.trail_id}`"
          :alt="`image of ${ waiverData.trail_name}`"
      />
    </div>
    <SignupStats
        :users="waiverData.users"
        :passenger-capacity="waiverData.passenger_capacity"
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
      <WaiverTable :waiver-data="props.waiverData"/>
    </TabsContent>
    <TabsContent value="waitlisted">
      <WaitlistTable :waitlist-data="waitlist_data"/>
    </TabsContent>
  </Tabs>
</template>

<script setup>
import { Badge } from '@/components/ui/badge'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import SignupStats from "@/components/admin/SignupStats.vue";
import WaiverTable from "@/components/admin/WaiverTable.vue";
import WaitlistTable from "@/components/admin/WaitlistTable.vue";
import {onMounted, ref} from "vue";
import {useAuth} from "@/lib/auth.js";

const { fetchWithAuth } = useAuth()

const props = defineProps({waiverData: {type: Object, required: true}})
const waitlist_data = ref([])

async function loadWaitlist() {
  const res = await fetchWithAuth('/api/admin/waitlist')
  if (!res.ok) return
  const users = await res.json()
  waitlist_data.value = users.sort((a, b) => a.waitlist_pos - b.waitlist_pos)
}

onMounted(loadWaitlist)

</script>
