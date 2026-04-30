<script setup>
import { ref, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'
import { ArrowLeftRight, TriangleAlert } from 'lucide-vue-next'
import TrailPicker from '@/components/admin/TrailPicker.vue'

const props = defineProps({
  candidates: { type: Array, required: true }, // array of { trail_id, trail_name, trail_num_votes }
})
const emit = defineEmits(['swapped', 'close'])

const open = ref(true)
watch(open, v => { if (!v) emit('close') })

const step = ref(1)
const selectedOldTrailId = ref(null)
const selectedNewTrail = ref(null)
const submitting = ref(false)

const { fetchWithAuth } = useAuth()

const excludeIds = props.candidates.map(c => c.trail_id)
const selectedOldTrail = ref(null)

function selectOld(id) {
  selectedOldTrailId.value = id
  selectedOldTrail.value = props.candidates.find(c => c.trail_id === id)
}

async function confirm() {
  if (!selectedOldTrailId.value || !selectedNewTrail.value) return
  submitting.value = true
  try {
    const res = await fetchWithAuth('/api/admin/hike/vote-trail', {
      method: 'PUT',
      body: JSON.stringify({
        old_trail_id: selectedOldTrailId.value,
        new_trail_id: selectedNewTrail.value.id,
      }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.error || 'Request failed')
    }
    const data = await res.json()
    toast.success(`Swapped trail — ${data.votes_migrated} vote(s) migrated`)
    emit('swapped', data)
    open.value = false
  } catch (e) {
    toast.error(`Failed to swap trail: ${e.message}`)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-[600px] max-h-[85vh] flex flex-col gap-0 p-0 overflow-hidden">

      <!-- Step 1: Pick which candidate to replace -->
      <template v-if="step === 1">
        <div class="shrink-0 border-b px-6 py-4">
          <DialogHeader>
            <div class="flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-muted shrink-0">
                <ArrowLeftRight class="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <DialogTitle class="text-base">Swap Vote Trail</DialogTitle>
                <DialogDescription class="text-xs mt-0.5">Select which candidate trail to replace.</DialogDescription>
              </div>
            </div>
          </DialogHeader>
        </div>
        <div class="overflow-y-auto flex-1 min-h-0 p-6">
          <div class="flex flex-col gap-2">
            <button
              v-for="c in candidates"
              :key="c.trail_id"
              class="flex items-center justify-between rounded-lg border px-4 py-3 text-left text-sm transition-colors"
              :class="selectedOldTrailId === c.trail_id
                ? 'border-primary bg-primary/5 text-foreground'
                : 'border-border hover:bg-muted/50 text-foreground'"
              @click="selectOld(c.trail_id)"
            >
              <span class="font-medium">{{ c.trail_name }}</span>
              <span class="text-muted-foreground text-xs tabular-nums">{{ c.trail_num_votes }} vote(s)</span>
            </button>
          </div>
        </div>
        <div class="shrink-0 border-t bg-muted/20 flex justify-end gap-2 px-6 py-3">
          <Button variant="outline" size="sm" @click="open = false">Cancel</Button>
          <Button size="sm" :disabled="!selectedOldTrailId" @click="step = 2">Next</Button>
        </div>
      </template>

      <!-- Step 2: Pick the replacement trail -->
      <template v-else-if="step === 2">
        <div class="shrink-0 border-b px-6 py-4">
          <DialogHeader>
            <div class="flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-muted shrink-0">
                <ArrowLeftRight class="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <DialogTitle class="text-base">Select Replacement Trail</DialogTitle>
                <DialogDescription class="text-xs mt-0.5">
                  Choose a trail to replace <strong class="text-foreground">{{ selectedOldTrail?.trail_name }}</strong>.
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>
        </div>
        <div class="overflow-y-auto flex-1 min-h-0 p-6">
          <TrailPicker
            mode="single"
            :exclude-ids="excludeIds"
            v-model="selectedNewTrail"
          />
        </div>
        <div class="shrink-0 border-t bg-muted/20 flex justify-end gap-2 px-6 py-3">
          <Button variant="outline" size="sm" @click="step = 1; selectedNewTrail = null">Back</Button>
          <Button size="sm" :disabled="!selectedNewTrail" @click="step = 3">Next</Button>
        </div>
      </template>

      <!-- Step 3: Confirm -->
      <template v-else>
        <div class="shrink-0 border-b px-6 py-4">
          <DialogHeader>
            <div class="flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-destructive/10 shrink-0">
                <ArrowLeftRight class="h-4 w-4 text-destructive" />
              </div>
              <div>
                <DialogTitle class="text-base">Confirm Trail Swap</DialogTitle>
                <DialogDescription class="text-xs mt-0.5">
                  Replace <strong class="text-foreground">{{ selectedOldTrail?.trail_name }}</strong> with
                  <strong class="text-foreground">{{ selectedNewTrail?.name }}</strong>?
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>
        </div>
        <div class="overflow-y-auto flex-1 min-h-0 p-6">
          <div class="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-700 dark:text-amber-400 flex items-start gap-2.5">
            <TriangleAlert class="h-4 w-4 shrink-0 mt-0.5" />
            <span>
              All existing votes for <strong>{{ selectedOldTrail?.trail_name }}</strong>
              ({{ selectedOldTrail?.trail_num_votes }}) will be transferred to
              <strong>{{ selectedNewTrail?.name }}</strong>.
              Members will <strong>not</strong> be notified of this change.
            </span>
          </div>
        </div>
        <div class="shrink-0 border-t bg-muted/20 flex justify-end gap-2 px-6 py-3">
          <Button variant="outline" size="sm" @click="step = 2">Back</Button>
          <Button variant="destructive" size="sm" :disabled="submitting" @click="confirm">
            <ArrowLeftRight class="h-3.5 w-3.5" />
            {{ submitting ? 'Swapping…' : 'Swap Trail' }}
          </Button>
        </div>
      </template>

    </DialogContent>
  </Dialog>
</template>
