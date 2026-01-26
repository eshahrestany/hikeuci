<script setup>
import { computed, onMounted, ref } from 'vue'
import VChart from 'vue-echarts'
import '@/lib/echarts'

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Separator } from '@/components/ui/separator'

import AttendanceTable from '@/components/admin/AttendanceTable.vue'
import {useAuth} from "@/lib/auth.js";

const { fetchWithAuth } = useAuth()

async function apiGet(path) {
  const res = await fetchWithAuth(path, { credentials: 'include' })
  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

const hikes = ref([])
const selectedHikeId = ref(null)

onMounted(async () => {
  const data = await apiGet('/api/admin/history/hikes')
  console.info(data)
  hikes.value = data.hikes || []
  if (hikes.value.length) selectedHikeId.value = hikes.value[0].id
})

const last5 = computed(() => hikes.value.slice(0, 5))
const older = computed(() => hikes.value.slice(5))

const selectedHike = computed(() => hikes.value.find(h => h.id === selectedHikeId.value) || null)

const trendOption = computed(() => {
  const xs = [...hikes.value].slice().reverse().map(h => new Date(h.hike_date).toLocaleDateString())
  const ys = [...hikes.value].slice().reverse().map(h => h.stats?.checked_in_total ?? 0)

  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xs },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: ys, smooth: true }],
    grid: { left: 40, right: 20, top: 30, bottom: 40 }
  }
})
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6 p-6">
    <Card class="h-fit">
      <CardHeader>
        <CardTitle>Past hikes</CardTitle>
      </CardHeader>
      <CardContent class="space-y-3">
        <div class="space-y-2">
          <Button
              v-for="h in last5"
              :key="h.id"
              variant="ghost"
              class="w-full justify-start"
              :class="selectedHikeId === h.id ? 'bg-muted' : ''"
              @click="selectedHikeId = h.id"
          >
            <div class="flex flex-col items-start">
              <span class="font-medium">{{ new Date(h.hike_date).toLocaleString() }}</span>
              <span class="text-xs text-muted-foreground">
                {{ h.trail?.name || 'No trail' }} — {{ h.stats?.checked_in_total ?? 0 }} checked in
              </span>
            </div>
          </Button>
        </div>

        <Separator v-if="older.length" />

        <Collapsible v-if="older.length">
          <CollapsibleTrigger as-child>
            <Button variant="outline" class="w-full">Older hikes ({{ older.length }})</Button>
          </CollapsibleTrigger>
          <CollapsibleContent class="mt-2 space-y-2">
            <Button
                v-for="h in older"
                :key="h.id"
                variant="ghost"
                class="w-full justify-start"
                :class="selectedHikeId === h.id ? 'bg-muted' : ''"
                @click="selectedHikeId = h.id"
            >
              <div class="flex flex-col items-start">
                <span class="font-medium">{{ new Date(h.hike_date).toLocaleString() }}</span>
                <span class="text-xs text-muted-foreground">
                  {{ h.trail?.name || 'No trail' }} — {{ h.stats?.checked_in_total ?? 0 }} checked in
                </span>
              </div>
            </Button>
          </CollapsibleContent>
        </Collapsible>
      </CardContent>
    </Card>

    <!-- Right: dashboard + selected hike -->
    <div class="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Attendance trend</CardTitle>
        </CardHeader>
        <CardContent>
          <VChart class="h-[280px] w-full" :option="trendOption" autoresize />
        </CardContent>
      </Card>

      <Card v-if="selectedHike">
        <CardHeader>
          <CardTitle>
            {{ new Date(selectedHike.hike_date).toLocaleString() }} — {{ selectedHike.trail?.name || 'No trail' }}
          </CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="rounded-md border p-3">
              <div class="text-xs text-muted-foreground">Checked in</div>
              <div class="text-2xl font-semibold">{{ selectedHike.stats.checked_in_total }}</div>
            </div>
            <div class="rounded-md border p-3">
              <div class="text-xs text-muted-foreground">No-shows</div>
              <div class="text-2xl font-semibold">{{ selectedHike.stats.noshow_total }}</div>
            </div>
            <div class="rounded-md border p-3">
              <div class="text-xs text-muted-foreground">Passenger capacity</div>
              <div class="text-2xl font-semibold">{{ selectedHike.stats.passenger_capacity }}</div>
            </div>
            <div class="rounded-md border p-3">
              <div class="text-xs text-muted-foreground">Passenger utilization</div>
              <div class="text-2xl font-semibold">
                <span v-if="selectedHike.stats.passenger_utilization != null">
                  {{ Math.round(selectedHike.stats.passenger_utilization * 100) }}%
                </span>
                <span v-else>—</span>
              </div>
            </div>
          </div>

          <AttendanceTable :hike-id="selectedHike.id" />
        </CardContent>
      </Card>
    </div>
  </div>
</template>
