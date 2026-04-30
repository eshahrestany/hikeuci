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
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'
import {PlusCircle, Save, MailCheck, MailX} from "lucide-vue-next"

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

const {fetchWithAuth} = useAuth()

const defaultMemberState = {
  name: '',
  email: '',
  tel: '',
}


const formData = reactive({ ...defaultMemberState })
const localMeta = ref({ subscribed_to_mailing_list: true, can_delete: true })

watch(() => props.memberData, (newMember) => {
  if (newMember) {
    Object.assign(formData, newMember)
    localMeta.value = {
      subscribed_to_mailing_list: newMember.subscribed_to_mailing_list,
      can_delete: newMember.can_delete,
    }
  } else {
    Object.assign(formData, defaultMemberState)
  }
}, { immediate: true })


const isEditing = computed(() => !!props.memberData)
const dialogTitle = computed(() => isEditing.value ? 'Edit Member' : 'Add new Member')
const submitButtonText = computed(() => isEditing.value ? 'Save Changes' : 'Add Member')


const handleSubmit = async () => {
  try {
    const endpoint = isEditing.value ? `/api/admin/members/${props.memberData.id}` : '/api/admin/members'
    const method = isEditing.value ? 'PUT' : 'POST'

    const response = await fetchWithAuth(endpoint,{method: method, body: JSON.stringify(formData)})
    if (!response.ok) {
      throw Error(response.status)
    }

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
        const endpoint = `/api/admin/members/${props.memberData.id}`
        const method = "DELETE"

        const response = await fetchWithAuth(endpoint, {method: method})
        if (!response.ok) {
          throw new Error(response.status)
        }
        toast.success(`Member successfully Deleted`)

        emit('submitted')
        emit('update:isOpen', false)
    } catch (error) {
        toast.error('Submission Failed', { description: error.message })
    }
}

const toggleMailingList = async () => {
  try {
    const subscribed = !localMeta.value.subscribed_to_mailing_list
    const response = await fetchWithAuth(`/api/admin/members/${props.memberData.id}/mailing-list`, {
      method: 'PATCH',
      body: JSON.stringify({ subscribed }),
    })
    if (!response.ok) throw new Error(response.status)
    const updated = await response.json()
    localMeta.value = {
      subscribed_to_mailing_list: updated.subscribed_to_mailing_list,
      can_delete: updated.can_delete,
    }
    toast.success(subscribed ? 'Added to mailing list' : 'Removed from mailing list')
    emit('submitted')
  } catch (error) {
    toast.error('Failed to update mailing list', { description: error.message })
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

        </div>
      </form>

      <DialogFooter class="w-full flex justify-between items-center gap-4">
        <Button class="items-center text-center" type="submit" variant="default" form="member-form">
          {{ submitButtonText }}
          <Save v-if="isEditing"/>
          <PlusCircle v-else/>
        </Button>
        <Button type="button" variant="outline" @click="handleClose(false)">Cancel</Button>
        <Button
          v-if="isEditing"
          type="button"
          :variant="localMeta.subscribed_to_mailing_list ? 'outline' : 'secondary'"
          @click="toggleMailingList()"
        >
          <MailX v-if="localMeta.subscribed_to_mailing_list" class="h-3.5 w-3.5 mr-1" />
          <MailCheck v-else class="h-3.5 w-3.5 mr-1" />
          {{ localMeta.subscribed_to_mailing_list ? 'Remove from Mailing List' : 'Add to Mailing List' }}
        </Button>
        <Button
          v-if="isEditing"
          type="button"
          variant="destructive"
          :disabled="!localMeta.can_delete"
          :title="!localMeta.can_delete ? 'Cannot delete: member has existing records (signups, waivers, etc.)' : ''"
          @click="deleteMember()"
        >Delete</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>