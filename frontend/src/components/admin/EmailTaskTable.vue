<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/lib/auth.js'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import { ArrowUp, ArrowDown, ArrowUpDown, Search } from 'lucide-vue-next'
import { toast } from 'vue-sonner'

const STATUS_CLASS = {
  sent:    'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/30',
  pending: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30',
  failed:  'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/30',
}

const props = defineProps({
  campaignId: { type: Number, required: true },
  campaignType: { type: String, default: null },
  refreshTick: { type: Number, default: 0 },
})

const isManual = computed(() => props.campaignType === 'manual')

const { fetchWithAuth } = useAuth()
const route = useRoute()
const router = useRouter()

// Initialize from URL so deep-links restore state
const VALID_STATUSES = ['pending', 'sent', 'failed']
const status = ref(VALID_STATUSES.includes(route.query.status) ? route.query.status : 'all')
const q = ref(route.query.q || '')
const sort = ref(['sent_at', 'status', 'attempts'].includes(route.query.sort) ? route.query.sort : 'sent_at')
const dir = ref(route.query.dir === 'asc' ? 'asc' : 'desc')
const page = ref(Math.max(1, parseInt(route.query.page) || 1))

const loading = ref(false)
const error = ref('')
const items = ref([])
const total = ref(0)
const hasNext = ref(false)
const maxAttempts = ref(3)
const initialLoaded = ref(false)

let searchTimer = null
let inFlightController = null

function syncUrl() {
  const next = { ...route.query }
  next.status = status.value === 'all' ? undefined : status.value
  next.q = q.value || undefined
  next.sort = sort.value === 'sent_at' ? undefined : sort.value
  next.dir = dir.value === 'desc' ? undefined : dir.value
  next.page = page.value === 1 ? undefined : String(page.value)
  router.replace({ query: next })
}

async function load({ background = false } = {}) {
  if (!props.campaignId) return
  if (inFlightController) inFlightController.abort()
  inFlightController = new AbortController()

  const showSkeleton = !background && !initialLoaded.value
  if (showSkeleton) loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({ page: String(page.value) })
    if (status.value !== 'all') params.set('status', status.value)
    if (q.value.trim()) params.set('q', q.value.trim())
    if (sort.value !== 'sent_at') params.set('sort', sort.value)
    if (dir.value !== 'desc') params.set('dir', dir.value)
    const res = await fetchWithAuth(
      `/api/admin/email-campaigns/${props.campaignId}/tasks?${params.toString()}`,
      { signal: inFlightController.signal },
    )
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const body = await res.json()
    if (background && initialLoaded.value) {
      // Merge in-place so unchanged rows aren't recreated in the DOM.
      const newById = new Map(body.items.map(i => [i.id, i]))
      items.value = items.value
        .map(item => newById.has(item.id) ? { ...item, ...newById.get(item.id) } : item)
        .filter(item => newById.has(item.id))
      for (const newItem of body.items) {
        if (!items.value.some(i => i.id === newItem.id)) items.value.push(newItem)
      }
    } else {
      items.value = body.items
    }
    total.value = body.total
    hasNext.value = body.has_next
    maxAttempts.value = body.max_attempts
    initialLoaded.value = true
  } catch (e) {
    if (e.name === 'AbortError') return
    console.error('Failed to load tasks:', e)
    error.value = 'Failed to load tasks.'
    toast.error('Failed to load tasks')
  } finally {
    if (showSkeleton) loading.value = false
  }
}

watch(() => props.campaignId, () => {
  initialLoaded.value = false
  page.value = 1
  syncUrl()
  load()
})

watch(() => props.refreshTick, () => { load({ background: true }) })

watch(q, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    syncUrl()
    load()
  }, 300)
})

watch(status, () => {
  page.value = 1
  syncUrl()
  load()
})

function toggleSort(field) {
  if (sort.value === field) {
    dir.value = dir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sort.value = field
    dir.value = field === 'sent_at' ? 'desc' : 'asc'
  }
  page.value = 1
  syncUrl()
  load()
}

function nextPage() {
  if (!hasNext.value) return
  page.value += 1
  syncUrl()
  load()
}

function prevPage() {
  if (page.value <= 1) return
  page.value -= 1
  syncUrl()
  load()
}

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / 50)))

function formatSentAt(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit',
  })
}

function sortIcon(field) {
  if (sort.value !== field) return ArrowUpDown
  return dir.value === 'asc' ? ArrowUp : ArrowDown
}

function attemptsClass(task) {
  return task.status === 'failed' && task.attempts >= maxAttempts.value
    ? 'text-red-600 dark:text-red-400 font-medium'
    : ''
}

const EMAIL_TYPE_LABEL = {
  voting:      'Voting',
  signup:      'Signup',
  waiver:      'Waiver',
  waitlist:    'Waitlist',
  late_signup: 'Late Signup',
}

function emailTypeLabel(type) {
  return EMAIL_TYPE_LABEL[type] || type || '—'
}

onMounted(load)
onUnmounted(() => {
  if (searchTimer) clearTimeout(searchTimer)
  if (inFlightController) inFlightController.abort()
})
</script>

<template>
  <div class="space-y-3">
    <!-- Filter row -->
    <div class="flex flex-wrap items-center gap-2">
      <Select v-model="status">
        <SelectTrigger class="w-[160px]">
          <SelectValue placeholder="All statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All statuses</SelectItem>
          <SelectItem value="pending">Pending</SelectItem>
          <SelectItem value="sent">Sent</SelectItem>
          <SelectItem value="failed">Failed</SelectItem>
        </SelectContent>
      </Select>
      <div class="relative flex-1 min-w-[220px] max-w-md">
        <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          v-model="q"
          placeholder="Search by name or email"
          class="pl-9"
        />
      </div>
    </div>

    <!-- Table -->
    <div class="rounded-lg border overflow-hidden">
      <Table>
        <TableHeader class="bg-muted/50">
          <TableRow class="border-b">
            <TableHead class="px-3 py-2 text-xs font-semibold">Member</TableHead>
            <TableHead class="px-3 py-2 text-xs font-semibold">Email</TableHead>
            <TableHead v-if="isManual" class="px-3 py-2 text-xs font-semibold">Type</TableHead>
            <TableHead class="px-3 py-2 text-xs font-semibold">
              <button class="inline-flex items-center gap-1 hover:text-foreground" @click="toggleSort('status')">
                Status <component :is="sortIcon('status')" class="h-3 w-3" />
              </button>
            </TableHead>
            <TableHead class="px-3 py-2 text-xs font-semibold">
              <button class="inline-flex items-center gap-1 hover:text-foreground" @click="toggleSort('attempts')">
                Attempts <component :is="sortIcon('attempts')" class="h-3 w-3" />
              </button>
            </TableHead>
            <TableHead class="px-3 py-2 text-xs font-semibold">
              <button class="inline-flex items-center gap-1 hover:text-foreground" @click="toggleSort('sent_at')">
                Sent At <component :is="sortIcon('sent_at')" class="h-3 w-3" />
              </button>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <template v-if="loading">
            <TableRow v-for="n in 8" :key="n" class="odd:bg-muted/20">
              <TableCell class="px-3 py-2"><Skeleton class="h-4 w-32" /></TableCell>
              <TableCell class="px-3 py-2"><Skeleton class="h-4 w-48" /></TableCell>
              <TableCell v-if="isManual" class="px-3 py-2"><Skeleton class="h-5 w-20" /></TableCell>
              <TableCell class="px-3 py-2"><Skeleton class="h-5 w-16" /></TableCell>
              <TableCell class="px-3 py-2"><Skeleton class="h-4 w-10" /></TableCell>
              <TableCell class="px-3 py-2"><Skeleton class="h-4 w-32" /></TableCell>
            </TableRow>
          </template>
          <template v-else-if="error">
            <TableRow>
              <TableCell :colspan="isManual ? 6 : 5" class="h-24 text-center">
                <div class="flex flex-col items-center gap-2">
                  <span class="text-destructive text-sm">{{ error }}</span>
                  <Button variant="outline" size="sm" @click="load">Retry</Button>
                </div>
              </TableCell>
            </TableRow>
          </template>
          <template v-else-if="items.length">
            <TableRow
              v-for="task in items"
              :key="task.id"
              class="odd:bg-muted/20 hover:bg-muted/40 transition-colors"
            >
              <TableCell class="px-3 py-2 text-sm font-medium">
                <router-link
                  :to="{ name: 'Member History', params: { memberId: task.member.id } }"
                  class="hover:underline"
                >{{ task.member.name }}</router-link>
              </TableCell>
              <TableCell class="px-3 py-2 text-xs text-muted-foreground">{{ task.member.email }}</TableCell>
              <TableCell v-if="isManual" class="px-3 py-2">
                <Badge variant="secondary" class="text-xs">{{ emailTypeLabel(task.email_type) }}</Badge>
              </TableCell>
              <TableCell class="px-3 py-2">
                <Badge variant="outline" class="text-xs" :class="STATUS_CLASS[task.status]">
                  {{ task.status }}
                </Badge>
              </TableCell>
              <TableCell class="px-3 py-2 text-xs tabular-nums" :class="attemptsClass(task)">
                {{ task.attempts }} / {{ maxAttempts }}
              </TableCell>
              <TableCell class="px-3 py-2 text-xs text-muted-foreground">{{ formatSentAt(task.sent_at) }}</TableCell>
            </TableRow>
          </template>
          <template v-else>
            <TableRow>
              <TableCell :colspan="isManual ? 6 : 5" class="h-24 text-center text-sm text-muted-foreground">
                No tasks match these filters.
              </TableCell>
            </TableRow>
          </template>
        </TableBody>
      </Table>
    </div>

    <!-- Pagination footer -->
    <div class="flex items-center justify-between text-sm">
      <span class="text-muted-foreground">
        Page {{ page }} of {{ totalPages }} · {{ total }} total
      </span>
      <div class="flex items-center gap-2">
        <Button
          variant="outline" size="sm"
          :disabled="page <= 1 || loading"
          @click="prevPage"
        >Previous</Button>
        <Button
          variant="outline" size="sm"
          :disabled="!hasNext || loading"
          @click="nextPage"
        >Next</Button>
      </div>
    </div>
  </div>
</template>
