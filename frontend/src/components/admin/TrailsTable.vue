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
import {useRouter} from "vue-router";
import TrailsForm from "@/components/admin/TrailsForm.vue";
import DifficultyBadge from "@/components/common/DifficultyBadge.vue";
import Link from "@/components/common/Link.vue";
import {difficulties} from "@/lib/common.js"
import {PlusCircle, Pencil} from "lucide-vue-next"
import {Input} from "@/components/ui/input/index.js";

const { fetchWithAuth } = useAuth()
const router = useRouter()

const loading = ref(true)
const response = ref([])
const formIsOpen = ref(false)
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
    header: '',
    cell: ({ row }) =>
      h(Button, {
        variant: 'outline',
        size: 'sm',
        onClick: () => router.push({ name: 'Trail Detail', params: { trailId: String(row.original.id) } })
      }, () => [h(Pencil, { class: 'h-3.5 w-3.5 mr-1' }), 'Edit']),
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
  <!-- Toolbar -->
  <div class="flex flex-wrap items-center gap-2 pb-3">
    <Input
      v-model="search"
      class="h-8 max-w-xs text-sm"
      placeholder="Search name, location, difficulty…"
    />
    <Button size="sm" variant="outline" @click="formIsOpen = true">
      <PlusCircle class="h-4 w-4"/>Add Trail
    </Button>
    <span v-if="!loading" class="ml-auto text-xs text-muted-foreground">{{ response.length }} trails</span>
  </div>

  <TrailsForm v-model:isOpen="formIsOpen" :trail-data="null" @submitted="loadTrails" />

  <!-- Table -->
  <div class="rounded-lg border overflow-x-auto">
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
          <TableCell colspan="7" class="h-24 text-center text-sm text-muted-foreground">
            No trails found.
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