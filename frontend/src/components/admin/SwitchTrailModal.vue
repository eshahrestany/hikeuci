<script setup>
import { ref, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'
import TrailPicker from '@/components/admin/TrailPicker.vue'

const props = defineProps({
  currentTrailId: { type: Number, required: true },
  phase: { type: String, required: true }, // 'signup' | 'waiver'
})
const emit = defineEmits(['switched', 'close'])

const open = ref(true)
watch(open, v => { if (!v) emit('close') })

const step = ref(1)
const selectedTrail = ref(null) // full trail object from TrailPicker
const submitting = ref(false)

const { fetchWithAuth } = useAuth()

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
    <DialogContent class="sm:max-w-[600px]">

      <!-- Step 1: Select Trail -->
      <template v-if="step === 1">
        <DialogHeader>
          <DialogTitle>Switch Trail</DialogTitle>
          <DialogDescription>Select a new trail for this hike.</DialogDescription>
        </DialogHeader>

        <Label>Trail</Label>
        <TrailPicker
          mode="single"
          :exclude-id="currentTrailId"
          v-model="selectedTrail"
        />

        <DialogFooter>
          <Button variant="outline" @click="open = false">Cancel</Button>
          <Button :disabled="!selectedTrail" @click="step = 2">Next</Button>
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
