<script setup>

import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {FlexRender, getCoreRowModel, getFilteredRowModel, getSortedRowModel, useVueTable, getPaginationRowModel} from "@tanstack/vue-table";
import {Check, Edit, MailPlus, PlusCircle, Trash, MoreHorizontal, Undo2} from "lucide-vue-next";
import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import AddSignup from "@/components/admin/AddSignup.vue";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import ModifyUserModal from "@/components/admin/ModifyUserModal.vue";
import {ref, shallowRef, watch, h} from "vue";
import {toast} from "vue-sonner";
import {Badge} from "@/components/ui/badge";
import {Tooltip, TooltipContent, TooltipTrigger} from "@/components/ui/tooltip";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover";
import {useAuth} from "@/lib/auth.js";
import {HoverCard, HoverCardContent, HoverCardTrigger} from "@/components/ui/hover-card";
import {ButtonGroup} from "@/components/ui/button-group"
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-vue-next'
import ExportEmailButton from "@/components/admin/ExportEmailButton.vue";

const props = defineProps({
  mode: {type: String, required: true}, // "waiver" or "signup"
  users: { type: Object, required: true },
  currentTrailId: { type: Number, required: true },
})
const emit = defineEmits(['switched', 'cancelled', 'changed'])

const editUser = ref(null)
const confirmRemovalOpen = ref(false)
const confirmUser = ref(null)
const sendEmailConfirmUser = ref(null)
const undoOpen = ref(false)
const undoUser = ref(null)
const showAddSignup = ref(false)

const { postWithAuth, fetchWithAuth } = useAuth()

function handleAdded(newUser) {
  data.value.push(newUser)
  data.value = [...data.value]
  showAddSignup.value = false
  emit('changed')
}

async function checkInRow(user) {
  try {
    const res = await postWithAuth('/api/admin/check-in', { user_id: user.member_id })
    if (!res.ok) throw new Error(await res.text() || 'Unknown error')
    user.is_checked_in = true
    if (res.status === 200) { toast.success(`${user.name} checked in`); emit('changed') }
    if (res.status === 208) toast.info(`${user.name} was already checked in`)
  } catch {
    toast.error("Check-in failed")
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
    if (!res.ok) throw new Error(await res.text() || 'Unknown error')
    user.is_checked_in = false
    if (res.status === 200) { toast.success(`${user.name} check-in undone`); emit('changed') }
    if (res.status === 208) toast.info(`${user.name} was not checked in`)
  } catch {
    toast.error('Undo failed')
  } finally {
    undoOpen.value = false
    undoUser.value = null
  }
}

function modifyRow(user) { editUser.value = user }

function resendEmail(user) {
  postWithAuth('/api/mail/resend', { email_type: props.mode, member_id: user.member_id })
    .then(res => {
      if (!res.ok) throw new Error()
      toast.success(`Email sent to ${user.name}`)
    })
    .catch(() => toast.error('Failed to resend email'))
  sendEmailConfirmUser.value = null
}

function removeRow(user) {
  confirmUser.value = user
  confirmRemovalOpen.value = true
}

async function confirmedRemove() {
  const user = confirmUser.value
  try {
    const res = await postWithAuth('/api/admin/remove-user', { user_id: user.member_id })
    if (!res.ok) throw new Error(await res.text() || 'Error')
    const idx = data.value.findIndex(u => u.member_id === user.member_id)
    if (idx !== -1) {
      data.value.splice(idx, 1)
      data.value = [...data.value]
    }
    toast.success(`${user.name} removed`)
    emit('changed')
  } catch {
    toast.error('Remove failed')
  } finally {
    confirmRemovalOpen.value = false
    confirmUser.value = null
  }
}

const headerWithSortBtn = (label, ctx) => {
  const col = ctx.column
  const sorted = col.getIsSorted()
  const Icon = sorted === 'asc' ? ArrowUp : sorted === 'desc' ? ArrowDown : ArrowUpDown
  const labelNode = typeof label === 'string'
    ? h('span', label)
    : h('span', { class: 'inline-flex items-center gap-1' }, [
        h('span', { class: 'sm:hidden' }, label.short),
        h('span', { class: 'hidden sm:inline' }, label.long),
      ])
  return h('div', { class: 'inline-flex items-center w-fit gap-x-0 md:gap-x-2' }, [
    labelNode,
    h(Button, {
      variant: 'ghost', size: 'icon', class: 'h-4 w-4 p-0',
      onClick: () => col.toggleSorting(sorted === 'asc'),
    }, () => h(Icon, { class: 'h-4 w-4' })),
  ])
}

const data = shallowRef([...props.users])
watch(() => props.users, (users) => { data.value = [...users] })

const statusBadge = (yes) => h(Badge, {
  variant: 'outline',
  class: 'h-6 text-xs font-medium ' + (yes
    ? 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/30'
    : 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/30')
}, () => yes ? 'Yes' : 'No')

const columns = [
  {
    id: 'name',
    header: h('span', {}, 'Name'),
    accessorFn: row => row.name,
    cell: info => h('span', { class: 'inline-flex text-xs max-w-18 md:max-w-full md:text-sm line-clamp-3 md:line-clamp-0' }, info.getValue()),
    filterFn: (row, colId, filter) =>
      String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'type',
    enableSorting: true,
    accessorFn: row => row.transport_type,
    header: (ctx) => headerWithSortBtn('Type', ctx),
    sortingFn: (a, b) => {
      const r = (t) => (t === 'driver' ? 0 : t === 'self' ? 1 : 2)
      return r(a.getValue('type')) - r(b.getValue('type'))
    },
    cell: ({ row }) => {
      const t = row.original.transport_type
      if (t === 'driver') {
        return h(HoverCard, { openDelay: 100 }, {
          default: () => [
            h(HoverCardTrigger, { asChild: true }, () =>
              h('span', { class: 'inline-flex items-center gap-1' }, [
                h(Badge, { class: 'md:hidden px-1 py-0 size-7 text-xl text-center' }, () => 'D'),
                h('span', { class: 'hidden md:inline underline decoration-dotted text-sm' }, 'Driver'),
              ])
            ),
            h(HoverCardContent, { class: 'w-64' }, () =>
              h('div', { class: 'space-y-1' }, [
                h('div', { class: 'text-sm' }, row.original.vehicle_desc),
                h('div', { class: 'text-xs text-muted-foreground' }, `${row.original.vehicle_capacity} passengers`),
              ])
            ),
          ],
        })
      }
      if (t === 'passenger') {
        return h('span', { class: 'inline-flex items-center gap-1' }, [
          h(Badge, { class: 'md:hidden size-7 px-1 py-0 text-xl text-center' }, () => 'P'),
          h('span', { class: 'hidden md:inline text-sm' }, 'Passenger'),
        ])
      }
      return h('span', { class: 'inline-flex items-center gap-1' }, [
        h(Badge, { class: 'md:hidden size-7 px-1 py-0 text-xl text-center' }, () => 'S'),
        h('span', { class: 'hidden md:inline text-sm' }, 'Self-Transport'),
      ])
    }
  },
  {
    id: 'waiver',
    enableSorting: true,
    accessorFn: row => row.has_waiver,
    header: (ctx) => headerWithSortBtn({ long: "Waiver?", short: 'Wvr?' }, ctx),
    sortingFn: (a, b) => Number(a.original.has_waiver) - Number(b.original.has_waiver),
    cell: ({ row }) => statusBadge(row.original.has_waiver)
  },
  {
    id: 'checked_in',
    enableSorting: true,
    accessorFn: row => row.is_checked_in,
    header: (ctx) => headerWithSortBtn({ long: "Checked In?", short: 'Chkd?' }, ctx),
    sortingFn: (a, b) => Number(a.original.is_checked_in) - Number(b.original.is_checked_in),
    cell: ({ row }) => statusBadge(row.original.is_checked_in),
  },
  {
    id: 'actions',
    header: 'Actions',
    cell: ({ row }) =>
      h('div', { class: 'inline-flex items-center overflow-x-auto gap-1' }, [
        // Mobile: quick check-in icon
        h(Tooltip, null, {
          default: () => [
            h(TooltipTrigger, { asChild: true }, () =>
              h(Button, {
                class: 'size-7 ' + (props.mode === "waiver" ? 'md:hidden' : 'hidden'),
                size: 'icon',
                onClick: () => row.original.is_checked_in ? promptUndo(row.original) : checkInRow(row.original),
                disabled: !row.original.has_waiver && !row.original.is_checked_in,
              }, () => row.original.is_checked_in ? h(Undo2, { class: 'size-[18px]' }) : h(Check, { class: 'size-[18px]' }))
            ),
            h(TooltipContent, null, () => row.original.is_checked_in ? 'Undo Check-In' : 'Check In'),
          ],
        }),

        // Mobile: actions popover
        h('div', { class: 'md:hidden' }, [
          h(Popover, null, {
            default: () => [
              h(PopoverTrigger, { asChild: true }, () =>
                h(Button, { variant: 'ghost', size: 'icon' }, () => h(MoreHorizontal, { class: 'h-4 w-4' }))
              ),
              h(PopoverContent, { class: 'w-64 p-3' }, () => [
                h('div', { class: 'text-sm mb-3 text-muted-foreground' },
                  row.original.transport_type === 'passenger' ? 'Passenger'
                    : row.original.transport_type === 'self' ? 'Self-Transport'
                    : `Driver (${row.original.vehicle_desc}, ${row.original.vehicle_capacity} passengers)`
                ),
                h('div', { class: 'flex flex-wrap gap-2' }, [
                  !row.original.is_checked_in
                    ? h(Button, {
                        class: props.mode === "waiver" ? '' : 'hidden', size: 'sm',
                        onClick: () => checkInRow(row.original),
                        disabled: !row.original.has_waiver,
                      }, () => [h(Check, { class: 'h-4 w-4 mr-1' }), 'Check In'])
                    : h(Button, { size: 'sm', variant: 'outline', onClick: () => promptUndo(row.original) },
                        () => [h(Undo2, { class: 'h-4 w-4 mr-1' }), 'Undo Check-In']),
                  h(Button, {
                    size: 'sm', variant: 'outline', disabled: row.original.has_waiver,
                    onClick: () => { sendEmailConfirmUser.value = row.original },
                  }, () => [h(MailPlus, { class: 'h-4 w-4 mr-1' }), 'Resend Email']),
                  h(Button, { size: 'sm', variant: 'outline', onClick: () => modifyRow(row.original) },
                    () => [h(Edit, { class: 'h-4 w-4 mr-1' }), 'Modify']),
                  h(Button, { size: 'sm', variant: 'destructive', onClick: () => removeRow(row.original) },
                    () => [h(Trash, { class: 'h-4 w-4 mr-1' }), 'Remove']),
                ]),
              ]),
            ],
          }),
        ]),

        // Desktop: inline action buttons
        h(ButtonGroup, { class: 'hidden md:inline-flex' }, [
          props.mode === "waiver" ? h(Tooltip, null, {
            default: () => [
              h(TooltipTrigger, { asChild: true }, () =>
                h(Button, {
                  size: 'sm',
                  onClick: () => row.original.is_checked_in ? promptUndo(row.original) : checkInRow(row.original),
                  disabled: !row.original.has_waiver && !row.original.is_checked_in,
                }, () => row.original.is_checked_in ? h(Undo2, { class: 'h-4 w-4' }) : h(Check, { class: 'h-4 w-4' }))
              ),
              h(TooltipContent, null, () => row.original.is_checked_in ? 'Undo Check-In' : 'Check In'),
            ],
          }) : null,
          h(Tooltip, null, {
            default: () => [
              h(TooltipTrigger, { asChild: true }, () =>
                h(Button, {
                  variant: 'outline', size: 'sm', disabled: row.original.has_waiver,
                  onClick: () => { sendEmailConfirmUser.value = row.original },
                }, () => h(MailPlus, { class: 'h-4 w-4' }))
              ),
              h(TooltipContent, null, () => 'Resend Email'),
            ],
          }),
          h(Tooltip, null, {
            default: () => [
              h(TooltipTrigger, { asChild: true }, () =>
                h(Button, { variant: 'outline', size: 'sm', onClick: () => modifyRow(row.original) },
                  () => h(Edit, { class: 'h-4 w-4' }))
              ),
              h(TooltipContent, null, () => 'Modify Hiker'),
            ],
          }),
          h(Tooltip, null, {
            default: () => [
              h(TooltipTrigger, { asChild: true }, () =>
                h(Button, { variant: 'destructive', size: 'sm', onClick: () => removeRow(row.original) },
                  () => h(Trash, { class: 'h-4 w-4' }))
              ),
              h(TooltipContent, null, () => 'Remove Hiker'),
            ],
          }),
        ]),
      ]),
  },
]

const sorting = ref([])

const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getSortedRowModel: getSortedRowModel(),
  state: { get sorting() { return sorting.value } },
  onSortingChange: (updater) => {
    sorting.value = typeof updater === 'function' ? updater(sorting.value) : updater
  },
  initialState: {
    columnVisibility: {
      waiver: props.mode === 'waiver',
      checked_in: props.mode === 'waiver'
    },
    pagination: { pageIndex: 0, pageSize: 10 }
  }
})
</script>

<template>
  <!-- Toolbar -->
  <div class="flex flex-wrap items-center gap-2 py-2">
    <Input
      class="h-8 w-full sm:max-w-xs text-sm"
      placeholder="Filter hikers…"
      :model-value="table.getColumn('name')?.getFilterValue()"
      @update:model-value="(val) => table.getColumn('name')?.setFilterValue(val)"
    />
    <div class="flex flex-wrap gap-2 ml-auto">
      <ExportEmailButton mode="signup"/>
      <Button size="sm" @click="showAddSignup = true">
        <PlusCircle class="h-4 w-4" />
        {{ props.mode === 'signup' ? 'Add Signup' : 'Add Late Signup' }}
      </Button>
    </div>
  </div>

  <!-- Table -->
  <div class="rounded-lg border overflow-hidden">
    <Table
      class="table-fixed text-sm
             [&_th]:px-3 [&_td]:px-3
             [&_th]:py-2 [&_td]:py-2
             [&_th]:text-xs [&_td]:text-xs
             [&_th]:font-semibold"
    >
      <colgroup>
        <col v-for="col in table.getVisibleLeafColumns()" :key="col.id"
          :class="col.id === 'name' ? 'w-[40%]' : col.id === 'actions' ? 'w-[21%]' : 'w-[15%]'"
        />
      </colgroup>
      <TableHeader class="bg-muted/50">
        <TableRow v-for="hg in table.getHeaderGroups()" :key="hg.id" class="border-b">
          <TableHead v-for="h in hg.headers" :key="h.id">
            <FlexRender v-if="!h.isPlaceholder" :render="h.column.columnDef.header" :props="h.getContext()" />
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <template v-if="table.getRowModel().rows.length">
          <TableRow
            v-for="row in table.getRowModel().rows"
            :key="row.id"
            class="align-top odd:bg-muted/20 hover:bg-muted/40 transition-colors"
          >
            <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id" class="whitespace-normal break-words">
              <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
            </TableCell>
          </TableRow>
        </template>
        <TableRow v-else>
          <TableCell colspan="5" class="h-24 text-center text-muted-foreground text-sm">
            No hikers yet.
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <!-- Pagination -->
    <div class="flex items-center gap-2 px-3 py-2 border-t bg-muted/20">
      <Button variant="outline" size="sm" :disabled="!table.getCanPreviousPage()" @click="table.previousPage()">
        Previous
      </Button>
      <Button variant="outline" size="sm" :disabled="!table.getCanNextPage()" @click="table.nextPage()">
        Next
      </Button>
      <span class="ml-auto text-xs text-muted-foreground">
        Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
      </span>
    </div>
  </div>

  <!-- Modals -->
  <ModifyUserModal v-if="editUser" mode="waiver" :user="editUser" @close="editUser = null" @saved="() => { editUser = null; emit('changed') }" />
  <AddSignup v-if="showAddSignup" :mode="props.mode === 'signup' ? 'new' : 'late'" @close="showAddSignup = false" @added="handleAdded" />

  <Dialog v-model:open="confirmRemovalOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Remove hiker?</DialogTitle>
        <DialogDescription>Are you sure you want to remove {{ confirmUser?.name }} from this hike?</DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="outline" @click="confirmRemovalOpen = false">Cancel</Button>
        <Button variant="destructive" @click="confirmedRemove">Remove</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <Dialog v-model:open="undoOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Undo check-in?</DialogTitle>
        <DialogDescription>Are you sure you want to undo check-in for {{ undoUser?.name }}?</DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="outline" @click="undoOpen = false">Cancel</Button>
        <Button @click="confirmedUndo">Undo Check-In</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <Dialog v-model:open="sendEmailConfirmUser">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Resend {{ props.mode.charAt(0).toUpperCase() + props.mode.slice(1) }} Email?</DialogTitle>
        <DialogDescription>
          This will generate a new {{ props.mode }} link and send it to <span class="font-semibold text-foreground">{{ sendEmailConfirmUser?.name }}</span>.
          Any existing link will be invalidated.
        </DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="outline" @click="sendEmailConfirmUser = null">Cancel</Button>
        <Button @click="resendEmail(sendEmailConfirmUser)">Resend Email</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
