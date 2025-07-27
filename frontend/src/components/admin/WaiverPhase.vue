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
      <Button class="ml-auto" @click="showAddSignup = true">
        <PlusCircle class="h-4 w-4" />Add Late Signup
      </Button>
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

  <AddLateSignup
    v-if="showAddSignup"
    :hike-id="waiverData.hike_id"
    @close="showAddSignup = false"
    @added="handleAdded"
  />

  <Dialog v-model:open="confirmOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Remove Hiker?</DialogTitle>
        <DialogDescription>
          Are you sure you want to remove
          {{ confirmUser?.first_name }} {{ confirmUser?.last_name }}
          from this hike?
        </DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="outline" @click="confirmOpen = false">
          Cancel
        </Button>
        <Button variant="destructive" @click="confirmedRemove">
          Remove
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup>
import {ref, computed, h, onMounted, watch, shallowRef} from 'vue'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table'
import { useVueTable, getCoreRowModel, getFilteredRowModel } from '@tanstack/vue-table'
import { FlexRender } from '@tanstack/vue-table'
import {Check, ChevronsUpDown, Edit, MailPlus, Search, Trash} from "lucide-vue-next";
import { useAuth } from "@/lib/auth.js"
import { toast } from "vue-sonner";
import EditUserSignup from "@/components/admin/EditUserSignup.vue";
import SignupStats from "@/components/admin/SignupStats.vue";
import {CardHeader, CardTitle} from "@/components/ui/card/index.js";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter
} from '@/components/ui/dialog'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { PlusCircle } from 'lucide-vue-next'
import AddLateSignup from '@/components/admin/AddLateSignup.vue'

const { postWithAuth } = useAuth()

const props = defineProps({waiverData: { type: Object, required: true }})
const editUser = ref(null)
const confirmOpen = ref(false)
const confirmUser = ref(null)
const showAddSignup = ref(false)
function handleAdded(newUser) {
  data.value.push(newUser)        // refresh table
  data.value = [...data.value]
  showAddSignup.value = false
}

// Row-level actions
async function checkInRow(user) {
  try {
    const res = await postWithAuth('/active-hike/check-in', {
      user_id: user.member_id,
    })
    if (!res.ok) {
      const errText = await res.text()
      throw new Error(errText || 'Unknown error')
    }
    user.is_checked_in = true
    if (res.status === 200) toast.success(`${user.first_name} ${user.last_name} has been checked in.`)
    if (res.status === 208) toast.info(`${user.first_name} ${user.last_name} was already checked in.`)
  } catch {
    toast.error("Check-in Failed")
  }
}

function modifyRow(user) {
  editUser.value = user
}

function resendEmail(user) {
  postWithAuth('/mail/resend-waiver', {
    hike_id: props.waiverData.hike_id,
    user_id: user.member_id
  })
    .then(res => {
      if (!res.ok) throw new Error('Failed to resend email')
      toast.success(`Email sent to ${user.first_name} ${user.last_name}`)
    })
    .catch(() => {
      toast.error('Failed to resend email')
    })
}

function removeRow(user) {
  confirmUser.value = user
  confirmOpen.value = true
}

async function confirmedRemove() {
  const user = confirmUser.value
  try {
    const res = await postWithAuth('/active-hike/remove-user', {
      hike_id: props.waiverData.hike_id,
      user_id: user.member_id
    })

    if (!res.ok) throw new Error(await res.text() || 'Error')
    const idx = data.value.findIndex(u => u.member_id === user.member_id)
    if (idx !== -1) {
      data.value.splice(idx, 1)
      data.value = [...data.value]
    }

    toast.success(`${user.first_name} ${user.last_name} removed`)
    removeRow(user)
  } catch {
    toast.error('Remove failed')
  } finally {
    confirmOpen.value = false
    confirmUser.value = null
  }
}


// table setup
const data = shallowRef([...props.waiverData.users])

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
    cell: ({ row }) =>
      row.original.transport_type === "passenger"
        ? 'Passenger'
        : row.original.transport_type === "driver"
          ? 'Driver'
          : 'Self-Transport',
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
        // Check-In
        h(
          Tooltip,
          null,
          {
            default: () => [
              h(
                TooltipTrigger,
                { asChild: true },
                () =>
                  h(
                    Button,
                    {
                      size: 'icon',
                      onClick: () => checkInRow(row.original),
                      disabled:
                        !row.original.has_waiver || row.original.is_checked_in,
                    },
                    () => h(Check, { class: 'h-4 w-4' }),
                  ),
              ),
              h(TooltipContent, null, () => 'Check In Hiker'),
            ],
          },
        ),

        // Modify
        h(
          Tooltip,
          null,
          {
            default: () => [
              h(
                TooltipTrigger,
                { asChild: true },
                () =>
                  h(
                    Button,
                    {
                      variant: 'outline',
                      size: 'icon',
                      onClick: () => modifyRow(row.original),
                    },
                    () => h(Edit, { class: 'h-4 w-4' }),
                  ),
              ),
              h(TooltipContent, null, () => 'Modify Hiker'),
            ],
          },
        ),

        // Resend Waiver
        h(
          Tooltip,
          null,
          {
            default: () => [
              h(
                TooltipTrigger,
                { asChild: true },
                () =>
                  h(
                    Button,
                    {
                      variant: 'outline',
                      size: 'icon',
                      onClick: () => resendEmail(row.original),
                    },
                    () => h(MailPlus, { class: 'h-4 w-4' }),
                  ),
              ),
              h(TooltipContent, null, () => 'Resend Waiver'),
            ],
          },
        ),

        // Remove
        h(
          Tooltip,
          null,
          {
            default: () => [
              h(
                TooltipTrigger,
                { asChild: true },
                () =>
                  h(
                    Button,
                    {
                      variant: 'destructive',
                      size: 'icon',
                      onClick: () => removeRow(row.original),
                    },
                    () => h(Trash, { class: 'h-4 w-4' }),
                  ),
              ),
              h(TooltipContent, null, () => 'Remove Hiker'),
            ],
          },
        ),
      ]),
  }

]
const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
</script>
