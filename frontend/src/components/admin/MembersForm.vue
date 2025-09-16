<script setup>
import { reactive, watch, computed } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'
import {Checkbox} from "@/components/ui/checkbox/index.js";

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  memberData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:isOpen', 'submitted'])

const { getAuthHeaders, fetchWithAuth} = useAuth()

const defaultMemberState = {
  name: '',
  email: '',
  tel: '',
  is_officer: false,
}


const formData = reactive({ ...defaultMemberState })

watch(() => props.memberData, (newMember) => {
  if (newMember) {
    Object.assign(formData, newMember)
  } else {
    Object.assign(formData, defaultMemberState)
  }
}, { immediate: true })


const isEditing = computed(() => !!props.memberData)
const dialogTitle = computed(() => isEditing.value ? 'Edit Member' : 'Add new Member')
const submitButtonText = computed(() => isEditing.value ? 'Save Changes' : '+ Add Member')


const handleSubmit = async () => {
  try {
    const endpoint = isEditing.value ? `/admin/members/${props.memberData.id}` : '/admin/members'
    const method = isEditing.value ? 'PUT' : 'POST'

    const response = await fetchWithAuth(endpoint,{method: method, body: JSON.stringify(formData)})

    toast.success(`Member successfully ${isEditing.value ? 'updated' : 'created'}! 🎉`)
    emit('submitted')
    emit('update:isOpen', false)
    Object.assign(formData, defaultMemberState)
  } catch (error) {
    console.error("Failed to submit member form:", error)
    toast.error('Submission Failed', { description: error.message })
  }
}

const deleteMember = async () => {
    try {
        const endpoint = `/admin/members/${props.memberData.id}`
        const method = "DELETE"

        const response = await fetchWithAuth(endpoint, {method: method})
        toast.success(`Member successfully Deleted`)

        emit('submitted')
        emit('update:isOpen', false)
    } catch (error) {
        toast.error('Submission Failed', { description: error.message })
    }
}

const handleClose = (openState) => {
  emit('update:isOpen', openState)
}
</script>

<template>
  <Dialog :open="isOpen" @update:open="handleClose">
    <DialogContent class="sm:max-w-2xl grid-rows-[auto,1fr,auto]">
      <DialogHeader>
        <DialogTitle>{{ dialogTitle }}</DialogTitle>
        <DialogDescription>
          Fill out the details for the member below. Name and Email are the only required fields
        </DialogDescription>
      </DialogHeader>

      <form id="member-form" @submit.prevent="handleSubmit" class="py-4 overflow-y-auto pr-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="name">Member Name</Label>
            <Input id="name" v-model="formData.name" placeholder="evan" required />
          </div>

          <div class="space-y-2">
            <Label for="email">Member Email</Label>
            <Input id="email" type="email" v-model="formData.email" placeholder="evan@uci.edu" required />
          </div>

         <div class="space-y-2">
            <Label for="tel">Member Phone #</Label>
            <Input id="tel" type="tel" v-model="formData.tel" placeholder="123 867 5309" />
         </div>

          <div class="space-y-2">
            <Label for="is_officer">Is Officer</Label>
            <Checkbox id="is_officer" type="checkbox" v-model="formData.is_officer" />
          </div>

        </div>
      </form>

      <DialogFooter class="w-full flex justify-between items-center gap-4">
        <Button type="button" variant="outline" @click="handleClose(false)">Cancel</Button>
        <Button type="submit" variant="default" form="member-form">{{ submitButtonText }}</Button>
        <Button v-if="isEditing" type="button" variant="destructive" @click="deleteMember()">Delete</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>