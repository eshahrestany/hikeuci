<script setup>
import { ref } from 'vue'
import { TriangleAlert, ArrowLeftRight, Ban, X } from 'lucide-vue-next'
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
import SwapVoteTrailModal from '@/components/admin/SwapVoteTrailModal.vue'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'

const props = defineProps({
  currentTrailId: { type: Number, default: null },
  phase: { type: String, required: true }, // 'voting' | 'signup' | 'waiver'
  candidates: { type: Array, default: () => [] },
})
const emit = defineEmits(['switched', 'swapped', 'cancelled'])

const drawerOpen = ref(false)
const showSwitchModal = ref(false)
const showSwapVoteModal = ref(false)
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
      <Button variant="destructive" size="sm">
        <TriangleAlert class="h-4 w-4" />
        Danger Zone
      </Button>
    </DrawerTrigger>

    <DrawerContent class="p-0 flex flex-col max-w-sm ml-auto">
      <!-- Header -->
      <DrawerHeader class="border-b px-5 py-4 bg-destructive/5">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-2.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-destructive/10 shrink-0">
              <TriangleAlert class="h-4 w-4 text-destructive" />
            </div>
            <div>
              <DrawerTitle class="text-base text-destructive">Danger Zone</DrawerTitle>
              <DrawerDescription class="text-xs mt-0.5">
                Actions here are difficult to reverse.
              </DrawerDescription>
            </div>
          </div>
        </div>
      </DrawerHeader>

      <!-- Actions -->
      <div class="flex-1 overflow-y-auto p-5 space-y-3">

        <!-- Swap Vote Trail (voting phase only) -->
        <div v-if="phase === 'voting'" class="rounded-xl border bg-card p-4 space-y-3">
          <div class="flex items-start gap-3">
            <div class="flex h-7 w-7 items-center justify-center rounded-full bg-muted shrink-0 mt-0.5">
              <ArrowLeftRight class="h-3.5 w-3.5 text-muted-foreground" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium leading-snug">Swap Vote Trail</p>
              <p class="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                Replace one of the voting candidate trails. Existing votes for the removed trail will be transferred to the new one.
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" class="w-full" @click="showSwapVoteModal = true">
            <ArrowLeftRight class="h-3.5 w-3.5" />
            Swap Trail
          </Button>
        </div>

        <!-- Switch Trail (signup/waiver only) -->
        <div v-if="phase !== 'voting'" class="rounded-xl border bg-card p-4 space-y-3">
          <div class="flex items-start gap-3">
            <div class="flex h-7 w-7 items-center justify-center rounded-full bg-muted shrink-0 mt-0.5">
              <ArrowLeftRight class="h-3.5 w-3.5 text-muted-foreground" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium leading-snug">Switch Trail</p>
              <p class="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                Replace the trail for this hike with a different trail from the catalog.
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" class="w-full" @click="showSwitchModal = true">
            <ArrowLeftRight class="h-3.5 w-3.5" />
            Switch Trail
          </Button>
        </div>

        <!-- Cancel Hike -->
        <div class="rounded-xl border border-destructive/30 bg-destructive/5 p-4 space-y-3">
          <div class="flex items-start gap-3">
            <div class="flex h-7 w-7 items-center justify-center rounded-full bg-destructive/10 shrink-0 mt-0.5">
              <Ban class="h-3.5 w-3.5 text-destructive" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium text-destructive leading-snug">Cancel Hike</p>
              <p class="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                Permanently cancel this hike. All magic links will be invalidated and the hike removed from the schedule.
              </p>
            </div>
          </div>
          <Button variant="destructive" size="sm" class="w-full" @click="showCancelConfirm = true">
            <Ban class="h-3.5 w-3.5" />
            Cancel Hike
          </Button>
        </div>

      </div>
    </DrawerContent>

    <!-- Modals render via portal into <body> -->
    <SwitchTrailModal
      v-if="showSwitchModal"
      :current-trail-id="currentTrailId"
      :phase="phase"
      @switched="(data) => { emit('switched', data); drawerOpen = false }"
      @close="showSwitchModal = false"
    />

    <SwapVoteTrailModal
      v-if="showSwapVoteModal"
      :candidates="candidates"
      @swapped="(data) => { emit('swapped', data); drawerOpen = false }"
      @close="showSwapVoteModal = false"
    />

    <!-- Cancel confirm dialog -->
    <Dialog v-model:open="showCancelConfirm">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <div class="flex items-center gap-3 mb-1">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-destructive/10 shrink-0">
              <Ban class="h-5 w-5 text-destructive" />
            </div>
            <DialogTitle class="text-lg">Cancel this hike?</DialogTitle>
          </div>
          <DialogDescription class="text-sm leading-relaxed">
            This will <strong class="text-foreground">permanently cancel</strong> the active hike.
            All outstanding voting, signup, and waiver links will be immediately invalidated.
            <span class="block mt-1.5 text-destructive font-medium">This action cannot be undone.</span>
          </DialogDescription>
        </DialogHeader>
        <DialogFooter class="gap-2 mt-2">
          <Button variant="outline" class="flex-1" @click="showCancelConfirm = false">
            Go Back
          </Button>
          <Button variant="destructive" class="flex-1" :disabled="cancelling" @click="confirmCancel">
            <Ban class="h-4 w-4" />
            {{ cancelling ? 'Cancelling…' : 'Yes, Cancel Hike' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </Drawer>
</template>
