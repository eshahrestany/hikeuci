<script setup>
import { reactive, ref, watch, computed } from 'vue'
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
import { Switch } from '@/components/ui/switch'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'
import { PlusCircle, Save } from 'lucide-vue-next'

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

const { fetchWithAuth } = useAuth()

const defaultFormState = () => ({
  name: '',
  email: '',
  tel: '',
  subscribed_to_mailing_list: true,
})

const formData = reactive(defaultFormState())
const original = ref(defaultFormState())
const canDelete = ref(true)

watch(() => props.memberData, (newMember) => {
  if (newMember) {
    Object.assign(formData, {
      name: newMember.name,
      email: newMember.email,
      tel: newMember.tel,
      subscribed_to_mailing_list: newMember.subscribed_to_mailing_list,
    })
    original.value = { ...formData }
    canDelete.value = newMember.can_delete
  } else {
    Object.assign(formData, defaultFormState())
    original.value = defaultFormState()
  }
}, { immediate: true })

const isEditing = computed(() => !!props.memberData)
const dialogTitle = computed(() => isEditing.value ? 'Edit Member' : 'Add new Member')
const submitButtonText = computed(() => isEditing.value ? 'Save Changes' : 'Add Member')

const isDirty = computed(() => {
  if (!isEditing.value) return true
  return (
    formData.name !== original.value.name ||
    formData.email !== original.value.email ||
    formData.tel !== original.value.tel ||
    formData.subscribed_to_mailing_list !== original.value.subscribed_to_mailing_list
  )
})

const handleSubmit = async () => {
  try {
    const endpoint = isEditing.value ? `/api/admin/members/${props.memberData.id}` : '/api/admin/members'
    const method = isEditing.value ? 'PUT' : 'POST'

    const response = await fetchWithAuth(endpoint, { method, body: JSON.stringify(formData) })
    if (!response.ok) {
      throw Error(response.status)
    }

    toast.success(`Member successfully ${isEditing.value ? 'updated' : 'created'}!`)
    emit('submitted')
    emit('update:isOpen', false)
    Object.assign(formData, defaultFormState())
  } catch (error) {
    console.error('Failed to submit member form:', error)
    toast.error('Submission Failed', { description: error.message })
  }
}

const deleteMember = async () => {
  try {
    const response = await fetchWithAuth(`/api/admin/members/${props.memberData.id}`, { method: 'DELETE' })
    if (!response.ok) {
      throw new Error(response.status)
    }
    toast.success('Member successfully deleted')
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
          Fill out the details for the member below. Name and Email are the only required fields, phone number will be assigned once the user enters their phone while filling out a signup form.
        </DialogDescription>
      </DialogHeader>

      <form id="member-form" @submit.prevent="handleSubmit" class="py-4 overflow-y-auto pr-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="name">Member Name</Label>
            <Input id="name" v-model="formData.name" placeholder="Peter Anteater" required />
          </div>

          <div class="space-y-2">
            <Label for="email">Member Email</Label>
            <Input id="email" type="email" v-model="formData.email" placeholder="peteranteater@uci.edu" required />
          </div>

          <div class="space-y-2">
            <Label for="tel">Member Phone #</Label>
            <Input id="tel" type="tel" v-model="formData.tel" placeholder="123 867 5309" />
          </div>

          <div class="flex items-center gap-3 pt-1">
            <Switch
              id="mailing-list"
              v-model="formData.subscribed_to_mailing_list"
            />
            <Label for="mailing-list" class="cursor-pointer">Mailing list</Label>
          </div>
        </div>
      </form>

      <DialogFooter class="w-full flex justify-between items-center gap-4">
        <Button
          class="items-center text-center"
          type="submit"
          variant="default"
          form="member-form"
          :disabled="!isDirty"
        >
          {{ submitButtonText }}
          <Save v-if="isEditing" />
          <PlusCircle v-else />
        </Button>
        <Button type="button" variant="outline" @click="handleClose(false)">Cancel</Button>
        <Button
          v-if="isEditing"
          type="button"
          variant="destructive"
          :disabled="!canDelete"
          :title="!canDelete ? 'Cannot delete: member has existing records (signups, waivers, etc.)' : ''"
          @click="deleteMember()"
        >Delete</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
