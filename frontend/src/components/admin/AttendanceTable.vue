<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { createColumnHelper, getCoreRowModel, useVueTable } from '@tanstack/vue-table'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem
} from '@/components/ui/dropdown-menu'
import {useAuth} from "@/lib/auth.js";

const { fetchWithAuth } = useAuth()


const props = defineProps({
  hikeId: { type: Number, required: true }
})

async function apiGet(path) {
  const res = await fetchWithAuth(path, { credentials: 'include' })
  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

const view = ref('attended') // attended|noshow|all
const transport = ref('any') // any|driver|passenger|self
const q = ref('')

const page = ref(1)
const pageSize = ref(25)

const total = ref(0)
const rows = ref([])

const queryString = computed(() => {
  const p = new URLSearchParams()
  p.set('view', view.value)
  p.set('transport', transport.value)
  if (q.value.trim()) p.set('q', q.value.trim())
  p.set('page', String(page.value))
  p.set('page_size', String(pageSize.value))
  return p.toString()
})

const csvHref = computed(() => {
  const p = new URLSearchParams()
  p.set('view', view.value)
  p.set('transport', transport.value)
  if (q.value.trim()) p.set('q', q.value.trim())
  return `/api/admin/history/hikes/${props.hikeId}/attendance.csv?${p.toString()}`
})

async function load() {
  const data = await apiGet(`/api/admin/history/hikes/${props.hikeId}/attendance?${queryString.value}`)
  console.info(data)
  rows.value = data.rows || []
  total.value = data.total || 0
}

onMounted(load)

watch(
    () => [props.hikeId, view.value, transport.value],
    () => {
      page.value = 1
      load()
    }
)

watch(
    () => [q.value, page.value, pageSize.value],
    () => load()
)

const columnHelper = createColumnHelper()

const columns = [
  columnHelper.accessor('name', { header: 'Name', cell: info => info.getValue() }),
  columnHelper.accessor('email', { header: 'Email', cell: info => info.getValue() }),
  columnHelper.accessor('transport_type', {
    header: 'Transport',
    cell: info => info.getValue()
  }),
  columnHelper.accessor('status', {
    header: 'Signup status',
    cell: info => info.getValue()
  }),
  columnHelper.accessor('is_checked_in', {
    header: 'Checked in',
    cell: info => info.getValue() ? 'Yes' : 'No'
  })
]

const table = useVueTable({
  get data() { return rows.value },
  columns,
  getCoreRowModel: getCoreRowModel()
})

const pageCount = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
</script>

<template>
  <div class="space-y-3">
    <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-3">
      <Tabs v-model="view" class="w-full md:w-auto">
        <TabsList>
          <TabsTrigger value="attended">Attended</TabsTrigger>
          <TabsTrigger value="noshow">No-shows</TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>
      </Tabs>

      <div class="flex items-center gap-2">
        <Button variant="outline" :class="transport==='any' ? 'bg-muted' : ''" @click="transport='any'">All</Button>
        <Button variant="outline" :class="transport==='passenger' ? 'bg-muted' : ''" @click="transport='passenger'">Passengers</Button>
        <Button variant="outline" :class="transport==='driver' ? 'bg-muted' : ''" @click="transport='driver'">Drivers</Button>
        <Button variant="outline" :class="transport==='self' ? 'bg-muted' : ''" @click="transport='self'">Self</Button>
      </div>

      <div class="flex-1" />

      <Input v-model="q" placeholder="Search name/email..." class="md:max-w-[280px]" />

      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="outline">Export CSV</Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem as-child>
            <a :href="csvHref">Export (filters applied)</a>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>

    <div class="text-sm text-muted-foreground">
      Showing <Badge variant="secondary">{{ rows.length }}</Badge> of <Badge variant="secondary">{{ total }}</Badge>
    </div>

    <div class="rounded-md border overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="border-b bg-muted/30">
        <tr>
          <th v-for="h in table.getHeaderGroups()[0].headers" :key="h.id" class="text-left p-2">
            {{ h.column.columnDef.header }}
          </th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="r in table.getRowModel().rows" :key="r.id" class="border-b last:border-0">
          <td v-for="c in r.getVisibleCells()" :key="c.id" class="p-2">
            {{ c.getValue() }}
          </td>
        </tr>
        <tr v-if="!rows.length">
          <td class="p-3 text-muted-foreground" :colspan="columns.length">No results.</td>
        </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between gap-3">
      <div class="text-sm text-muted-foreground">
        Page {{ page }} / {{ pageCount }}
      </div>
      <div class="flex gap-2">
        <Button variant="outline" :disabled="page<=1" @click="page--">Prev</Button>
        <Button variant="outline" :disabled="page>=pageCount" @click="page++">Next</Button>
      </div>
    </div>
  </div>
</template>
