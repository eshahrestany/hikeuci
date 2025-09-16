<script setup>

import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table/index.js";
import {FlexRender, getCoreRowModel, getFilteredRowModel, useVueTable, getPaginationRowModel} from "@tanstack/vue-table";
import {Check, Edit, MailPlus, PlusCircle, Trash, MoreHorizontal, RotateCcw, Undo2} from "lucide-vue-next";
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
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover/index.js";
import {useAuth} from "@/lib/auth.js";

const props = defineProps({waiverData: { type: Object, required: true }})

const editUser = ref(null)
const confirmOpen = ref(false)
const confirmUser = ref(null)
const undoOpen = ref(false)
const undoUser = ref(null)
const showAddSignup = ref(false)

const { postWithAuth, fetchWithAuth } = useAuth()

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

function promptUndo(user) {
  undoUser.value = user
  undoOpen.value = true
}

async function confirmedUndo() {
  const user = undoUser.value
  try {
    const res = await fetchWithAuth('/api/admin/check-in', {
      method: 'DELETE',
      body: JSON.stringify({ user_id: user.member_id }),
    })
    if (!res.ok) {
      const errText = await res.text()
      throw new Error(errText || 'Unknown error')
    }
    user.is_checked_in = false
    if (res.status === 200) toast.success(`${user.name} check-in undone.`)
    if (res.status === 208) toast.info(`${user.name} was not checked in.`)
  } catch {
    toast.error('Undo failed')
  } finally {
    undoOpen.value = false
    undoUser.value = null
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
    cell: info => h('span', { class: 'break-words' }, info.getValue()),
    filterFn: (row, colId, filter) =>
      String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'type',
    header: () => h('span', { class: 'hidden md:inline' }, 'Type'),
    cell: ({ row }) =>
      h('span', { class: 'hidden md:inline break-words' },
        row.original.transport_type === "passenger"
          ? 'Passenger'
          : row.original.transport_type === "driver"
            ? `Driver (${row.original.vehicle_capacity} passengers)`
            : 'Self-Transport'
      ),
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
      h('div', { class: 'flex items-center gap-2' }, [
        // Mobile: quick Check-In / Undo icon
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
                      class: 'md:hidden',
                      size: 'icon',
                      onClick: () => row.original.is_checked_in ? promptUndo(row.original) : checkInRow(row.original),
                      disabled: !row.original.has_waiver && !row.original.is_checked_in,
                    },
                    () => row.original.is_checked_in ? h(Undo2, { class: 'h-4 w-4' }) : h(Check, { class: 'h-4 w-4' }),
                  ),
              ),
              h(TooltipContent, null, () => row.original.is_checked_in ? 'Undo Check-In' : 'Check In Hiker'),
            ],
          },
        ),

        // Mobile: compact actions popover (ellipsis)
        h('div', { class: 'md:hidden' }, [
          h(Popover, null, {
            default: () => [
              h(PopoverTrigger, { asChild: true }, () =>
                h(Button, { variant: 'ghost', size: 'icon' }, () => h(MoreHorizontal, { class: 'h-4 w-4' }))
              ),
              h(PopoverContent, { class: 'w-64 p-3' }, () => [
                h('div', { class: 'text-sm mb-3' }, `Type: ${row.original.transport_type === 'passenger' ? 'Passenger' : row.original.transport_type === 'driver' ? `Driver (${row.original.vehicle_capacity} passengers)` : 'Self-Transport'}`),
                h('div', { class: 'flex flex-wrap gap-2' }, [
                  !row.original.is_checked_in ? h(Button, {
                    size: 'sm',
                    onClick: () => checkInRow(row.original),
                    disabled: !row.original.has_waiver,
                  }, () => [h(Check, { class: 'h-4 w-4 mr-1' }), 'Check In']) : h(Button, {
                    size: 'sm', variant: 'outline',
                    onClick: () => promptUndo(row.original),
                  }, () => [h(RotateCcw, { class: 'h-4 w-4 mr-1' }), 'Undo Check-In']),
                  h(Button, {
                    size: 'sm', variant: 'outline',
                    disabled: row.original.has_waiver,
                    onClick: () => resendEmail(row.original),
                  }, () => [h(MailPlus, { class: 'h-4 w-4 mr-1' }), 'Resend Waiver']),
                  h(Button, {
                    size: 'sm', variant: 'outline',
                    onClick: () => modifyRow(row.original),
                  }, () => [h(Edit, { class: 'h-4 w-4 mr-1' }), 'Modify']),
                  h(Button, {
                    size: 'sm', variant: 'destructive',
                    onClick: () => removeRow(row.original),
                  }, () => [h(Trash, { class: 'h-4 w-4 mr-1' }), 'Remove']),
                ]),
              ]),
            ],
          }),
        ]),

        // Desktop: show individual action icons inline
        h('div', { class: 'hidden md:flex space-x-2' }, [
          // Check-In / Undo
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
                        onClick: () => row.original.is_checked_in ? promptUndo(row.original) : checkInRow(row.original),
                        disabled: !row.original.has_waiver && !row.original.is_checked_in,
                      },
                      () => row.original.is_checked_in ? h(RotateCcw, { class: 'h-4 w-4' }) : h(Check, { class: 'h-4 w-4' }),
                    ),
                ),
                h(TooltipContent, null, () => row.original.is_checked_in ? 'Undo Check-In' : 'Check In Hiker'),
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
      ]),
  },

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
  <div class="flex items-center py-2 flex-nowrap">
    <Input
      class="max-w-[12rem] sm:max-w-sm mr-3"
      placeholder="Filter names..."
      :model-value="table.getColumn('name')?.getFilterValue()"
      @update:model-value="(val) => table.getColumn('name')?.setFilterValue(val)"
    />
    <Button class="md:ml-auto shrink-0" @click="showAddSignup = true">
      <PlusCircle class="h-4 w-4" />Add Late Signup
    </Button>
  </div>

  <!-- Table of Users -->
  <div class="rounded-md border overflow-x-auto w-full">
    <Table>
      <TableHeader>
        <TableRow v-for="hg in table.getHeaderGroups()" :key="hg.id">
          <TableHead v-for="h in hg.headers" :key="h.id" class="whitespace-normal">
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
            <TableRow class="align-top">
              <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id" class="whitespace-normal break-words">
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

  <Dialog v-model:open="undoOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Undo Check-In?</DialogTitle>
        <DialogDescription>
          Are you sure you want to undo check-in for
          {{ undoUser?.name }}?
        </DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="outline" @click="undoOpen = false">
          Cancel
        </Button>
        <Button @click="confirmedUndo">
          Undo Check-In
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
