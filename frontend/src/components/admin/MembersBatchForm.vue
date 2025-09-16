<script setup>
import { ref, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:isOpen', 'submitted'])

const { fetchWithAuth } = useAuth()

const pastedData = ref('')
const errorMessage = ref(null)

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    pastedData.value = ''
    errorMessage.value = null
  }
})

const handleSubmit = async () => {
  errorMessage.value = null;
  const membersPayload = [];

  const lines = pastedData.value.trim().split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    const parts = line.split(/[\t,]/).map(p => p.trim());

    const name = parts[0] || '';
    const email = parts[1] || '';

    if (!name || !email) {
      const errorMsg = `Error on row ${i + 1}: Each row must contain both a name and an email.`;
      toast.error('Invalid Data', { description: errorMsg });
      errorMessage.value = errorMsg;
      return;
    }

    membersPayload.push({ name, email });
  }

  if (membersPayload.length === 0) {
    const errorMsg = 'No data to process. Please paste some information.';
    toast.warning('Empty Submission', { description: errorMsg });
    errorMessage.value = errorMsg;
    return;
  }

  try {
    const endpoint = '/admin/members/batch'
    await fetchWithAuth(endpoint, {
      method: 'POST',
      body: JSON.stringify(membersPayload)
    });

    toast.success(`${membersPayload.length} members successfully added! 🎉`);
    emit('submitted');
    emit('update:isOpen', false);

  } catch (error) {
    console.error("Failed to submit batch form:", error);
    toast.error('Batch Submission Failed', { description: error.message });
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
        <DialogTitle>Batch Add Members</DialogTitle>
        <DialogDescription>
          Paste data from a spreadsheet. Each member should be on a new line,
          with Name and Email separated by a comma or tab.
        </DialogDescription>
      </DialogHeader>

      <form id="member-batch-form" @submit.prevent="handleSubmit" class="py-4 overflow-y-auto pr-6">
        <div class="space-y-2">
          <Label for="batch-data">Pasted Member Data</Label>
          <textarea
            id="batch-data"
            v-model="pastedData"
            rows="10"
            placeholder="Alice Wonderland  alice@example.com&#10;Bob Builder,bob@example.com"
            class="font-mono"
          />
          <p v-if="errorMessage" class="text-sm text-red-500 mt-1">
            {{ errorMessage }}
          </p>
        </div>
      </form>

      <DialogFooter class="w-full flex justify-between items-center gap-4">
        <Button type="button" variant="outline" @click="handleClose(false)">Cancel</Button>
        <Button type="submit" variant="default" form="member-batch-form">+ Add Members</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>