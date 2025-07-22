<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarTrigger />
    <SidebarInset>
      <section class="p-6">
        <h1 class="text-3xl text-white font-bold mb-3">HikeUCI Dashboard</h1>
        <hr class="h-px mb-8 bg-gray-200 border-0 dark:bg-gray-700" />
        <Card class="max-w-4xl mx-auto space-y-6">
          <CardHeader>
            <CardTitle class="text-2xl">Upcoming Hike</CardTitle>
            <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
          </CardHeader>
          <CardContent>
            <!-- Loading Skeleton -->
            <div v-if="loading">
              <Skeleton class="h-6 w-3/5 mb-4" />
              <Skeleton class="space-y-2">
                <Skeleton class="h-4 w-full" />
                <Skeleton class="h-4 w-4/5" />
                <Skeleton class="h-4 w-2/3" />
              </Skeleton>
            </div>

            <!-- No Upcoming Hike -->
            <div v-else-if="response.status === 'none'">
              <p class="text-center text-sm text-gray-500 mb-4"> No upcoming hikes found. </p>
              <Button variant="outline" class="block mx-auto"> Set Next Hike </Button>
            </div>

            <!-- Voting Phase -->
            <div v-else-if="response.status === 'voting'">
              <p class="font-semibold text-xl mb-2"> Current Phase: <Badge class="text-md">Voting</Badge></p>
              <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <Card v-for="candidate in response.candidates" :key="candidate.candidate_id">
                  <CardHeader>
                    <img class="h-24 w-full object-cover rounded-md mb-2" :src="`/api/images/uploads/${candidate.trail_id}.png`" :alt="candidate.trail_name"/>
                    <CardTitle>{{ candidate.trail_name }}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p class="text-sm mb-1">
                      Votes:
                      {{ candidate.candidate_num_votes }}
                      ({{ votePercentage(candidate) }}%)
                    </p>
                    <Progress :value="parseFloat(votePercentage(candidate))" class="mb-2"/>
                    <Button variant="outline" class="mb-2 p-0 " @click="showVoters[candidate.candidate_id] = !showVoters[candidate.candidate_id]">
                      <ChevronDown v-if="showVoters[candidate.candidate_id]"/>
                      <ChevronRight v-else/>
                      {{
                        showVoters[candidate.candidate_id]
                          ? 'Hide Votes'
                          : 'See Votes'
                      }}
                    </Button>
                    <ul
                      v-if="showVoters[candidate.candidate_id]"
                      class="list-disc list-inside text-sm space-y-1"
                    >
                      <li
                        v-for="(name, idx) in candidate.candidate_voters"
                        :key="idx"
                      >
                        {{ name }}
                      </li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </div>

            <!-- Signup Phase -->
            <div v-else-if="response.status === 'signup'">
              <p class="font-semibold text-xl mb-2">
                Current Phase:
                <Badge class="text-md">Signup</Badge>
              </p>
              <Card>
                <CardHeader>
                  <img
                    class="h-36 w-full object-cover rounded-md mb-2"
                    :src="`/api/images/uploads/${response.trail_id}.png`"
                    :alt="response.trail_name"
                  />
                  <CardTitle>{{ response.trail_name }}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div class="space-y-1 mb-4">
                    <p>Total Signups: {{ response.num_signups }}</p>
                    <p>Passengers: {{ response.num_passengers }}</p>
                    <p>Drivers: {{ response.num_drivers }}</p>
                    <p>Passenger Capacity: {{ response.passenger_capacity }}</p>
                  </div>
                  <div class="space-y-2">
                    <Button variant="link" @click="showSignup.passengers = !showSignup.passengers">
                      {{ showSignup.passengers ? 'Hide Passengers' : 'See Passengers' }}
                    </Button>
                    <ul v-if="showSignup.passengers" class="list-disc list-inside text-sm ml-4">
                      <li v-for="(name, idx) in response.passengers" :key="idx">{{ name }}</li>
                    </ul>
                    <Button variant="link" @click="showSignup.drivers = !showSignup.drivers">
                      {{ showSignup.drivers ? 'Hide Drivers' : 'See Drivers' }}
                    </Button>
                    <ul v-if="showSignup.drivers" class="list-disc list-inside text-sm ml-4">
                      <li v-for="(name, idx) in response.drivers" :key="idx">{{ name }}</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>

            <!-- Waiver Phase -->
            <div v-else-if="response.status === 'waiver'">
              <div class="flex items-center justify-between mb-4">
                <p class="font-semibold text-xl">Current Phase: <Badge class="text-md">Waiver</Badge></p>
              </div>

              <CardHeader>
                  <img
                    class="h-36 w-full object-cover rounded-md mb-2"
                    :src="`/api/images/uploads/${response.trail_id}.png`"
                    :alt="response.trail_name"
                  />
                  <CardTitle>{{ response.trail_name }}</CardTitle>
                </CardHeader>

              <!-- Name Filter -->
              <div class="flex items-center justify-between py-2">
                <Input
                  class="max-w-sm"
                  placeholder="Filter names..."
                  :model-value="table.getColumn('name')?.getFilterValue()"
                  @update:model-value="(value) => table.getColumn('name')?.setFilterValue(value)"
                />

                <div class="space-x-2">
                  <Button :disabled="!hasSelection" @click="checkInSelected">Check In</Button>
                  <Button :disabled="!hasSelection" @click="modifySelected">Modify</Button>
                  <Button variant="destructive" :disabled="!hasSelection" @click="removeSelected">Remove</Button>
                </div>
              </div>
              <div class="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow v-for="hg in table.getHeaderGroups()" :key="hg.id">
                      <TableHead v-for="h in hg.headers" :key="h.id">
                        <FlexRender v-if="!h.isPlaceholder" :render="h.column.columnDef.header" :props="h.getContext()" />
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <template v-if="table.getRowModel().rows.length">
                      <template v-for="row in table.getRowModel().rows" :key="row.id">
                        <TableRow :data-state="row.getIsSelected() && 'selected'">
                          <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                            <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
                          </TableCell>
                        </TableRow>
                      </template>
                    </template>
                    <TableRow v-else>
                      <TableCell colspan="5" class="h-24 text-center">No results.</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>

            <!-- Other Phases -->
            <div v-else>
              <p class="font-semibold text-lg">{{ capitalize(response.status) }} Phase</p>
              <p class="text-xs text-gray-500">(UI for '{{ response.status }}' phase goes here)</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </SidebarInset>
  </SidebarProvider>
</template>

<script setup>
import { ref, onMounted, computed, reactive, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../lib/auth.js'

import AppSidebar from '@/components/AppSidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table'
import { useVueTable, getCoreRowModel, getFilteredRowModel } from '@tanstack/vue-table'
import { FlexRender } from '@tanstack/vue-table'
import { ChevronDown, ChevronRight } from "lucide-vue-next"


const { state: signOut, fetchWithAuth } = useAuth()
const router = useRouter()

const loading = ref(true)
const response = ref({ status: 'none', candidates: [], users: [], trail_id: null, trail_name: '' })
const showVoters = reactive({})
const showSignup = reactive({ passengers: false, drivers: false })

// Selection
const rowSelection = ref({})
const hasSelection = computed(() => Object.values(rowSelection.value).some(v => v))
function checkInSelected() { /* TODO */ }
function modifySelected() { /* TODO */ }
function removeSelected() { /* TODO */ }

// Table
const data = computed(() => response.value.users)
const columns = [
  { id: 'name', header: 'Name', accessorFn: row => `${row.first_name} ${row.last_name}`, cell: info => info.getValue(), filterFn: (row, colId, filter) => String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase()) },
  { id: 'type', header: 'Type', cell: ({ row }) => row.original.is_driver ? 'Driver' : 'Passenger' },
  { id: 'waiver', header: 'Waiver?', cell: ({ row }) => h(Badge, { variant: 'outline', class: row.original.has_waiver ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800' }, () => row.original.has_waiver ? 'Yes' : 'No') },
  { id: 'checked_in', header: 'Checked In?', cell: ({ row }) => h(Badge, { variant: 'outline', class: row.original.is_checked_in ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800' }, () => row.original.is_checked_in ? 'Yes' : 'No'), enableSorting: false },
]
const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel()
})

const totalVotes = computed(
  () =>
    response.value.candidates.reduce(
      (sum, c) => sum + c.candidate_num_votes,
      0
    )
)

function votePercentage(candidate) {
  if (totalVotes.value === 0) return 0
  return ((candidate.candidate_num_votes / totalVotes.value) * 100).toFixed(
    1
  )
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

async function loadUpcoming() {
  loading.value = true
  try {
    const res = await fetchWithAuth('/api/dashboard/upcoming')
    response.value = await res.json()
  } catch {
    response.value = { status: 'none', candidates: [], users: [], trail_id: null, trail_name: '' }
  } finally {
    loading.value = false
  }
}

onMounted(loadUpcoming)

function signOutAndReturn() { signOut(); router.replace('/login') }
</script>

<style scoped>
</style>
