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
import {ref, h, computed, onMounted} from "vue";
import {useAuth} from "@/lib/auth.js";
import TrailsForm from "@/components/admin/TrailsForm.vue";
import DifficultyBadge from "@/components/common/DifficultyBadge.vue";
import Link from "@/components/common/Link.vue";
import {difficulties} from "@/lib/common.js"
import {PlusCircle} from "lucide-vue-next"
import {Input} from "@/components/ui/input/index.js";

const { fetchWithAuth } = useAuth()

const loading = ref(true)
const response = ref([])
const formIsOpen = ref(false);
const editTrailData = ref({});
const search = ref('')


async function loadTrails() {
  loading.value = true
  try {
    const res = await fetchWithAuth('/api/admin/trails')
    if (!res.ok) {
      throw Error(res.status)
    }
    response.value = await res.json()
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

const data = computed(() => {
  if (!search.value) {
    return response.value;
  }
  return response.value.filter(trail =>
    trail.name.toLowerCase().includes(search.value.toLowerCase()) ||
    trail.location.toLowerCase().includes(search.value.toLowerCase()) ||
    difficulties[trail.difficulty].toLowerCase().includes(search.value.toLowerCase())
  );
} )
const columns = [
  {
    id: 'name',
    header: 'Name',
    accessorFn: row => `${row.name}`, // keep for filter/sort
    cell: ({ row }) =>
        h(Link, {
          to: row.original.alltrails_url,
          text: row.original.name,
          newTab: true,
          size: 14,
        }),
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
    cell: info => h(DifficultyBadge, {difficulty: info.row.original.difficulty}),
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
  getPaginationRowModel: getPaginationRowModel(),
  initialState: {
    pagination: {
      pageIndex: 0,
      pageSize: 10,
    }
  }
})

onMounted(loadTrails)
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <Input
      v-model="search"
      class="max-w-[300px]"
      placeholder="Search name, location, difficulty…"
    />
    <Button variant="outline" @click="openForm(null)"><PlusCircle/>Add Trail</Button>
  </div>
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
</template>