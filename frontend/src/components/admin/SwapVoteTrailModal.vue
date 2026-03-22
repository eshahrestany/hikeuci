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
import { Label } from '@/components/ui/label'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'
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
        <div class="overflow-y-auto flex-1 min-h-0 flex flex-col gap-4 p-6">
          <DialogHeader>
            <DialogTitle>Swap Vote Trail</DialogTitle>
            <DialogDescription>Select which candidate trail to replace.</DialogDescription>
          </DialogHeader>
          <div class="flex flex-col gap-2">
            <button
              v-for="c in candidates"
              :key="c.trail_id"
              class="flex items-center justify-between rounded-md border p-3 text-left text-sm transition-colors"
              :class="selectedOldTrailId === c.trail_id
                ? 'border-primary bg-primary/5'
                : 'hover:bg-muted/50'"
              @click="selectOld(c.trail_id)"
            >
              <span class="font-medium">{{ c.trail_name }}</span>
              <span class="text-muted-foreground text-xs">{{ c.trail_num_votes }} vote(s)</span>
            </button>
          </div>
        </div>
        <div class="shrink-0 border-t flex justify-end gap-2 px-6 py-4">
          <Button variant="outline" @click="open = false">Cancel</Button>
          <Button :disabled="!selectedOldTrailId" @click="step = 2">Next</Button>
        </div>
      </template>

      <!-- Step 2: Pick the replacement trail -->
      <template v-else-if="step === 2">
        <div class="overflow-y-auto flex-1 min-h-0 flex flex-col gap-4 p-6">
          <DialogHeader>
            <DialogTitle>Select Replacement Trail</DialogTitle>
            <DialogDescription>
              Choose a trail to replace <strong>{{ selectedOldTrail?.trail_name }}</strong>.
            </DialogDescription>
          </DialogHeader>
          <Label>Trail</Label>
          <TrailPicker
            mode="single"
            :exclude-ids="excludeIds"
            v-model="selectedNewTrail"
          />
        </div>
        <div class="shrink-0 border-t flex justify-end gap-2 px-6 py-4">
          <Button variant="outline" @click="step = 1; selectedNewTrail = null">Back</Button>
          <Button :disabled="!selectedNewTrail" @click="step = 3">Next</Button>
        </div>
      </template>

      <!-- Step 3: Confirm -->
      <template v-else>
        <div class="overflow-y-auto flex-1 min-h-0 flex flex-col gap-4 p-6">
          <DialogHeader>
            <DialogTitle>Confirm Trail Swap</DialogTitle>
            <DialogDescription>
              Replace <strong>{{ selectedOldTrail?.trail_name }}</strong> with <strong>{{ selectedNewTrail?.name }}</strong>?
            </DialogDescription>
          </DialogHeader>
          <div class="rounded-md border border-yellow-500/50 bg-yellow-50 dark:bg-yellow-950/30 px-4 py-3 text-sm text-yellow-800 dark:text-yellow-200">
            All existing votes for <strong>{{ selectedOldTrail?.trail_name }}</strong>
            ({{ selectedOldTrail?.trail_num_votes }}) will be transferred to
            <strong>{{ selectedNewTrail?.name }}</strong>.
            Members will <strong>not</strong> be notified of this change.
          </div>
        </div>
        <div class="shrink-0 border-t flex justify-end gap-2 px-6 py-4">
          <Button variant="outline" @click="step = 2">Back</Button>
          <Button variant="destructive" :disabled="submitting" @click="confirm">
            {{ submitting ? 'Swapping…' : 'Swap Trail' }}
          </Button>
        </div>
      </template>

    </DialogContent>
  </Dialog>
</template>
