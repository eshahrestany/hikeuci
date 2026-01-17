<script setup>
import { reactive, watch, computed, ref } from 'vue'
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
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from '@/components/ui/select'
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldInput,
  NumberFieldIncrement
} from '@/components/ui/number-field'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  trailData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:isOpen', 'submitted'])

const { getAuthHeaders, fetchWithAuth} = useAuth()

const difficultyOptions = [
  { value: 0, label: 'Easy' },
  { value: 1, label: 'Moderate' },
  { value: 2, label: 'Difficult' },
  { value: 3, label: 'Very Difficult' },
]

const defaultTrailState = {
  name: '',
  location: '',
  length_mi: 0.0,
  estimated_time_hr: 0.0,
  required_water_liters: 0.0,
  difficulty: 1,
  alltrails_url: '',
  trailhead_gmaps_url: '',
  trailhead_amaps_url: '',
  description: ''
}


const formData = reactive({ ...defaultTrailState })

watch(() => props.trailData, (newTrail) => {
  if (newTrail) {
    Object.assign(formData, newTrail)
  } else {
    Object.assign(formData, defaultTrailState)
  }
}, { immediate: true })


const isEditing = computed(() => !!props.trailData)
const dialogTitle = computed(() => isEditing.value ? 'Edit Trail' : 'Create New Trail')
const submitButtonText = computed(() => isEditing.value ? 'Save Changes' : 'Create Trail')



const selectedFile = ref(null);
function handleFileChange(event) {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
  }
}

const uploadPhoto = async (trailId) => {
  try {
    const endpoint = `/api/images/uploads/${trailId}`;
    const method = 'POST';
    const uploadFormData = new FormData()
    uploadFormData.append("file", selectedFile.value)

    const headers = {
       ...getAuthHeaders(),
    }

    const response = await fetch(endpoint,
      {
        method: method,
        headers,
        body: uploadFormData,
      });
    if (!response.ok) {
      throw Error(response.status)
    }


    toast.success(`Trail Photo successfully updated 🎉`)
  } catch (error) {
    console.error("Failed to submit trail photo:", error)
    toast.error('Photo Submission Failed', { description: error.message })
  }
}

const handleSubmit = async () => {
  try {
    const endpoint = isEditing.value ? `/api/admin/trails/${props.trailData.id}` : '/api/admin/trails'
    const method = isEditing.value ? 'PUT' : 'POST'

    const response = await fetchWithAuth(endpoint,{method: method, body: JSON.stringify(formData)})
    if (!response.ok) {
      throw Error(response.status)
    }
    const body = await response.json()

    if (selectedFile.value) {
      await uploadPhoto(body.id);
    }
    toast.success(`Trail successfully ${isEditing.value ? 'updated' : 'created'}! 🎉`)
    Object.assign(formData, defaultTrailState)
    emit('submitted')
    emit('update:isOpen', false)
  } catch (error) {
    console.error("Failed to submit trail form:", error)
    toast.error('Submission Failed', { description: error.message })
  }
}

const deleteTrail = async () => {
    try {
        const endpoint = `/api/admin/trails/${props.trailData.id}`
        const method = "DELETE"

        const response = await fetchWithAuth(endpoint, {method: method})
        if (!response.ok) {
          throw Error(response.status)
        }

        toast.success(`Trail successfully Deleted`)
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
    <DialogContent class="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{{ dialogTitle }}</DialogTitle>
        <DialogDescription>
          Fill out the details for the trail below. All fields are required except for the optional warning.
        </DialogDescription>
      </DialogHeader>

      <form id="trail-form" @submit.prevent="handleSubmit" class="py-4 pr-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="name">Trail Name</Label>
            <Input id="name" v-model="formData.name" required />
          </div>

          <div class="space-y-2">
            <Label for="location">Location</Label>
            <Input id="location" v-model="formData.location" placeholder="e.g., Crystal Cove State Park" required />
          </div>

          <div class="space-y-2">
            <Label for="length_mi">Length (miles)</Label>
            <NumberField id="length_mi" v-model="formData.length_mi" :min="0" :step="0.1">
              <NumberFieldContent>
                <NumberFieldDecrement />
                <NumberFieldInput />
                <NumberFieldIncrement />
              </NumberFieldContent>
            </NumberField>
          </div>

          <div class="space-y-2">
            <Label for="estimated_time_hr">Estimated Time (hours)</Label>
            <NumberField id="estimated_time_hr" v-model="formData.estimated_time_hr" :min="0" :step="0.25">
              <NumberFieldContent>
                <NumberFieldDecrement />
                <NumberFieldInput />
                <NumberFieldIncrement />
              </NumberFieldContent>
            </NumberField>
          </div>

          <div class="space-y-2">
            <Label for="required_water_liters">Required Water (liters)</Label>
            <NumberField id="required_water_liters" v-model="formData.required_water_liters" :min="0" :step="0.5">
              <NumberFieldContent>
                <NumberFieldDecrement />
                <NumberFieldInput />
                <NumberFieldIncrement />
              </NumberFieldContent>
            </NumberField>
          </div>

          <div class="space-y-2">
            <Label for="difficulty">Difficulty</Label>
            <Select id="difficulty" v-model="formData.difficulty">
              <SelectTrigger>
                <SelectValue placeholder="Select a difficulty" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="option in difficultyOptions"
                  :key="option.value"
                  :value="option.value">
                  {{ option.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="space-y-2 col-span-1 md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label class="mb-2" for="picture">Picture</Label>
              <Input id="picture" type="file" accept="image/png, image/jpeg" @change="handleFileChange" :required="!isEditing"/>
            </div>
            <div v-if="isEditing">
              <p class="text-sm text-gray-400">This trail has an existing image, view it with the link below or upload a new one to replace it.</p>
              <a class="text-blue-300 hover:underline text-sm" target="_blank" :href="`/api/images/uploads/` + formData.id">/api/images/uploads/{{ formData.id }}</a>
            </div>
          </div>

          <div class="space-y-2 col-span-1 md:col-span-2">
            <Label for="alltrails_url">AllTrails URL</Label>
            <Input id="alltrails_url" type="url" v-model="formData.alltrails_url" placeholder="https://www.alltrails.com/..."  />
          </div>

          <div class="space-y-2 col-span-1 md:col-span-2">
            <Label for="trailhead_gmaps_url">Google Maps Trailhead URL</Label>
            <Input id="trailhead_gmaps_url" type="url" v-model="formData.trailhead_gmaps_url" placeholder="https://maps.app.goo.gl/..."  />
          </div>

          <div class="space-y-2 col-span-1 md:col-span-2">
            <Label for="trailhead_amaps_url">Apple Maps Trailhead URL</Label>
            <Input id="trailhead_amaps_url" type="url" v-model="formData.trailhead_amaps_url" placeholder="https://maps.apple.com/..."  />
          </div>

          <div class="space-y-2 col-span-1 md:col-span-2">
            <Label for="description">Optional Trail Warning</Label>
            <Input id="description" v-model="formData.description" placeholder="e.g., 'Expect to get wet on this trail! Bring waterproof shoes.'" />
          </div>
        </div>
      </form>

      <DialogFooter class="w-full flex flex-row flex-nowrap justify-between items-center gap-2">
        <Button type="button" variant="outline" @click="handleClose(false)">Cancel</Button>
        <Button type="submit" variant="default" form="trail-form">{{ submitButtonText }}</Button>
        <Button v-if="isEditing" type="button" variant="destructive" @click="deleteTrail()">Delete</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>