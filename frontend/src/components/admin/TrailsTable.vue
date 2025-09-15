<script setup>
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table/index.js";
import {FlexRender, getCoreRowModel, getFilteredRowModel, useVueTable} from "@tanstack/vue-table";
import {Button} from "@/components/ui/button/index.js";
import {ref, h, computed, onMounted} from "vue";
import {useAuth} from "@/lib/auth.js";
import TrailsForm from "@/components/admin/TrailsForm.vue";
import {useRouter} from "vue-router";

const { state: signOut, fetchWithAuth } = useAuth()
const router = useRouter()

const loading = ref(true)
const response = ref([])
const formIsOpen = ref(false);
const editTrailData = ref({});

const difficulties = [
    'Easy', 'Moderate', 'Difficult', 'Very Difficult'
]

async function loadTrails() {
  loading.value = true
  try {
    const res = await fetchWithAuth('/admin/trails')
    response.value = await res.json()
    console.info(response.value)
  } catch {
    response.value = []
  } finally {
    loading.value = false
  }
}

function openForm(trailData= null)
{
    editTrailData.value = trailData
    formIsOpen.value = true;
}
function handleFormSuccess()
{
    loadTrails();
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
    id: 'location',
    header: 'Location',
    accessorFn: row => `${row.location}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'length_mi',
    header: 'Length (mi)',
    accessorFn: row => `${row.length_mi}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'estimated_time_hr',
    header: 'Estimated Time (hrs)',
    accessorFn: row => `${row.estimated_time_hr}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'required_water_liters',
    header: 'Required Water (l)',
    accessorFn: row => `${row.required_water_liters}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'difficulty',
    header: 'Difficulty',
    accessorFn: row => `${difficulties[row.difficulty]}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'alltrails_url',
    header: 'All trails',
    accessorFn: row => `${row.alltrails_url}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'trailhead_gmaps_url',
    header: 'Google Maps',
    accessorFn: row => `${row.trailhead_gmaps_url}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'trailhead_amaps_url',
    header: 'Apple Maps',
    accessorFn: row => `${row.trailhead_amaps_url}`,
    cell: info => info.getValue(),
    filterFn: (row, colId, filter) =>
        String(row.getValue(colId)).toLowerCase().includes(filter.toLowerCase())
  },
  {
    id: 'description',
    header: 'Description',
    accessorFn: row => `${row.description}`,
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

onMounted(loadTrails)
</script>

<template>
<Button variant="outline" @click="openForm(null)">+ Add Trail</Button>
<TrailsForm
    v-model:isOpen="formIsOpen"
    :trail-data="editTrailData"
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