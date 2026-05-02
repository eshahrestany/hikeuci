<script setup>
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table/index.js";
import {
  FlexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useVueTable
} from "@tanstack/vue-table";
import {Button} from "@/components/ui/button/index.js";
import {ref, h, computed, onMounted, watch} from "vue";
import {useAuth} from "@/lib/auth.js";
import MembersForm from "@/components/admin/MembersForm.vue";
import MembersBatchForm from "@/components/admin/MembersBatchForm.vue";
import {PlusCircle, ListPlus, History, Pencil, FileDown, Loader2} from "lucide-vue-next"
import { toast } from 'vue-sonner'
import { useRouter } from "vue-router"
import {Input} from "@/components/ui/input/index.js";
import { Badge } from "@/components/ui/badge";


const router = useRouter()
const {fetchWithAuth, postWithAuth } = useAuth()

const loading = ref(true)
const response = ref([])
const formIsOpen = ref(false);
const batchFormOpen = ref(false);
const editMemberData = ref({});
const search = ref('')
const exportingMembers = ref(new Set())

async function exportWaivers(memberId) {
  if (exportingMembers.value.has(memberId)) return
  exportingMembers.value = new Set([...exportingMembers.value, memberId])

  try {
    const res = await postWithAuth('/api/admin/export-waivers', { member_id: memberId })
    if (!res.ok) {
      const err = await res.json()
      toast.error('Export failed', { description: err.error || 'Could not start export' })
      return
    }
    const { task_id, member_name } = await res.json()

    // Poll for completion (timeout after 60s)
    const maxAttempts = 60
    let status = 'pending'
    for (let i = 0; i < maxAttempts && status === 'pending'; i++) {
      await new Promise(r => setTimeout(r, 1000))
      const statusRes = await fetchWithAuth(`/api/admin/export-waivers/${task_id}/status`)
      const statusData = await statusRes.json()
      status = statusData.status
      if (status === 'failed') {
        toast.error('Export failed', { description: statusData.error || 'Task encountered an error' })
        return
      }
    }
    if (status !== 'done') {
      toast.error('Export timed out', { description: 'Please try again' })
      return
    }

    // Trigger download
    const dlRes = await fetchWithAuth(`/api/admin/export-waivers/${task_id}/download`)
    if (!dlRes.ok) {
      toast.error('Download failed')
      return
    }
    const blob = await dlRes.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${member_name} - Waivers.zip`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    toast.success(`Exported waivers for ${member_name}`)
  } catch (e) {
    console.error('Export failed:', e)
    toast.error('Export failed', { description: 'An unexpected error occurred' })
  } finally {
    const next = new Set(exportingMembers.value)
    next.delete(memberId)
    exportingMembers.value = next
  }
}

async function loadMembers() {
  loading.value = true
  try {
    const res = await fetchWithAuth('/api/admin/members')
    response.value = await res.json()
    console.info(response.value)
  } catch {
    response.value = []
  } finally {
    loading.value = false
  }
}

function openForm(memberData= null)
{
    editMemberData.value = memberData
    formIsOpen.value = true;
}
function handleFormSuccess()
{
    loadMembers();
}

const data = computed(() => {
  if (!search.value) {
    return response.value;
  }
  return response.value.filter(member =>
    member.name.toLowerCase().includes(search.value.toLowerCase()) ||
    member.email.toLowerCase().includes(search.value.toLowerCase()) ||
    member.tel?.toLowerCase().includes(search.value.toLowerCase())
  );
} )

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
    id: 'email',
    header: 'Email',
    accessorFn: row => `${row.email}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'tel',
    header: 'Phone #',
    accessorFn: row => `${row.tel}`,
    cell: info => info.getValue() !== 'null' ? info.getValue() : h(Badge, {variant: 'secondary'}, 'Not Provided'),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'is_officer',
    header: 'Officer',
    accessorFn: row => `${row.is_officer}`,
    cell: info => info.getValue() === 'true' ? h(Badge, {variant: 'default'}, 'Yes') : h(Badge, {variant: 'secondary'}, 'No'),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'subscribed_to_mailing_list',
    header: 'Mailing List',
    accessorFn: row => row.subscribed_to_mailing_list,
    cell: info => info.getValue()
      ? h(Badge, {variant: 'default'}, 'Subscribed')
      : h(Badge, {variant: 'secondary'}, 'Unsubscribed'),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'edit',
    header: '',
    cell: ({ row }) =>
      h('div', { class: 'flex items-center gap-2' }, [
        h(Button, {
          variant: 'outline',
          size: 'sm',
          onClick: () => openForm(row.original)
        }, () => [h(Pencil, { class: 'h-3.5 w-3.5 mr-1' }), 'Edit Member']),
        h(Button, {
          variant: 'outline',
          size: 'sm',
          onClick: () => router.push({ name: 'Member History', params: { memberId: row.original.id } })
        }, () => [h(History, { class: 'h-3.5 w-3.5 mr-1' }), 'Signup History']),
        h(Button, {
          variant: 'outline',
          size: 'sm',
          disabled: exportingMembers.value.has(row.original.id),
          onClick: () => exportWaivers(row.original.id)
        }, () => [
          exportingMembers.value.has(row.original.id)
            ? h(Loader2, { class: 'h-3.5 w-3.5 mr-1 animate-spin' })
            : h(FileDown, { class: 'h-3.5 w-3.5 mr-1' }),
          exportingMembers.value.has(row.original.id) ? 'Exporting…' : 'Export Waivers'
        ]),
      ]),
  }
];

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

onMounted(loadMembers)
</script>

<template>
  <MembersBatchForm v-model:isOpen="batchFormOpen" @submitted="handleFormSuccess"/>
  <MembersForm
      v-model:isOpen="formIsOpen"
      :member-data="editMemberData"
      @submitted="handleFormSuccess"
  />
  <!-- Toolbar -->
  <div class="flex flex-wrap items-center gap-2 pb-3">
    <Input
      v-model="search"
      class="h-8 max-w-xs text-sm"
      placeholder="Search name, email, phone…"
    />
    <Button size="sm" variant="outline" @click="openForm(null)"><PlusCircle class="h-4 w-4"/>Add Member</Button>
    <Button size="sm" variant="outline" @click="batchFormOpen=true"><ListPlus class="h-4 w-4"/>Batch Add</Button>
    <span v-if="!loading" class="ml-auto text-xs text-muted-foreground">{{ response.length }} members</span>
  </div>

  <!-- Table -->
  <div class="rounded-lg border overflow-hidden">
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
          <TableCell colspan="5" class="h-24 text-center text-sm text-muted-foreground">
            No members found.
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <!-- Pagination -->
    <div class="flex items-center gap-2 px-3 py-2 border-t bg-muted/20">
      <Button variant="outline" size="sm" :disabled="!table.getCanPreviousPage()" @click="table.previousPage()">Previous</Button>
      <Button variant="outline" size="sm" :disabled="!table.getCanNextPage()" @click="table.nextPage()">Next</Button>
      <span class="ml-auto text-xs text-muted-foreground">
        Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
      </span>
    </div>
  </div>
</template>