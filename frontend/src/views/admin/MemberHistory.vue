<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  FlexRender,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  useVueTable,
} from '@tanstack/vue-table'
import { ArrowLeft, ArrowUpDown, ArrowUp, ArrowDown, ExternalLink } from 'lucide-vue-next'
import Link from '@/components/common/Link.vue'
import { useAuth } from '@/lib/auth.js'
import { h } from 'vue'

const route = useRoute()
const router = useRouter()
const { fetchWithAuth } = useAuth()

const loading = ref(true)
const data = ref(null)

async function loadMemberHistory() {
  loading.value = true
  try {
    const res = await fetchWithAuth(`/api/admin/history/members/${route.params.memberId}`)
    if (!res.ok) throw Error(res.status)
    data.value = await res.json()
  } catch (e) {
    console.error('Failed to load member history:', e)
    data.value = null
  } finally {
    loading.value = false
  }
}

function formatDate(isoStr) {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })
}

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

const hikesData = computed(() => data.value?.hikes || [])

const columns = [
  {
    id: 'hike_date',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Date', ctx),
    accessorFn: row => row.hike_date,
    cell: ({ row }) => formatDate(row.original.hike_date),
  },
  {
    id: 'trail_name',
    header: 'Trail',
    accessorFn: row => row.trail_name,
    cell: ({ row }) => {
      const parts = []
      if (row.original.trail_alltrails_url) {
        parts.push(h(Link, {
          to: row.original.trail_alltrails_url,
          text: row.original.trail_name,
          newTab: true,
          size: 14,
        }))
      } else {
        parts.push(row.original.trail_name)
      }
      if (row.original.hike_status === 'cancelled') {
        parts.push(h(Badge, {
          variant: 'outline',
          class: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 ml-2',
        }, () => 'Cancelled'))
      }
      return h('span', { class: 'inline-flex items-center' }, parts)
    },
  },
  {
    id: 'signup_status',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Status', ctx),
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
    id: 'transport_type',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Transport', ctx),
    accessorFn: row => row.transport_type,
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
    id: 'is_checked_in',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Checked In', ctx),
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
    id: 'details',
    header: '',
    cell: ({ row }) =>
      h(Button, {
        variant: 'outline',
        size: 'sm',
        onClick: () => router.push({ name: 'Hike Detail', params: { hikeId: row.original.hike_id } }),
      }, () => [h('span', 'Details'), h(ExternalLink, { class: 'h-3 w-3 ml-1' })]),
  },
]

const sorting = ref([])

const table = useVueTable({
  get data() { return hikesData.value },
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

onMounted(loadMemberHistory)
</script>

<template>
  <section class="p-6">
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <div class="flex flex-wrap items-center gap-4">
          <Button variant="outline" size="sm" @click="router.push({ name: 'Dashboard Members' })">
            <ArrowLeft class="h-4 w-4 mr-1" /> Back
          </Button>
          <template v-if="!loading && data">
            <CardTitle class="text-2xl">{{ data.member.name }}</CardTitle>
            <span class="text-sm text-muted-foreground">{{ data.member.email }}</span>
          </template>
          <Skeleton v-if="loading" class="h-8 w-48" />
        </div>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />

        <!-- Summary stats -->
        <div v-if="!loading && data" class="flex flex-wrap gap-6 pt-2 text-sm">
          <div>
            <span class="text-muted-foreground">Total Signups</span>
            <p class="text-lg font-semibold">{{ data.summary.total_signups }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Confirmed</span>
            <p class="text-lg font-semibold">{{ data.summary.total_confirmed }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Checked In</span>
            <p class="text-lg font-semibold">{{ data.summary.total_checked_in }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Attendance Rate</span>
            <p class="text-lg font-semibold">{{ Math.round(data.summary.attendance_rate * 100) }}%</p>
          </div>
          <div>
            <span class="text-muted-foreground">Times Driver</span>
            <p class="text-lg font-semibold">{{ data.summary.times_driver }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Times Passenger</span>
            <p class="text-lg font-semibold">{{ data.summary.times_passenger }}</p>
          </div>
          <div>
            <span class="text-muted-foreground">Times Self</span>
            <p class="text-lg font-semibold">{{ data.summary.times_self }}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Skeleton v-if="loading" class="h-64 w-full" />
        <template v-else-if="data && data.hikes.length">
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
                    No hike history found.
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
                {{ hikesData.length }} hike{{ hikesData.length !== 1 ? 's' : '' }}
                <template v-if="table.getPageCount() > 1">
                  &middot; Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
                </template>
              </span>
            </div>
          </div>
        </template>
        <p v-else-if="data" class="text-sm text-muted-foreground text-center py-8">
          No hike history found for this member.
        </p>
        <p v-else class="text-sm text-muted-foreground text-center py-8">
          Member not found.
        </p>
      </CardContent>
    </Card>
  </section>
</template>
