<template>
  <div class="rounded-lg border overflow-hidden">
    <Table>
      <TableHeader class="bg-muted/50">
        <TableRow class="border-b">
          <TableHead v-for="h in table.getHeaderGroups().flatMap(hg => hg.headers)" :key="h.id" class="text-xs font-semibold px-3 py-2">
            <FlexRender v-if="!h.isPlaceholder" :render="h.column.columnDef.header" :props="h.getContext()" />
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <template v-if="data.length > 0">
          <TableRow
            v-for="row in table.getRowModel().rows"
            :key="row.id"
            class="odd:bg-muted/20 hover:bg-muted/40 transition-colors"
          >
            <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id" class="px-3 py-2 text-xs">
              <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
            </TableCell>
          </TableRow>
        </template>
        <TableRow v-else>
          <TableCell colspan="3" class="h-24 text-center text-sm text-muted-foreground">
            No waitlisted hikers.
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <ModifyUserModal
      v-if="editUser"
      mode="waitlist"
      :user="editUser"
      @close="editUser = null"
      @saved="onUserSaved"
    />
  </div>
</template>

<script setup>
import { h, shallowRef, ref } from 'vue'
import { useVueTable, getCoreRowModel, FlexRender } from '@tanstack/vue-table'
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Edit } from 'lucide-vue-next'
import ModifyUserModal from '@/components/admin/ModifyUserModal.vue'

const props = defineProps({ waitlistData: { type: Object, required: true } })
const data = shallowRef([...props.waitlistData])
const editUser = ref(null)

function modifyRow(user) {
  editUser.value = user
  editUser.value.transport_type = "passenger"
}

function onUserSaved(updatedUser) {
  data.value = data.value.filter(u => u.member_id !== updatedUser.member_id)
  editUser.value = null
}

const columns = [
  {
    id: 'pos',
    header: 'Position',
    accessorFn: row => row.waitlist_pos,
    cell: info => h(Badge, { variant: 'secondary', class: 'tabular-nums' }, () => `#${info.getValue()}`),
  },
  {
    id: 'name',
    header: 'Name',
    accessorFn: row => row.name,
    cell: info => h('span', { class: 'text-sm' }, info.getValue()),
  },
  {
    id: 'actions',
    header: 'Actions',
    cell: ({ row }) =>
      h(Button, {
        variant: 'outline', size: 'sm',
        onClick: () => modifyRow(row.original),
      }, () => [h(Edit, { class: 'h-3.5 w-3.5 mr-1' }), 'Move up']),
  },
]

const table = useVueTable({ data, columns, getCoreRowModel: getCoreRowModel() })
</script>
