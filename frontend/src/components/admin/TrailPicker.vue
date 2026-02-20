<script setup>
import { ref, computed, onMounted } from 'vue'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableHead, TableRow, TableHeader, TableCell, TableBody } from '@/components/ui/table'
import { useAuth } from '@/lib/auth.js'
import DifficultyBadge from '@/components/common/DifficultyBadge.vue'

const props = defineProps({
  // 'single': modelValue is a trail object | null
  // 'multi':  modelValue is a trail object[]
  mode:      { type: String, default: 'single' },
  maxSelect: { type: Number, default: 3 },
  excludeId: { type: Number, default: null },
  modelValue: { default: null },
})
const emit = defineEmits(['update:modelValue'])

const { fetchWithAuth } = useAuth()

const allTrails = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchWithAuth('/api/admin/trails')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    allTrails.value = data.map(t => ({
      id: t.id,
      name: t.name,
      location: t.location,
      difficulty: t.difficulty,
    }))
  } catch (e) {
    error.value = e?.message ?? 'Failed to load trails'
  } finally {
    loading.value = false
  }
}

onMounted(load)

const filteredTrails = computed(() => {
  let list = props.excludeId != null
    ? allTrails.value.filter(t => t.id !== props.excludeId)
    : allTrails.value
  const q = search.value.trim().toLowerCase()
  if (!q) return list
  const difficultyLabels = ['easy', 'moderate', 'difficult', 'very difficult']
  return list.filter(t =>
    (t.name ?? '').toLowerCase().includes(q) ||
    (t.location ?? '').toLowerCase().includes(q) ||
    (difficultyLabels[t.difficulty] ?? '').includes(q)
  )
})

const selectedIds = computed(() => {
  if (props.mode === 'multi') return (props.modelValue ?? []).map(t => t.id)
  return props.modelValue ? [props.modelValue.id] : []
})

function isSelected(id) {
  return selectedIds.value.includes(id)
}

function toggle(trail) {
  if (props.mode === 'single') {
    emit('update:modelValue', isSelected(trail.id) ? null : trail)
  } else {
    const current = [...(props.modelValue ?? [])]
    const i = current.findIndex(t => t.id === trail.id)
    if (i >= 0) {
      current.splice(i, 1)
    } else if (current.length < props.maxSelect) {
      current.push(trail)
    }
    emit('update:modelValue', current)
  }
}

const selectionLabel = computed(() =>
  props.mode === 'multi'
    ? `${selectedIds.value.length}/${props.maxSelect} selected`
    : selectedIds.value.length ? '1/1 selected' : '0/1 selected'
)
</script>

<template>
  <div class="space-y-2">
    <div v-if="loading" class="grid gap-3 md:grid-cols-2">
      <Skeleton class="h-10 w-full rounded-md" />
      <Skeleton class="h-10 w-full rounded-md" />
      <Skeleton v-if="mode === 'multi'" class="h-10 w-full rounded-md" />
      <p class="text-xs text-muted-foreground col-span-full">Loading trails…</p>
    </div>
    <p v-else-if="error" class="text-sm text-red-500">{{ error }}</p>

    <template v-else>
      <div class="flex items-center justify-between gap-3">
        <Input
          v-model="search"
          class="max-w-md"
          placeholder="Search name, location, difficulty…"
        />
        <p class="text-xs text-muted-foreground shrink-0">{{ selectionLabel }}</p>
      </div>

      <Table class="table-fixed">
        <TableHeader>
          <TableRow>
            <TableHead class="w-10">Select</TableHead>
            <TableHead class="w-2/5">Name</TableHead>
            <TableHead class="w-2/5">Location</TableHead>
            <TableHead class="w-28">Difficulty</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="t in filteredTrails"
            :key="t.id"
            class="cursor-pointer"
            @click="toggle(t)"
          >
            <TableCell>
              <input
                v-if="mode === 'multi'"
                type="checkbox"
                :checked="isSelected(t.id)"
                :disabled="!isSelected(t.id) && selectedIds.length >= maxSelect"
                @click.stop
                @change="toggle(t)"
              />
              <input
                v-else
                type="radio"
                name="trail-picker"
                :checked="isSelected(t.id)"
                @click.stop
                @change="toggle(t)"
              />
            </TableCell>
            <TableCell class="font-medium whitespace-normal break-words">{{ t.name }}</TableCell>
            <TableCell class="whitespace-normal break-words">{{ t.location || '—' }}</TableCell>
            <TableCell><DifficultyBadge :difficulty="t.difficulty" /></TableCell>
          </TableRow>

          <TableRow v-if="!filteredTrails.length">
            <TableCell colspan="4" class="text-center text-sm text-muted-foreground py-6">
              No trails match your search.
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </template>
  </div>
</template>
