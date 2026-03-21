<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { CheckIcon, ChevronsUpDownIcon, Calculator, Download, Loader2 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import HikeHistoryCharts from '@/components/admin/HikeHistoryCharts.vue'
import HikeHistoryTable from '@/components/admin/HikeHistoryTable.vue'
import { toast } from 'vue-sonner'
import { useAuth } from '@/lib/auth.js'

const router = useRouter()
const { fetchWithAuth, postWithAuth } = useAuth()

const loading = ref(true)
const academicYears = ref([])
const selectedAY = ref('')
const open = ref(false)
const hikes = ref([])
const hikesLoading = ref(false)
const loadError = ref('')
const attendanceFrequency = ref(null)

// Reimbursement state
const selectedHikeIds = ref([])
const rateDialogOpen = ref(false)
const ratePerMile = ref('0.00')
const reimbursementLoading = ref(false)
const resultsDialogOpen = ref(false)
const reimbursementResults = ref(null)

// Frequency drill-down state
const frequencyDialogOpen = ref(false)
const frequencyDialogCount = ref(0)
const frequencyDialogMembers = ref([])
const frequencyDialogLoading = ref(false)

async function onSelectFrequency(count) {
  frequencyDialogCount.value = count
  frequencyDialogOpen.value = true
  frequencyDialogLoading.value = true
  frequencyDialogMembers.value = []
  try {
    const res = await fetchWithAuth(
      `/api/admin/history/attendance-frequency/members?ay=${encodeURIComponent(selectedAY.value)}&count=${count}`
    )
    if (!res.ok) throw Error(res.status)
    const data = await res.json()
    frequencyDialogMembers.value = data.members
  } catch {
    toast.error('Failed to load members')
    frequencyDialogOpen.value = false
  } finally {
    frequencyDialogLoading.value = false
  }
}

const selectedLabel = computed(() =>
  academicYears.value.find(ay => ay === selectedAY.value) || 'Select year...'
)

function selectAY(val) {
  selectedAY.value = val === selectedAY.value ? '' : val
  open.value = false
}

async function loadAcademicYears() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await fetchWithAuth('/api/admin/history/academic-years')
    if (!res.ok) throw Error(res.status)
    const data = await res.json()
    academicYears.value = data.academic_years
    selectedAY.value = data.current
  } catch (e) {
    console.error('Failed to load academic years:', e)
    academicYears.value = []
    loadError.value = 'Failed to load academic years.'
    toast.error('Failed to load academic years')
  } finally {
    loading.value = false
  }
}

async function loadHikes(ay) {
  if (!ay) return
  hikesLoading.value = true
  loadError.value = ''
  try {
    const [hikesRes, freqRes] = await Promise.all([
      fetchWithAuth(`/api/admin/history/hikes?ay=${encodeURIComponent(ay)}`),
      fetchWithAuth(`/api/admin/history/attendance-frequency?ay=${encodeURIComponent(ay)}`),
    ])
    if (!hikesRes.ok) throw Error(hikesRes.status)
    hikes.value = await hikesRes.json()
    attendanceFrequency.value = freqRes.ok ? await freqRes.json() : null
  } catch (e) {
    console.error('Failed to load hikes:', e)
    hikes.value = []
    attendanceFrequency.value = null
    loadError.value = 'Failed to load hike history.'
    toast.error('Failed to load hike history')
  } finally {
    hikesLoading.value = false
  }
}

async function calculateReimbursements() {
  const rate = parseFloat(ratePerMile.value)
  if (isNaN(rate) || rate <= 0) {
    toast.error('Please enter a valid rate per mile')
    return
  }

  reimbursementLoading.value = true
  try {
    const res = await postWithAuth('/api/admin/history/reimbursements', {
      hike_ids: selectedHikeIds.value,
      rate_per_mile: rate,
    })
    const data = await res.json()
    if (!res.ok) {
      toast.error(data.error || 'Failed to calculate reimbursements')
      return
    }
    reimbursementResults.value = data
    rateDialogOpen.value = false
    resultsDialogOpen.value = true
  } catch {
    toast.error('Failed to calculate reimbursements')
  } finally {
    reimbursementLoading.value = false
  }
}

function exportReimbursementsCSV() {
  if (!reimbursementResults.value) return
  const rows = reimbursementResults.value.reimbursements
  const headers = ['Name', 'Email', 'Phone', 'Hikes Driven', 'Total Miles', 'Reimbursement']
  const csvRows = [headers.join(',')]

  for (const r of rows) {
    csvRows.push([
      `"${(r.name || '').replace(/"/g, '""')}"`,
      `"${(r.email || '').replace(/"/g, '""')}"`,
      `"${(r.phone || '').replace(/"/g, '""')}"`,
      r.hikes_driven,
      r.total_miles,
      r.reimbursement.toFixed(2),
    ].join(','))
  }

  csvRows.push('')
  csvRows.push(`"Total",,,,${reimbursementResults.value.total_miles},${reimbursementResults.value.total_reimbursement.toFixed(2)}`)

  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `driver_reimbursements_${selectedAY.value}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

watch(selectedAY, (ay) => loadHikes(ay))

onMounted(loadAcademicYears)
</script>

<template>
  <section class="p-6">
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <div class="flex flex-wrap items-center justify-between gap-4">
          <CardTitle class="text-2xl">Hike History</CardTitle>
          <div v-if="!loading" class="flex items-center gap-2">
            <Label class="text-sm text-muted-foreground whitespace-nowrap">Academic Year</Label>
            <Popover v-model:open="open">
              <PopoverTrigger as-child>
                <Button
                  variant="outline"
                  role="combobox"
                  :aria-expanded="open"
                  class="w-[180px] justify-between"
                >
                  {{ selectedLabel }}
                  <ChevronsUpDownIcon class="opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent class="w-[180px] p-0">
                <Command>
                  <CommandInput class="h-9" placeholder="Search year..." />
                  <CommandList>
                    <CommandEmpty>No results found.</CommandEmpty>
                    <CommandGroup>
                      <CommandItem
                        v-for="ay in academicYears"
                        :key="ay"
                        :value="ay"
                        @select="(ev) => selectAY(ev.detail.value)"
                      >
                        {{ ay }}
                        <CheckIcon
                          :class="cn(
                            'ml-auto',
                            selectedAY === ay ? 'opacity-100' : 'opacity-0',
                          )"
                        />
                      </CommandItem>
                    </CommandGroup>
                  </CommandList>
                </Command>
              </PopoverContent>
            </Popover>
          </div>
          <Skeleton v-else class="h-9 w-[180px]" />
        </div>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>
      <CardContent>
        <Skeleton v-if="hikesLoading" class="h-64 w-full" />
        <template v-else-if="hikes.length">
          <HikeHistoryCharts :hikes="hikes" :attendance-frequency="attendanceFrequency" @select-frequency="onSelectFrequency" />
          <div class="flex items-center justify-end mb-3">
            <Button
              :disabled="selectedHikeIds.length === 0"
              @click="rateDialogOpen = true"
            >
              <Calculator class="h-4 w-4 mr-1" />
              Calculate Reimbursements
              <span v-if="selectedHikeIds.length" class="ml-1 text-xs">({{ selectedHikeIds.length }})</span>
            </Button>
          </div>
          <HikeHistoryTable :hikes="hikes" @update:selected-hike-ids="selectedHikeIds = $event" />
        </template>
        <p v-else-if="loadError" class="text-sm text-destructive text-center py-8">
          {{ loadError }}
        </p>
        <p v-else-if="selectedAY" class="text-sm text-muted-foreground text-center py-8">
          No past hikes found for {{ selectedAY }}.
        </p>
      </CardContent>
    </Card>

    <!-- Rate Input Dialog -->
    <Dialog v-model:open="rateDialogOpen">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Driver Reimbursement Rate</DialogTitle>
          <DialogDescription>
            Enter the reimbursement rate in dollars per mile. This will be applied to
            {{ selectedHikeIds.length }} selected hike{{ selectedHikeIds.length !== 1 ? 's' : '' }}.
            Mileage is calculated as round-trip (2x driving distance to trailhead).
          </DialogDescription>
        </DialogHeader>
        <div class="flex items-center gap-2 py-4">
          <Label for="rate" class="whitespace-nowrap">$ per mile</Label>
          <Input
            id="rate"
            v-model="ratePerMile"
            type="number"
            step="0.01"
            min="0.01"
            class="max-w-[120px]"
          />
        </div>
        <DialogFooter>
          <Button variant="outline" @click="rateDialogOpen = false">Cancel</Button>
          <Button :disabled="reimbursementLoading" @click="calculateReimbursements">
            {{ reimbursementLoading ? 'Calculating...' : 'Calculate' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Results Dialog -->
    <Dialog v-model:open="resultsDialogOpen">
      <DialogContent class="sm:max-w-3xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Driver Reimbursements</DialogTitle>
          <DialogDescription>
            Rate: ${{ parseFloat(ratePerMile).toFixed(2) }}/mile
          </DialogDescription>
        </DialogHeader>
        <template v-if="reimbursementResults">
          <div v-if="reimbursementResults.reimbursements.length" class="space-y-4">
            <div class="border rounded-sm">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Phone</TableHead>
                    <TableHead class="text-right">Hikes</TableHead>
                    <TableHead class="text-right">Miles</TableHead>
                    <TableHead class="text-right">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-for="r in reimbursementResults.reimbursements" :key="r.email">
                    <TableCell>{{ r.name }}</TableCell>
                    <TableCell>{{ r.email }}</TableCell>
                    <TableCell>{{ r.phone || '—' }}</TableCell>
                    <TableCell class="text-right">{{ r.hikes_driven }}</TableCell>
                    <TableCell class="text-right">{{ r.total_miles }}</TableCell>
                    <TableCell class="text-right font-medium">${{ r.reimbursement.toFixed(2) }}</TableCell>
                  </TableRow>
                  <TableRow class="font-bold">
                    <TableCell colspan="4">Total</TableCell>
                    <TableCell class="text-right">{{ reimbursementResults.total_miles }}</TableCell>
                    <TableCell class="text-right">${{ reimbursementResults.total_reimbursement.toFixed(2) }}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground text-center py-4">
            No checked-in drivers found for the selected hikes.
          </p>
        </template>
        <DialogFooter>
          <Button variant="outline" @click="resultsDialogOpen = false">Close</Button>
          <Button
            v-if="reimbursementResults?.reimbursements.length"
            @click="exportReimbursementsCSV"
          >
            <Download class="h-4 w-4 mr-1" /> Export CSV
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Frequency Drill-Down Dialog -->
    <Dialog v-model:open="frequencyDialogOpen">
      <DialogContent class="sm:max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            Members with {{ frequencyDialogCount }} hike{{ frequencyDialogCount !== 1 ? 's' : '' }} attended
          </DialogTitle>
          <DialogDescription>
            {{ frequencyDialogMembers.length }} member{{ frequencyDialogMembers.length !== 1 ? 's' : '' }}
            in {{ selectedAY }}
          </DialogDescription>
        </DialogHeader>
        <div v-if="frequencyDialogLoading" class="flex justify-center py-8">
          <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
        <div v-else-if="frequencyDialogMembers.length" class="border rounded-sm">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="m in frequencyDialogMembers"
                :key="m.id"
                class="cursor-pointer hover:bg-muted/50"
                @click="frequencyDialogOpen = false; router.push({ name: 'Member History', params: { memberId: m.id } })"
              >
                <TableCell>{{ m.name }}</TableCell>
                <TableCell>{{ m.email }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="frequencyDialogOpen = false">Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </section>
</template>
