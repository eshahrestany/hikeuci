<template>
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
        <template v-if="data.length > 0">
          <TableRow
            v-for="row in table.getRowModel().rows"
            :key="row.id"
          >
            <TableCell
              v-for="cell in row.getVisibleCells()"
              :key="cell.id"
            >
              <FlexRender
                :render="cell.column.columnDef.cell"
                :props="cell.getContext()"
              />
            </TableCell>
          </TableRow>
        </template>
        <TableRow v-else>
          <TableCell colspan="3" class="h-24 text-center">
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
import { h, shallowRef, ref, onMounted } from 'vue'
import { useAuth } from '@/lib/auth.js'
import {
  useVueTable,
  getCoreRowModel,
  FlexRender,
} from '@tanstack/vue-table'
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Edit } from 'lucide-vue-next'
import ModifyUserModal from '@/components/admin/ModifyUserModal.vue'

const { fetchWithAuth } = useAuth()
const data = shallowRef([])

async function loadWaitlist() {
  const res = await fetchWithAuth('/admin/waitlist')
  if (!res.ok) return
  const users = await res.json()
  data.value = users.sort((a, b) => a.waitlist_pos - b.waitlist_pos)
}

onMounted(loadWaitlist)

const editUser = ref(null)

function modifyRow(user) {
  editUser.value = user
  editUser.value.transport_type = "passenger"
}

function onUserSaved(updatedUser) {
  data.value = data.value.filter(
    (u) => u.member_id !== updatedUser.member_id
  )
  editUser.value = null
}

const columns = [
  {
    id: 'pos',
    header: 'Position',
    accessorFn: (row) => row.waitlist_pos,
    cell: (info) => h(
      'span',
      { class: 'text-center ml-2 text' },
      info.getValue()
    ),
  },
  {
    id: 'name',
    header: 'Name',
    accessorFn: (row) => row.name,
    cell: (info) => info.getValue(),
  },
  {
    id: 'actions',
    header: 'Actions',
    cell: ({ row }) =>
      h(
        Button,
        {
          variant: 'outline',
          size: 'icon',
          onClick: () => modifyRow(row.original),
        },
        () => h(Edit, { class: 'h-4 w-4' })
      ),
  },
]

const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
})
</script>