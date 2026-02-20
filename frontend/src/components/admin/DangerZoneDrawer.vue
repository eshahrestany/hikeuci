<script setup>
import { ref } from 'vue'
import { TriangleAlert, ArrowLeftRight, Ban } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
  DrawerTrigger,
} from '@/components/ui/drawer'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import SwitchTrailModal from '@/components/admin/SwitchTrailModal.vue'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'

const props = defineProps({
  currentTrailId: { type: Number, required: true },
  phase: { type: String, required: true }, // 'signup' | 'waiver'
})
const emit = defineEmits(['switched', 'cancelled'])

const drawerOpen = ref(false)
const showSwitchModal = ref(false)
const showCancelConfirm = ref(false)
const cancelling = ref(false)

const { fetchWithAuth } = useAuth()

async function confirmCancel() {
  cancelling.value = true
  try {
    const res = await fetchWithAuth('/api/admin/hike/cancel', { method: 'POST' })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.error || 'Request failed')
    }
    toast.success('Hike cancelled')
    showCancelConfirm.value = false
    drawerOpen.value = false
    emit('cancelled')
  } catch (e) {
    toast.error(`Failed to cancel hike: ${e.message}`)
  } finally {
    cancelling.value = false
  }
}
</script>

<template>
  <Drawer v-model:open="drawerOpen" direction="right" :should-scale-background="false">
    <DrawerTrigger as-child>
      <Button variant="destructive">
        <TriangleAlert class="h-4 w-4" />
        Danger Zone
      </Button>
    </DrawerTrigger>

    <DrawerContent class="p-0 flex flex-col">
      <DrawerHeader class="border-b px-6 py-4">
        <DrawerTitle class="flex items-center gap-2 text-destructive">
          <TriangleAlert class="h-4 w-4" />
          Danger Zone
        </DrawerTitle>
        <DrawerDescription>
          These actions affect the active hike and are very hard to manually reverse from the database.
        </DrawerDescription>
      </DrawerHeader>

      <div class="flex flex-col gap-3 p-6">
        <!-- Switch Trail -->
        <div class="flex items-center justify-between gap-4 rounded-md border p-4">
          <div class="min-w-0">
            <p class="font-medium text-sm">Switch Trail</p>
            <p class="text-sm text-muted-foreground">Replace the trail for this hike.</p>
          </div>
          <Button variant="outline" size="sm" class="shrink-0" @click="showSwitchModal = true">
            <ArrowLeftRight class="h-4 w-4" />
            Switch Trail
          </Button>
        </div>

        <!-- Cancel Hike -->
        <div class="flex items-center justify-between gap-4 rounded-md border border-destructive/40 bg-destructive/5 p-4">
          <div class="min-w-0">
            <p class="font-medium text-sm text-destructive">Cancel Hike</p>
            <p class="text-sm text-muted-foreground">
              Permanently cancel this hike. All magic links will be invalidated immediately.
            </p>
          </div>
          <Button variant="destructive" size="sm" class="shrink-0" @click="showCancelConfirm = true">
            <Ban class="h-4 w-4" />
            Cancel Hike
          </Button>
        </div>
      </div>
    </DrawerContent>

    <!-- These use portals so they render into <body> regardless of placement here -->
    <SwitchTrailModal
      v-if="showSwitchModal"
      :current-trail-id="currentTrailId"
      :phase="phase"
      @switched="(data) => { emit('switched', data); drawerOpen = false }"
      @close="showSwitchModal = false"
    />

    <Dialog v-model:open="showCancelConfirm">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Cancel this hike?</DialogTitle>
          <DialogDescription>
            This will permanently cancel the hike. All outstanding voting, signup, and waiver links
            will be immediately invalidated. This cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" @click="showCancelConfirm = false">Go Back</Button>
          <Button variant="destructive" :disabled="cancelling" @click="confirmCancel">
            {{ cancelling ? 'Cancelling…' : 'Yes, Cancel Hike' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </Drawer>
</template>
