<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <p class="font-semibold text-xl">
        Current Phase: <Badge class="text-md">Waiver</Badge>
      </p>
    </div>

    <CardHeader class="flex items-start">
      <div class="basis-1/2">
        <img
          class="w-1/2 object-cover rounded-md"
          :src="`/api/images/uploads/${waiverData.trail_id}.png`"
          :alt="waiverData.trail_name"
        />
      </div>
      <div class="flex-1">
        <CardTitle class="mb-4">{{ waiverData.trail_name }}</CardTitle>
        <SignupStats
          :users="waiverData.users"
          :passenger-capacity="waiverData.passenger_capacity"
        />
      </div>
    </CardHeader>

    <!-- Name Filter + Actions -->
    <div class="flex items-center justify-between py-2">
      <Input
        class="max-w-sm"
        placeholder="Filter names..."
        :model-value="table.getColumn('name')?.getFilterValue()"
        @update:model-value="(val) => table.getColumn('name')?.setFilterValue(val)"
      />
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
    </div>
  </div>

  <EditUserSignup
      v-if="editUser"
      :user="editUser"
      :hike-id="waiverData.hike_id"
      @close="editUser = null"
      @saved="() => editUser = null"
  />
</template>

<script setup>
import { ref, computed, h, onMounted } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table'
import { useVueTable, getCoreRowModel, getFilteredRowModel } from '@tanstack/vue-table'
import { FlexRender } from '@tanstack/vue-table'
import {Check, Edit, Trash} from "lucide-vue-next";
import { useAuth } from "@/lib/auth.js"
import { toast } from "vue-sonner";
import EditUserSignup from "@/components/admin/EditUserSignup.vue";
import SignupStats from "@/components/admin/SignupStats.vue";
import {CardHeader, CardTitle} from "@/components/ui/card/index.js";

const { postWithAuth } = useAuth()

const props = defineProps({
  waiverData: { type: Object, required: true }
})

const editUser = ref(null)

// Row-level actions
async function checkInRow(user) {
  try {
    const res = await postWithAuth('/active-hike/check-in', {
      user_id: user.member_id,
    })
    if (!res.ok) {
      // pull error message from body if available
      const errText = await res.text()
      throw new Error(errText || 'Unknown error')
    }
    // only update UI after success
    user.is_checked_in = true

    if (res.status === 200) toast.success(`${user.first_name} ${user.last_name} has been checked in.`)
    if (res.status === 208) toast.info(`${user.first_name} ${user.last_name} was already checked in.`)
  } catch (err) {
    toast.error("Check-in Failed")
  }
}

function modifyRow(user) {
  editUser.value = user
}

function removeRow(user) {
  // TODO: implement remove logic for `user`
}

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
    cell: ({ row }) => (row.original.transport_type === "passenger" ?
        'Passenger' : row.original.transport_type === "driver" ?
            'Driver' : 'Self-Transport'),
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
  },
  {
    id: 'actions',
    header: 'Actions',
    cell: ({ row }) =>
      h('div', { class: 'flex space-x-2' }, [
        h(
          Button,
          {
            size: 'icon',
            class: 'cursor-pointer',
            onClick: () => checkInRow(row.original),
            disabled: !row.original.has_waiver || row.original.is_checked_in
          },
          () => h(Check, { class: 'h-4 w-4' })
        ),
        h(
          Button,
          {
            variant: 'outline',
            size: 'icon',
            class: 'cursor-pointer',
            onClick: () => modifyRow(row.original)
          },
          () => h(Edit, { class: 'h-4 w-4' })
        ),
        h(
          Button,
          {
            variant: 'destructive',
            size: 'icon',
            class: 'cursor-pointer',
            onClick: () => removeRow(row.original)
          },
          () => h(Trash, { class: 'h-4 w-4' })
        )
      ])
  }
]
const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
</script>
