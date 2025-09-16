<script setup>

import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table/index.js";
import {FlexRender, getCoreRowModel, getFilteredRowModel, useVueTable, getPaginationRowModel} from "@tanstack/vue-table";
import {Check, Edit, MailPlus, PlusCircle, Trash} from "lucide-vue-next";
import {Input} from "@/components/ui/input/index.js";
import {Button} from "@/components/ui/button/index.js";
import AddLateSignup from "@/components/admin/AddLateSignup.vue";
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

const props = defineProps({waiverData: { type: Object, required: true }})

const editUser = ref(null)
const confirmOpen = ref(false)
const confirmUser = ref(null)
const showAddSignup = ref(false)

const { postWithAuth } = useAuth()

function handleAdded(newUser) {
  data.value.push(newUser)
  data.value = [...data.value] // refresh table
  showAddSignup.value = false
}

// Row-level actions
async function checkInRow(user) {
  try {
    const res = await postWithAuth('/api/admin/check-in', {
      user_id: user.member_id,
    })
    if (!res.ok) {
      const errText = await res.text()
      throw new Error(errText || 'Unknown error')
    }
    user.is_checked_in = true
    if (res.status === 200) toast.success(`${user.name} has been checked in.`)
    if (res.status === 208) toast.info(`${user.name} was already checked in.`)
  } catch {
    toast.error("Check-in Failed")
  }
}

function modifyRow(user) {
  editUser.value = user
}

function resendEmail(user) {
  postWithAuth('/api/mail/resend', {
    email_type: "waiver",
    member_id: user.member_id
  })
    .then(res => {
      if (!res.ok) throw new Error('Failed to resend email')
      toast.success(`Email sent to ${user.name}`)
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
    const res = await postWithAuth('/api/admin/remove-user', {
      user_id: user.member_id
    })

    if (!res.ok) throw new Error(await res.text() || 'Error')
    const idx = data.value.findIndex(u => u.member_id === user.member_id)
    if (idx !== -1) {
      data.value.splice(idx, 1)
      data.value = [...data.value]
    }

    toast.success(`${user.name} removed`)
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
    accessorFn: row => `${row.name}`,
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
          ? `Driver (${row.original.vehicle_capacity} passengers)`
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
                      disabled: row.original.has_waiver,
                      onClick: () => resendEmail(row.original),
                    },
                    () => h(MailPlus, { class: 'h-4 w-4' }),
                  ),
              ),
              h(TooltipContent, null, () => 'Resend Waiver'),
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
  getPaginationRowModel: getPaginationRowModel(),
  initialState: {
    pagination: {
      pageIndex: 0,
      pageSize: 10,
    }
  }
})

</script>

<template>
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
          Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
        </span>
      </div>
  </div>

  <ModifyUserModal
      v-if="editUser"
      mode="waiver"
      :user="editUser"
      @close="editUser = null"
      @saved="() => editUser = null"
  />

  <AddLateSignup
    v-if="showAddSignup"
    @close="showAddSignup = false"
    @added="handleAdded"
  />

  <Dialog v-model:open="confirmOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Remove Hiker?</DialogTitle>
        <DialogDescription>
          Are you sure you want to remove
          {{ confirmUser?.name }}
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
