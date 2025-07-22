<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <p class="font-semibold text-xl">
        Current Phase: <Badge class="text-md">Waiver</Badge>
      </p>
    </div>

    <CardHeader>
      <img
        class="h-36 w-full object-cover rounded-md mb-2"
        :src="`/api/images/uploads/${waiverData.trail_id}.png`"
        :alt="waiverData.trail_name"
      />
      <CardTitle>{{ waiverData.trail_name }}</CardTitle>
    </CardHeader>

    <!-- Name Filter + Actions -->
    <div class="flex items-center justify-between py-2">
      <Input
        class="max-w-sm"
        placeholder="Filter names..."
        :model-value="table.getColumn('name')?.getFilterValue()"
        @update:model-value="(val) => table.getColumn('name')?.setFilterValue(val)"
      />
      <div class="space-x-2">
        <Button :disabled="!hasSelection" @click="checkInSelected">Check In</Button>
        <Button :disabled="!hasSelection" @click="modifySelected">Modify</Button>
        <Button variant="destructive" :disabled="!hasSelection" @click="removeSelected">
          Remove
        </Button>
      </div>
    </div>

    <!-- Table of Users -->
    <div class="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow v-for="hg in table.getHeaderGroups()" :key="hg.id">
            <TableHead v-for="h in hg.headers" :key="h.id">
              <FlexRender
                v-if="!h.isPlaceholder"
                :render="h.column.columnDef.header"
                :props="h.getContext()"
              />
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
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table'
import { useVueTable, getCoreRowModel, getFilteredRowModel } from '@tanstack/vue-table'
import { FlexRender } from '@tanstack/vue-table'

const props = defineProps({
  waiverData: { type: Object, required: true }
})

// selection
const rowSelection = ref({})
const hasSelection = computed(() =>
  Object.values(rowSelection.value).some(v => v)
)
function checkInSelected() { /* TODO */ }
function modifySelected()    { /* TODO */ }
function removeSelected()    { /* TODO */ }

// table setup
const data = computed(() => props.waiverData.users)
const columns = [
  {
    id: 'name',
    header: 'Name',
    accessorFn: row => `${row.first_name} ${row.last_name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
      String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'type',
    header: 'Type',
    cell: ({ row }) => (row.original.is_driver ? 'Driver' : 'Passenger')
  },
  {
    id: 'waiver',
    header: 'Waiver?',
    cell: ({ row }) =>
      h(
        Badge,
        {
          variant: 'outline',
          class: row.original.has_waiver
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        },
        () => (row.original.has_waiver ? 'Yes' : 'No')
      )
  },
  {
    id: 'checked_in',
    header: 'Checked In?',
    cell: ({ row }) =>
      h(
        Badge,
        {
          variant: 'outline',
          class: row.original.is_checked_in
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        },
        () => (row.original.is_checked_in ? 'Yes' : 'No')
      ),
    enableSorting: false
  }
]
const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  state: { rowSelection: rowSelection.value },
  onRowSelectionChange: v => (rowSelection.value = v)
})
</script>
