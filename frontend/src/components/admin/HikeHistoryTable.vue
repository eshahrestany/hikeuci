<script setup>
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  FlexRender,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  useVueTable,
} from "@tanstack/vue-table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import Link from "@/components/common/Link.vue"
import { ArrowUpDown, ArrowUp, ArrowDown, ExternalLink } from "lucide-vue-next"
import { ref, h, computed, watch } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const props = defineProps({
  hikes: { type: Array, required: true },
})

const emit = defineEmits(['update:selectedHikeIds'])

const rowSelection = ref({})

watch(() => props.hikes, () => {
  rowSelection.value = {}
  emit('update:selectedHikeIds', [])
})

watch(rowSelection, (sel) => {
  const ids = Object.keys(sel).filter(k => sel[k]).map(k => {
    const idx = parseInt(k)
    return props.hikes[idx]?.hike_id
  }).filter(Boolean)
  emit('update:selectedHikeIds', ids)
}, { deep: true })

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

function formatDate(isoStr) {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })
}

function attendanceBadge(rate) {
  const pct = Math.round(rate * 100)
  const colorClass = pct >= 80
    ? 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/30'
    : pct >= 50
      ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30'
      : 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/30'

  return h(Badge, { variant: 'outline', class: colorClass }, () => `${pct}%`)
}

const data = computed(() => props.hikes)

const columns = [
  {
    id: 'select',
    header: ({ table }) => h(Checkbox, {
      modelValue: table.getIsAllPageRowsSelected(),
      'onUpdate:modelValue': (value) => table.toggleAllPageRowsSelected(!!value),
    }),
    cell: ({ row }) => h(Checkbox, {
      modelValue: row.getIsSelected(),
      'onUpdate:modelValue': (value) => row.toggleSelected(!!value),
    }),
  },
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
      if (row.original.status === 'cancelled') {
        parts.push(h(Badge, {
          variant: 'outline',
          class: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/30 ml-2 text-xs',
        }, () => 'Cancelled'))
      }
      return h('span', { class: 'inline-flex items-center' }, parts)
    },
  },
  {
    id: 'num_confirmed',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Confirmed', ctx),
    accessorFn: row => row.num_confirmed,
    cell: info => info.getValue(),
  },
  {
    id: 'num_waitlisted',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Waitlisted', ctx),
    accessorFn: row => row.num_waitlisted,
    cell: info => info.getValue(),
  },
  {
    id: 'num_checked_in',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Checked In', ctx),
    accessorFn: row => row.num_checked_in,
    cell: info => info.getValue(),
  },
  {
    id: 'attendance_rate',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Attendance', ctx),
    accessorFn: row => row.attendance_rate,
    cell: ({ row }) => attendanceBadge(row.original.attendance_rate),
  },
  {
    id: 'num_drivers',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Drivers', ctx),
    accessorFn: row => row.num_drivers,
    cell: info => info.getValue(),
  },
  {
    id: 'num_passengers',
    enableSorting: true,
    header: (ctx) => headerWithSortBtn('Passengers', ctx),
    accessorFn: row => row.num_passengers,
    cell: info => info.getValue(),
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
  get data() { return data.value },
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  state: {
    get sorting() { return sorting.value },
    get rowSelection() { return rowSelection.value },
  },
  onSortingChange: (updater) => {
    sorting.value = typeof updater === 'function' ? updater(sorting.value) : updater
  },
  onRowSelectionChange: (updater) => {
    rowSelection.value = typeof updater === 'function' ? updater(rowSelection.value) : updater
  },
  initialState: {
    pagination: { pageIndex: 0, pageSize: 50 },
  },
})
</script>

<template>
  <div class="rounded-lg border overflow-x-auto">
    <Table>
      <TableHeader class="bg-muted/50">
        <TableRow v-for="hg in table.getHeaderGroups()" :key="hg.id" class="border-b">
          <TableHead v-for="h in hg.headers" :key="h.id" class="px-3 py-2 text-xs font-semibold">
            <FlexRender v-if="!h.isPlaceholder" :render="h.column.columnDef.header" :props="h.getContext()" />
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <template v-if="table.getRowModel().rows.length">
          <TableRow
            v-for="row in table.getRowModel().rows"
            :key="row.id"
            class="odd:bg-muted/20 hover:bg-muted/40 transition-colors"
          >
            <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id" class="px-3 py-2.5 text-sm">
              <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
            </TableCell>
          </TableRow>
        </template>
        <TableRow v-else>
          <TableCell :colspan="columns.length" class="h-24 text-center text-sm text-muted-foreground">
            No past hikes found for this academic year.
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
    <div class="flex items-center gap-2 px-3 py-2 border-t bg-muted/20">
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
      <span class="ml-auto text-xs text-muted-foreground">
        Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
      </span>
    </div>
  </div>
</template>
