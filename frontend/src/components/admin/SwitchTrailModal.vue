<script setup>
import { ref, watch, onMounted } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'

const props = defineProps({
  currentTrailId: { type: Number, required: true },
  phase: { type: String, required: true }, // 'signup' | 'waiver'
})
const emit = defineEmits(['switched', 'close'])

const open = ref(true)
watch(open, v => { if (!v) emit('close') })

const step = ref(1)
const trails = ref([])
const selectedTrail = ref(null)
const loading = ref(false)
const submitting = ref(false)

const { fetchWithAuth } = useAuth()

async function loadTrails() {
  loading.value = true
  try {
    const res = await fetchWithAuth('/api/admin/trails')
    if (!res.ok) throw new Error()
    trails.value = (await res.json()).filter(t => t.id !== props.currentTrailId)
  } catch {
    toast.error('Could not load trails')
  } finally {
    loading.value = false
  }
}

onMounted(loadTrails)

function difficultyVariant(d) {
  if (d === 'easy') return 'secondary'
  if (d === 'hard') return 'destructive'
  return 'default'
}

async function confirm() {
  if (!selectedTrail.value) return
  submitting.value = true
  try {
    const res = await fetchWithAuth('/api/admin/hike/trail', {
      method: 'PUT',
      body: JSON.stringify({ trail_id: selectedTrail.value.id }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.error || 'Request failed')
    }
    const data = await res.json()
    toast.success('Trail switched successfully')
    emit('switched', data)
    open.value = false
  } catch (e) {
    toast.error(`Failed to switch trail: ${e.message}`)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-[500px]">

      <!-- Step 1: Select Trail -->
      <template v-if="step === 1">
        <DialogHeader>
          <DialogTitle>Switch Trail</DialogTitle>
          <DialogDescription>Select a new trail for this hike.</DialogDescription>
        </DialogHeader>

        <div v-if="loading" class="py-6 text-center text-sm text-muted-foreground">
          Loading trails…
        </div>
        <div v-else-if="trails.length === 0" class="py-6 text-center text-sm text-muted-foreground">
          No other trails available.
        </div>
        <div v-else class="overflow-y-auto max-h-72 flex flex-col gap-2 pr-1">
          <button
            v-for="trail in trails"
            :key="trail.id"
            type="button"
            class="w-full text-left rounded-md border px-4 py-3 transition-colors hover:bg-accent"
            :class="selectedTrail?.id === trail.id ? 'border-primary bg-accent' : 'border-border'"
            @click="selectedTrail = trail"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium">{{ trail.name }}</span>
              <Badge :variant="difficultyVariant(trail.difficulty)">{{ trail.difficulty }}</Badge>
            </div>
            <div class="text-sm text-muted-foreground mt-0.5">{{ trail.location }}</div>
          </button>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="open = false">Cancel</Button>
          <Button :disabled="!selectedTrail || loading" @click="step = 2">Next</Button>
        </DialogFooter>
      </template>

      <!-- Step 2: Confirm -->
      <template v-else>
        <DialogHeader>
          <DialogTitle>Confirm Trail Switch</DialogTitle>
          <DialogDescription>
            Replace the current trail with <strong>{{ selectedTrail.name }}</strong>?
          </DialogDescription>
        </DialogHeader>

        <div class="rounded-md border border-yellow-500/50 bg-yellow-50 dark:bg-yellow-950/30 px-4 py-3 text-sm text-yellow-800 dark:text-yellow-200">
          <template v-if="phase === 'waiver'">
            Members with confirmed signups will <strong>not</strong> be automatically notified of this change.
            Any waivers already signed remain on file.
          </template>
          <template v-else>
            Signed-up members will <strong>not</strong> be automatically notified of this change.
          </template>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="step = 1">Back</Button>
          <Button variant="destructive" :disabled="submitting" @click="confirm">
            {{ submitting ? 'Switching…' : 'Switch Trail' }}
          </Button>
        </DialogFooter>
      </template>

    </DialogContent>
  </Dialog>
</template>
