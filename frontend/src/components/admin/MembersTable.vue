<script setup>
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table/index.js";
import {FlexRender, getCoreRowModel, getFilteredRowModel, useVueTable} from "@tanstack/vue-table";
import {Button} from "@/components/ui/button/index.js";
import {ref, h, computed, onMounted} from "vue";
import {useAuth} from "@/lib/auth.js";
import MembersForm from "@/components/admin/MembersForm.vue";
import MembersBatchForm from "@/components/admin/MembersBatchForm.vue";
import {PlusCircle, ListPlus} from "lucide-vue-next"


const {fetchWithAuth } = useAuth()

const loading = ref(true)
const response = ref([])
const formIsOpen = ref(false);
const batchFormOpen = ref(false);
const editMemberData = ref({});


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

const data = computed(() => response.value )

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
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'is_officer',
    header: 'Officer',
    accessorFn: row => `${row.is_officer}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'edit',
    header: 'Modify',
    cell: ({ row }) =>
      h(Button, {
        variant: 'outline',
        size: 'sm',
        onClick: () => openForm(row.original)
      }, () => 'Edit'),
  }
];

const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})

onMounted(loadMembers)
</script>

<template>
    <MembersBatchForm v-model:isOpen="batchFormOpen" @submitted="handleFormSuccess"/>
<Button variant="outline" @click="openForm(null)"><PlusCircle/>Add Member</Button>
<Button class="ml-2" variant="outline" @click="batchFormOpen=true"><ListPlus/>Batch Add Members</Button>
<MembersForm
    v-model:isOpen="formIsOpen"
    :member-data="editMemberData"
    @submitted="handleFormSuccess"
/>
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