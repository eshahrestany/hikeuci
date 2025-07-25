<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Edit Signup</DialogTitle>
      </DialogHeader>

      <div class="grid gap-4 py-4">
        <div class="grid grid-cols-2 items-center gap-4">
          <Label for="firstName">First Name</Label>
          <Input id="firstName" v-model="form.first_name" />
        </div>
        <div class="grid grid-cols-2 items-center gap-4">
          <Label for="lastName">Last Name</Label>
          <Input id="lastName" v-model="form.last_name" />
        </div>
        <div class="grid grid-cols-2 items-center gap-4">
          <Label for="transportType">Transport Type</Label>
          <Select v-model="form.transport_type">
            <SelectTrigger id="transportType">
              <SelectValue placeholder="Select…" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="driver">Driver</SelectItem>
              <SelectItem value="passenger">Passenger</SelectItem>
              <SelectItem value="self">Self-transport</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="open = false">Cancel</Button>
        <Button @click="onSave">Save</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from '@/components/ui/select'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'

const props = defineProps({
  user:   { type: Object, required: true },
  hikeId: { type: Number, required: true }
})
const emit = defineEmits(['saved','close'])
const open = ref(true)
watch(open, v => { if (!v) emit('close') })

// initialize form from props.user.transport_type
const form = reactive({
  first_name:     props.user.first_name,
  last_name:      props.user.last_name,
  transport_type: props.user.transport_type
})

const { postWithAuth } = useAuth()

async function onSave() {
  try {
    const res = await postWithAuth('/active-hike/modify-user', {
      hike_id:        props.hikeId,
      user_id:        props.user.member_id,
      first_name:     form.first_name,
      last_name:      form.last_name,
      transport_type: form.transport_type
    })
    if (!res.ok) {
      const err = await res.text()
      throw new Error(err || 'Unknown error')
    }

    // apply changes locally
    props.user.first_name     = form.first_name
    props.user.last_name      = form.last_name
    props.user.transport_type = form.transport_type

    toast.success('Signup updated')
    emit('saved', props.user)
    open.value = false
  } catch {
    toast.error('Update failed')
  }
}
</script>
