<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { ArrowLeft, Download } from 'lucide-vue-next'
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  FlexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  useVueTable,
} from '@tanstack/vue-table'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-vue-next'
import { Input } from '@/components/ui/input'
import Link from '@/components/common/Link.vue'
import { useAuth } from '@/lib/auth.js'
import { h } from 'vue'

const route = useRoute()
const router = useRouter()
const { fetchWithAuth } = useAuth()

const loading = ref(true)
const hikeData = ref(null)
const nameFilter = ref('')
const transportFilter = ref('all')
const statusFilter = ref('all')
const checkedInFilter = ref('all')

async function loadHikeDetail() {
  loading.value = true
  try {
    const res = await fetchWithAuth(`/api/admin/history/hikes/${route.params.hikeId}`)
    if (!res.ok) throw Error(res.status)
    hikeData.value = await res.json()
  } catch (e) {
    console.error('Failed to load hike detail:', e)
    hikeData.value = null
  } finally {
    loading.value = false
  }
}

function formatDate(isoStr) {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })
}

const filteredSignups = computed(() => {
  if (!hikeData.value) return []
  let data = hikeData.value.signups

  if (nameFilter.value) {
    const q = nameFilter.value.toLowerCase()
    data = data.filter(s => s.name.toLowerCase().includes(q) || s.email.toLowerCase().includes(q))
  }
  if (transportFilter.value !== 'all') {
    data = data.filter(s => s.transport_type === transportFilter.value)
  }
  if (statusFilter.value !== 'all') {
    data = data.filter(s => s.signup_status === statusFilter.value)
  }
  if (checkedInFilter.value !== 'all') {
    const checked = checkedInFilter.value === 'yes'
    data = data.filter(s => s.is_checked_in === checked)
  }
  return data
})

const headerWithSortBtn = (label, ctx) => {
  const col = ctx.column
  const sorted = col.getIsSorted()
  const Icon = sorted === 'asc' ? ArrowUp : sorted === 'desc' ? ArrowDown : ArrowUpDown

  return h('div', { class: 'inline-flex items-center gap-x-1' }, [
    h('span', label),
    h(
      Button,
      {
        variant: 'ghost',
        size: 'icon',
        class: 'h-4 w-4 p-0',
        onClick: () => col.toggleSorting(sorted === 'asc'),
      },
      () => h(Icon, { class: 'h-4 w-4' })
    ),
  ])
}

const columns = [
  {
    id: 'name',
    header: (ctx) => headerWithSortBtn('Name', ctx),
    enableSorting: true,
    accessorFn: row => row.name,
    cell: info => info.getValue(),
  },
  {
    id: 'email',
    header: 'Email',
    accessorFn: row => row.email,
    cell: info => info.getValue(),
  },
  {
    id: 'phone',
    header: 'Phone',
    accessorFn: row => row.phone || '—',
    cell: info => info.getValue(),
  },
  {
    id: 'transport_type',
    header: (ctx) => headerWithSortBtn('Transport', ctx),
    enableSorting: true,
    accessorFn: row => row.transport_type,
    sortingFn: (a, b) => {
      const r = (t) => (t === 'driver' ? 0 : t === 'self' ? 1 : 2)
      return r(a.getValue('transport_type')) - r(b.getValue('transport_type'))
    },
    cell: ({ row }) => {
      const t = row.original.transport_type
      const label = t === 'driver' ? 'Driver' : t === 'self' ? 'Self' : 'Passenger'
      const cls = t === 'driver'
        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
        : t === 'self'
          ? 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
          : ''
      return h(Badge, { variant: 'outline', class: cls }, () => label)
    },
  },
  {
    id: 'signup_status',
    header: (ctx) => headerWithSortBtn('Status', ctx),
    enableSorting: true,
    accessorFn: row => row.signup_status,
    cell: ({ row }) => {
      const s = row.original.signup_status
      const label = s.charAt(0).toUpperCase() + s.slice(1)
      const cls = s === 'confirmed'
        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
        : s === 'waitlisted'
          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          : ''
      return h(Badge, { variant: 'outline', class: cls }, () => label)
    },
  },
  {
    id: 'is_checked_in',
    header: (ctx) => headerWithSortBtn('Checked In', ctx),
    enableSorting: true,
    accessorFn: row => row.is_checked_in,
    sortingFn: (a, b) => Number(a.original.is_checked_in) - Number(b.original.is_checked_in),
    cell: ({ row }) => {
      const checked = row.original.is_checked_in
      return h(Badge, {
        variant: 'outline',
        class: checked
          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      }, () => checked ? 'Yes' : 'No')
    },
  },
  {
    id: 'has_waiver',
    header: (ctx) => headerWithSortBtn('Waiver', ctx),
    enableSorting: true,
    accessorFn: row => row.has_waiver,
    sortingFn: (a, b) => Number(a.original.has_waiver) - Number(b.original.has_waiver),
    cell: ({ row }) => {
      const has = row.original.has_waiver
      return h(Badge, {
        variant: 'outline',
        class: has
          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      }, () => has ? 'Yes' : 'No')
    },
  },
]

const sorting = ref([])

const table = useVueTable({
  get data() { return filteredSignups.value },
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  state: {
    get sorting() { return sorting.value },
  },
  onSortingChange: (updater) => {
    sorting.value = typeof updater === 'function' ? updater(sorting.value) : updater
  },
  initialState: {
    pagination: { pageIndex: 0, pageSize: 50 },
  },
})

function exportCSV() {
  const rows = filteredSignups.value
  const headers = ['Name', 'Email', 'Phone', 'Transport', 'Status', 'Checked In', 'Waiver']
  const csvRows = [headers.join(',')]

  for (const s of rows) {
    csvRows.push([
      `"${(s.name || '').replace(/"/g, '""')}"`,
      `"${(s.email || '').replace(/"/g, '""')}"`,
      `"${(s.phone || '').replace(/"/g, '""')}"`,
      s.transport_type,
      s.signup_status,
      s.is_checked_in ? 'Yes' : 'No',
      s.has_waiver ? 'Yes' : 'No',
    ].join(','))
  }

  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const trailName = hikeData.value?.trail_name?.replace(/\s+/g, '_') || 'hike'
  const date = hikeData.value?.hike_date?.split('T')[0] || 'unknown'
  a.download = `${trailName}_${date}_signups.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(loadHikeDetail)
</script>

<template>
  <section class="p-6">
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <div class="flex flex-wrap items-center gap-4">
          <Button variant="outline" size="sm" @click="router.push({ name: 'Dashboard History' })">
            <ArrowLeft class="h-4 w-4 mr-1" /> Back
          </Button>
          <template v-if="!loading && hikeData">
            <CardTitle class="text-2xl">
              {{ hikeData.trail_name }}
            </CardTitle>
            <Badge v-if="hikeData.status === 'cancelled'" variant="outline" class="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
              Cancelled
            </Badge>
            <span class="text-sm text-muted-foreground">{{ formatDate(hikeData.hike_date) }}</span>
          </template>
          <Skeleton v-if="loading" class="h-8 w-48" />
        </div>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />

        <!-- Summary stats -->
        <div v-if="!loading && hikeData" class="flex flex-wrap gap-6 pt-2 text-sm">
          <div>
            <span class="text-muted-foreground">Total Signups</span>
            <p class="text-lg font-semibold">{{ hikeData.num_signups }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Confirmed</span>
            <p class="text-lg font-semibold">{{ hikeData.num_confirmed }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Waitlisted</span>
            <p class="text-lg font-semibold">{{ hikeData.num_waitlisted }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Checked In</span>
            <p class="text-lg font-semibold">{{ hikeData.num_checked_in }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Attendance Rate</span>
            <p class="text-lg font-semibold">{{ Math.round(hikeData.attendance_rate * 100) }}%</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Skeleton v-if="loading" class="h-64 w-full" />
        <template v-else-if="hikeData">
          <!-- Filters -->
          <div class="flex flex-wrap items-center gap-2 mb-4">
            <Input
              v-model="nameFilter"
              class="max-w-[250px]"
              placeholder="Search name or email..."
            />
            <Select v-model="transportFilter">
              <SelectTrigger class="w-[140px]">
                <SelectValue placeholder="Transport" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Transport</SelectItem>
                <SelectItem value="driver">Driver</SelectItem>
                <SelectItem value="passenger">Passenger</SelectItem>
                <SelectItem value="self">Self</SelectItem>
              </SelectContent>
            </Select>
            <Select v-model="statusFilter">
              <SelectTrigger class="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="confirmed">Confirmed</SelectItem>
                <SelectItem value="waitlisted">Waitlisted</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
            <Select v-model="checkedInFilter">
              <SelectTrigger class="w-[150px]">
                <SelectValue placeholder="Checked In" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Attendance</SelectItem>
                <SelectItem value="yes">Checked In</SelectItem>
                <SelectItem value="no">Not Checked In</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm" class="ml-auto" @click="exportCSV">
              <Download class="h-4 w-4 mr-1" /> Export CSV
            </Button>
          </div>

          <!-- Signups Table -->
          <div class="border rounded-sm">
            <Table>
              <TableHeader>
                <TableRow v-for="hg in table.getHeaderGroups()" :key="hg.id">
                  <TableHead v-for="header in hg.headers" :key="header.id">
                    <FlexRender
                      v-if="!header.isPlaceholder"
                      :render="header.column.columnDef.header"
                      :props="header.getContext()"
                    />
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <template v-if="table.getRowModel().rows.length">
                  <TableRow v-for="row in table.getRowModel().rows" :key="row.id">
                    <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                      <FlexRender
                        :render="cell.column.columnDef.cell"
                        :props="cell.getContext()"
                      />
                    </TableCell>
                  </TableRow>
                </template>
                <TableRow v-else>
                  <TableCell :colspan="columns.length" class="h-24 text-center">
                    No signups match the current filters.
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
            <div class="flex items-center py-1 mx-2 space-x-2">
              <Button
                variant="outline"
                size="sm"
                :disabled="!table.getCanPreviousPage()"
                @click="table.previousPage()"
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                :disabled="!table.getCanNextPage()"
                @click="table.nextPage()"
              >
                Next
              </Button>
              <span class="ml-auto text-sm text-muted-foreground">
                {{ filteredSignups.length }} signup{{ filteredSignups.length !== 1 ? 's' : '' }}
                <template v-if="table.getPageCount() > 1">
                  &middot; Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
                </template>
              </span>
            </div>
          </div>
        </template>
        <p v-else class="text-sm text-muted-foreground text-center py-8">
          Hike not found.
        </p>
      </CardContent>
    </Card>
  </section>
</template>
