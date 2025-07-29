<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Edit Signup</DialogTitle>
      </DialogHeader>

      <div class="grid gap-4 py-4">
        <div class="grid grid-cols-2 items-center gap-4">
          <Label for="name">Name</Label>
          <Input id="name" v-model="form.name" />
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
        <div v-if="form.transport_type === 'driver'" class="col-span-2 space-y-4">
          <div v-if="vehicles.length">
            <Label for="vehicleSelect">Choose Vehicle</Label>
            <Select v-model="form.vehicle_id">
              <SelectTrigger id="vehicleSelect">
                <SelectValue placeholder="Select Vehicle…" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="v in vehicles"
                  :key="v.id"
                  :value="v.id"
                >
                  {{ v.description }} ({{ v.passenger_seats }} seats)
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div v-else class="space-y-2">
            <div class="grid grid-cols-2 items-center gap-4">
              <Label for="vehicleYear">Year</Label>
              <Input
                id="vehicleYear"
                v-model="newVehicle.year"
                placeholder="2021"
              />
            </div>
            <div class="grid grid-cols-2 items-center gap-4">
              <Label for="vehicleMake">Make</Label>
              <Input
                id="vehicleMake"
                v-model="newVehicle.make"
                placeholder="Toyota"
              />
            </div>
            <div class="grid grid-cols-2 items-center gap-4">
              <Label for="vehicleModel">Model</Label>
              <Input
                id="vehicleModel"
                v-model="newVehicle.model"
                placeholder="Corolla"
              />
            </div>
            <NumberField
              id="passengers"
              v-model="newVehicle.passenger_seats"
              :min="1"
              :default-value="1"
            >
              <Label for="passengers" class="font-semibold text-midnight">Passenger Capacity</Label>
              <NumberFieldContent class="max-w-1/4">
                <NumberFieldDecrement />
                <NumberFieldInput />
                <NumberFieldIncrement />
              </NumberFieldContent>
            </NumberField>
            <Button @click="addVehicle">Add Vehicle</Button>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="open = false">Cancel</Button>
        <Button :disabled="saveDisabled" @click="onSave">Save</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup>
import {ref, reactive, watch, onMounted, computed} from 'vue'
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
  user:   { type: Object, required: true },
  hikeId: { type: Number, required: true }
})
const emit = defineEmits(['saved','close'])
const open = ref(true)
watch(open, v => { if (!v) emit('close') })

const saveDisabled = computed(() =>
  form.transport_type === 'driver' && !form.vehicle_id
)

const form = reactive({
  name:           props.user.name,
  transport_type: props.user.transport_type,
  vehicle_id:     props.user.transport_type === 'driver'
                    ? props.user.vehicle_id
                    : null
})

const vehicles = ref([])
const newVehicle = reactive({
  year:            '',
  make:            '',
  model:           '',
  passenger_seats: 1
})

const { postWithAuth, fetchWithAuth } = useAuth()

async function loadVehicles() {
  try {
    const res = await fetchWithAuth(`/vehicles?member_id=${props.user.member_id}`)
    if (!res.ok) throw new Error()
    vehicles.value = await res.json()
  } catch {
    vehicles.value = []
  }
}

onMounted(() => {
  if (form.transport_type === 'driver') loadVehicles()
})
watch(() => form.transport_type, v => {
  if (v === 'driver') loadVehicles()
})

// create a new vehicle, then re-load
async function addVehicle() {
  try {
    const res = await postWithAuth('/vehicles', {
      member_id: props.user.member_id,
      make: newVehicle.make,
      model: newVehicle.model,
      year: newVehicle.year,
      passenger_seats: newVehicle.passenger_seats
    })
    if (!res.ok) throw new Error()
    const created = await res.json()
    vehicles.value.push(created)
    form.vehicle_id = created.id
    toast.success('Vehicle added')
  } catch {
    toast.error('Could not add vehicle')
  }
}

async function onSave() {
  try {
    const payload = {
      hike_id:        props.hikeId,
      user_id:        props.user.member_id,
      name:      form.name,
      transport_type: form.transport_type
    }
    if (form.transport_type === 'driver') {
      payload.vehicle_id = form.vehicle_id
    }

    const res = await postWithAuth('/active-hike/modify-user', payload)
    if (!res.ok) {
      const err = await res.text()
      throw new Error(err || 'Unknown error')
    }

    props.user.name      = form.name
    props.user.transport_type = form.transport_type
    props.user.vehicle_id     = form.vehicle_id

    toast.success('Signup updated')
    emit('saved', props.user)
    open.value = false
  } catch {
    toast.error('Update failed')
  }
}
</script>
