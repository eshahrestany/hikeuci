<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table/index.js"
import { Button } from "@/components/ui/button/index.js"
import { Badge } from "@/components/ui/badge"
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import {
  Tooltip, TooltipContent, TooltipProvider, TooltipTrigger,
} from "@/components/ui/tooltip"
import { PlusCircle, Trash2, Crown } from "lucide-vue-next"
import { toast } from "vue-sonner"
import { useAuth } from "@/lib/auth.js"
import MemberPicker from "@/components/admin/MemberPicker.vue"

const { state, setUser, fetchWithAuth, postWithAuth } = useAuth()
const router = useRouter()

const officers = ref([])
const loading = ref(true)

const addOpen = ref(false)
const candidateMembers = ref([])
const pickedMember = ref(null)
const candidatesLoading = ref(false)
const submitting = ref(false)

const deleteOpen = ref(false)
const deleteTarget = ref(null)

const transferOpen = ref(false)
const transferTarget = ref(null)

async function load() {
  loading.value = true
  try {
    const res = await fetchWithAuth("/api/admin/officers")
    if (!res.ok) throw new Error("Failed to load officers")
    officers.value = await res.json()
  } catch (e) {
    toast.error("Could not load officers")
    officers.value = []
  } finally {
    loading.value = false
  }
}

async function loadCandidates() {
  candidatesLoading.value = true
  try {
    const res = await fetchWithAuth("/api/admin/officers/candidate-members")
    candidateMembers.value = res.ok ? await res.json() : []
  } finally {
    candidatesLoading.value = false
  }
}

async function openAdd() {
  pickedMember.value = null
  addOpen.value = true
  await loadCandidates()
}

async function submitAdd() {
  if (!pickedMember.value) {
    toast.error("Select a member first")
    return
  }
  submitting.value = true
  try {
    const res = await postWithAuth("/api/admin/officers", {
      member_id: pickedMember.value.member_id,
    })
    const body = await res.json().catch(() => ({}))
    if (!res.ok) {
      toast.error(body.error || "Failed to add officer")
      return
    }
    toast.success(`Added ${body.name || body.email}`)
    addOpen.value = false
    await load()
  } finally {
    submitting.value = false
  }
}

function askDelete(officer) {
  deleteTarget.value = officer
  deleteOpen.value = true
}

async function confirmDelete() {
  const target = deleteTarget.value
  if (!target) return
  submitting.value = true
  try {
    const res = await fetchWithAuth(`/api/admin/officers/${target.id}`, { method: "DELETE" })
    const body = await res.json().catch(() => ({}))
    if (!res.ok) {
      toast.error(body.error || "Failed to remove officer")
      return
    }
    toast.success(`Removed ${target.name || target.email}`)
    deleteOpen.value = false
    deleteTarget.value = null
    await load()
  } finally {
    submitting.value = false
  }
}

function askTransfer(officer) {
  transferTarget.value = officer
  transferOpen.value = true
}

async function confirmTransfer() {
  const target = transferTarget.value
  if (!target) return
  submitting.value = true
  try {
    const res = await postWithAuth(`/api/admin/officers/${target.id}/transfer`, {})
    const body = await res.json().catch(() => ({}))
    if (!res.ok) {
      toast.error(body.error || "Transfer failed")
      return
    }
    toast.success(`Ownership transferred to ${target.name || target.email}`)
    if (state.user) setUser({ ...state.user, is_owner: false })
    transferOpen.value = false
    transferTarget.value = null
    router.replace({ name: "Dashboard" })
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<template>
  <!-- Toolbar -->
  <div class="flex flex-wrap items-center gap-2 pb-3">
    <Button size="sm" variant="outline" @click="openAdd"><PlusCircle class="h-4 w-4"/>Add Officer</Button>
    <span v-if="!loading" class="ml-auto text-xs text-muted-foreground">
      {{ officers.length }} officer{{ officers.length === 1 ? '' : 's' }}
    </span>
  </div>

  <!-- Table -->
  <div class="rounded-lg border overflow-hidden">
    <Table>
      <TableHeader class="bg-muted/50">
        <TableRow class="border-b">
          <TableHead class="px-3 py-2 text-xs font-semibold">Name</TableHead>
          <TableHead class="px-3 py-2 text-xs font-semibold">Email</TableHead>
          <TableHead class="px-3 py-2 text-xs font-semibold">Role</TableHead>
          <TableHead class="px-3 py-2 text-xs font-semibold">Added</TableHead>
          <TableHead class="px-3 py-2 text-xs font-semibold text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <template v-if="officers.length">
          <TableRow
            v-for="o in officers"
            :key="o.id"
            class="odd:bg-muted/20 hover:bg-muted/40 transition-colors"
          >
            <TableCell class="px-3 py-2.5 text-sm font-medium">
              {{ o.name || '—' }}
              <Badge v-if="!o.has_logged_in" variant="secondary" class="ml-2 text-xs">Pending sign-in</Badge>
            </TableCell>
            <TableCell class="px-3 py-2.5 text-sm text-muted-foreground">{{ o.email }}</TableCell>
            <TableCell class="px-3 py-2.5">
              <Badge v-if="o.is_owner" class="bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30 border text-xs">Owner</Badge>
              <Badge v-else variant="secondary" class="text-xs">Officer</Badge>
            </TableCell>
            <TableCell class="px-3 py-2.5 text-xs text-muted-foreground">{{ new Date(o.created_on).toLocaleDateString() }}</TableCell>
            <TableCell class="px-3 py-2.5 text-right">
              <div class="flex justify-end gap-2">
                <TooltipProvider v-if="!o.is_owner">
                  <Tooltip :disabled="o.has_logged_in">
                    <TooltipTrigger as-child>
                      <span>
                        <Button variant="outline" size="sm" :disabled="!o.has_logged_in" @click="askTransfer(o)">
                          <Crown class="h-3.5 w-3.5 mr-1"/>Transfer Ownership
                        </Button>
                      </span>
                    </TooltipTrigger>
                    <TooltipContent v-if="!o.has_logged_in">
                      Officer must sign in at least once before ownership can be transferred.
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <Button v-if="!o.is_owner" variant="outline" size="sm" @click="askDelete(o)">
                  <Trash2 class="h-3.5 w-3.5 mr-1"/>Remove
                </Button>
              </div>
            </TableCell>
          </TableRow>
        </template>
        <TableRow v-else>
          <TableCell colspan="5" class="h-24 text-center text-sm text-muted-foreground">
            {{ loading ? 'Loading…' : 'No officers.' }}
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>

  <!-- Add Officer -->
  <Dialog v-model:open="addOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Add Officer</DialogTitle>
        <DialogDescription>
          Pick an existing member by name or email. Officers must already exist as members.
        </DialogDescription>
      </DialogHeader>
      <form @submit.prevent="submitAdd" class="space-y-4">
        <MemberPicker
          v-model="pickedMember"
          :options="candidateMembers"
          :empty-message="candidatesLoading ? 'Loading…' : 'No eligible members.'"
        />
        <DialogFooter>
          <Button type="button" variant="ghost" @click="addOpen = false" :disabled="submitting">Cancel</Button>
          <Button type="submit" :disabled="submitting || !pickedMember">Add</Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>

  <!-- Remove Officer -->
  <Dialog v-model:open="deleteOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Remove officer?</DialogTitle>
        <DialogDescription>
          <span v-if="deleteTarget">
            <strong>{{ deleteTarget.name || deleteTarget.email }}</strong> will lose admin access. This can be undone by adding them again.
          </span>
        </DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="ghost" @click="deleteOpen = false" :disabled="submitting">Cancel</Button>
        <Button variant="destructive" @click="confirmDelete" :disabled="submitting">Remove</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <!-- Transfer Ownership -->
  <Dialog v-model:open="transferOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Transfer ownership?</DialogTitle>
        <DialogDescription>
          <span v-if="transferTarget">
            <strong>{{ transferTarget.name || transferTarget.email }}</strong> will become the new owner. You will lose access to this page and will no longer be able to manage officers. <strong>This cannot be undone</strong> — only the new owner can transfer ownership back.
          </span>
        </DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="ghost" @click="transferOpen = false" :disabled="submitting">Cancel</Button>
        <Button variant="destructive" @click="confirmTransfer" :disabled="submitting">Transfer Ownership</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
