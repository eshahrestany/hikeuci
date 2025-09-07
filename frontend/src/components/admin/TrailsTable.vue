<script setup>
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table/index.js";
import {FlexRender, getCoreRowModel, getFilteredRowModel, useVueTable} from "@tanstack/vue-table";
import {Check, Edit, MailPlus, PlusCircle, Trash} from "lucide-vue-next";
import {Input} from "@/components/ui/input/index.js";
import {Button} from "@/components/ui/button/index.js";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog/index.js";
import ModifyUserModal from "@/components/admin/ModifyUserModal.vue";
import {ref, shallowRef, h} from "vue";
import {toast} from "vue-sonner";
import {Badge} from "@/components/ui/badge/index.js";
import {Tooltip, TooltipContent, TooltipTrigger} from "@/components/ui/tooltip/index.js";
import {useAuth} from "@/lib/auth.js";

const props = defineProps({trailsData: { type: Object, required: true }})
const { postWithAuth } = useAuth()

const data = shallowRef([...props.trailsData])

const columns = [
  {
    id: 'name',
    header: 'Name',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'location',
    header: 'location',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'length_mi',
    header: 'length_mi',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'estimated_time_hr',
    header: 'estimated_time_hr',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'required_water_liters',
    header: 'required_water_liters',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'difficulty',
    header: 'difficulty',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'alltrails_endpoint',
    header: 'alltrails_endpoint',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'trailhead_gmaps_endpoint',
    header: 'trailhead_gmaps_endpoint',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'trailhead_amaps_endpoint',
    header: 'trailhead_amaps_endpoint',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'description',
    header: 'description',
    accessorFn: row => `${row.name}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
];

const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
</script>

<template>
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
        <TableRow>
          <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
            <FlexRender
              :render="cell.column.columnDef.cell"
              :props="cell.getContext()"
            />
          </TableCell>
        </TableRow>
      </template>
    </template>
    <TableRow v-else>
      <TableCell colspan="5" class="h-24 text-center">
        No results.
      </TableCell>
    </TableRow>
  </TableBody>
</Table>
</template>

<style scoped>

</style>