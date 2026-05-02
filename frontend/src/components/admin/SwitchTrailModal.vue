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
  currentTrailId: { type: Number, required: true },
  phase: { type: String, required: true },
})
const emit = defineEmits(['switched', 'close'])

const open = ref(true)
watch(open, v => { if (!v) emit('close') })

const step = ref(1)
const selectedTrail = ref(null)
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
    <DialogContent class="sm:max-w-[600px] max-h-[85vh] flex flex-col gap-0 p-0 overflow-hidden">

      <!-- Step 1: Select Trail -->
      <template v-if="step === 1">
        <div class="shrink-0 border-b px-6 py-4">
          <DialogHeader>
            <div class="flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-muted shrink-0">
                <ArrowLeftRight class="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <DialogTitle class="text-base">Switch Trail</DialogTitle>
                <DialogDescription class="text-xs mt-0.5">Select a new trail for this hike.</DialogDescription>
              </div>
            </div>
          </DialogHeader>
        </div>
        <div class="overflow-y-auto flex-1 min-h-0 p-6">
          <TrailPicker
            mode="single"
            :exclude-id="currentTrailId"
            v-model="selectedTrail"
          />
        </div>
        <div class="shrink-0 border-t bg-muted/20 flex justify-end gap-2 px-6 py-3">
          <Button variant="outline" size="sm" @click="open = false">Cancel</Button>
          <Button size="sm" :disabled="!selectedTrail" @click="step = 2">Next</Button>
        </div>
      </template>

      <!-- Step 2: Confirm -->
      <template v-else>
        <div class="shrink-0 border-b px-6 py-4">
          <DialogHeader>
            <div class="flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-destructive/10 shrink-0">
                <ArrowLeftRight class="h-4 w-4 text-destructive" />
              </div>
              <div>
                <DialogTitle class="text-base">Confirm Trail Switch</DialogTitle>
                <DialogDescription class="text-xs mt-0.5">
                  Replace the current trail with <strong class="text-foreground">{{ selectedTrail.name }}</strong>?
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>
        </div>
        <div class="overflow-y-auto flex-1 min-h-0 p-6">
          <div class="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-700 dark:text-amber-400 flex items-start gap-2.5">
            <TriangleAlert class="h-4 w-4 shrink-0 mt-0.5" />
            <span>
              <template v-if="phase === 'waiver'">
                Members with confirmed signups will <strong>not</strong> be automatically notified of this change.
                Any waivers already signed remain on file.
              </template>
              <template v-else>
                Signed-up members will <strong>not</strong> be automatically notified of this change.
              </template>
            </span>
          </div>
        </div>
        <div class="shrink-0 border-t bg-muted/20 flex justify-end gap-2 px-6 py-3">
          <Button variant="outline" size="sm" @click="step = 1">Back</Button>
          <Button variant="destructive" size="sm" :disabled="submitting" @click="confirm">
            <ArrowLeftRight class="h-3.5 w-3.5" />
            {{ submitting ? 'Switching…' : 'Switch Trail' }}
          </Button>
        </div>
      </template>

    </DialogContent>
  </Dialog>
</template>
