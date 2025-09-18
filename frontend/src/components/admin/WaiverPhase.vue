<template>
  <div>
    <p class="flex justify-center items-center font-semibold text-xl mb-6">
      Current Phase:
      <Badge class="text-md ml-2">Waiver</Badge>
    </p>

    <CardHeader class="flex items-start">
      <div class="basis-1/2">
        <img
          class="w-1/2 object-cover rounded-md"
          :src="`/api/images/uploads/${waiverData.trail_id}`"
          :alt="waiverData.trail_name"
        />
      </div>
      <div class="flex-1">
        <CardTitle>{{ waiverData.trail_name }}</CardTitle>
        <SignupStats
          :users="waiverData.users"
          :passenger-capacity="waiverData.passenger_capacity"
        />
      </div>
    </CardHeader>
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
  </div>
</template>

<script setup>
import { Badge } from '@/components/ui/badge'
import {CardHeader, CardTitle} from "@/components/ui/card/index.js";
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
