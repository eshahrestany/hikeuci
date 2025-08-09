<script setup>
import {ref, reactive, onMounted, watch, computed} from 'vue'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogFooter, DialogDescription
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Combobox, ComboboxAnchor, ComboboxTrigger, ComboboxInput,
  ComboboxList, ComboboxItem, ComboboxItemIndicator,
  ComboboxGroup, ComboboxEmpty
} from '@/components/ui/combobox'
import {
  Select, SelectTrigger, SelectValue, SelectContent, SelectItem
} from '@/components/ui/select'
import {
  NumberField, NumberFieldContent, NumberFieldDecrement,
  NumberFieldInput, NumberFieldIncrement
} from '@/components/ui/number-field'
import { Check, ChevronsUpDown, Search } from 'lucide-vue-next'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'
import {Input} from "@/components/ui/input/index.js";
import {cn} from "@/lib/utils.js";

const emit  = defineEmits(['close', 'added'])
const open  = ref(true)

watch(open, v => { if (!v) emit('close') })

const { fetchWithAuth, postWithAuth } = useAuth()

// ─── Emails ─────────────────────────────────────────────────────────────────
const emailOptions = ref([])           // [{member_id, email}]
const selected    = ref(null)          // whole option object

onMounted(loadEmails)
async function loadEmails() {
  const res = await fetchWithAuth(`/active-hike/list-emails-not-in-hike`)
  const raw = res.ok ? await res.json() : []

  emailOptions.value = raw.map(o => ({
    ...o,               // keep member_id / email for later use
    value: o.email,     // required by the example
    label: o.email,     // displayed & compared against
  }))
}

// ─── Form ───────────────────────────────────────────────────────────────────
const form = reactive({
  transport_type: 'passenger',
  vehicle_id: null,
})

// ─── Vehicles (only if driver) ──────────────────────────────────────────────
const vehicles = ref([])
const newVehicle = reactive({ year:'', make:'', model:'', passenger_seats:1 })

watch(() => form.transport_type, t => {
  if (t === 'driver' && selected.value) loadVehicles()
})

async function loadVehicles() {
  vehicles.value = []
  if (!selected.value) return
  const res = await fetchWithAuth(`/vehicles?member_id=${selected.value.member_id}`)
  vehicles.value = res.ok ? await res.json() : []
}

async function addVehicle() {
  try {
    const res  = await postWithAuth('/vehicles', {
      member_id: selected.value.member_id,
      year: newVehicle.year,
      make: newVehicle.make,
      model: newVehicle.model,
      passenger_seats: newVehicle.passenger_seats,
    })
    const created = await res.json()
    vehicles.value.push(created)
    form.vehicle_id = created.id
    toast.success('Vehicle added')
  } catch {
    toast.error('Could not add vehicle')
  }
}

// ─── Save ───────────────────────────────────────────────────────────────────
async function onSave() {
  if (!selected.value) return toast.error('Select a member')
  try {
    const payload = {
      member_id: selected.value.member_id,
      transport_type: form.transport_type,
      vehicle_id: form.transport_type === 'driver' ? form.vehicle_id : null,
    }
    const res = await postWithAuth('/active-hike/add-user', payload)
    if (!res.ok) throw new Error(await res.text())
    const added = await res.json()   // backend returns new user object
    toast.success('Late signup added')
    emit('added', added)
  } catch {
    toast.error('Add failed')
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-[450px]">
      <DialogHeader>
        <DialogTitle>Add Late Signup</DialogTitle>
        <DialogDescription>Select member and details</DialogDescription>
      </DialogHeader>

      <!-- Email Combobox -->
      <Combobox by="email" v-model="selected">
        <ComboboxAnchor class="w-full">
          <div class="relative w-full items-center">
            <ComboboxInput class="pl-9" :display-value="(val) => val?.email ?? ''" placeholder="Select email..." />
            <span class="absolute start-0 inset-y-0 flex items-center justify-center px-3">
              <Search class="size-4 text-muted-foreground" />
            </span>
          </div>
        </ComboboxAnchor>

        <ComboboxList>
          <ComboboxEmpty>
            No members found.
          </ComboboxEmpty>

          <ComboboxGroup>
            <ComboboxItem
              v-for="opt in emailOptions"
              :key="opt.value"
              :value="opt"
            >
              {{ opt.label }}

              <ComboboxItemIndicator>
                <Check :class="cn('ml-auto h-4 w-4')" />
              </ComboboxItemIndicator>
            </ComboboxItem>
          </ComboboxGroup>
        </ComboboxList>
      </Combobox>

      <!-- Transport Type -->
      <div class="grid grid-cols-2 items-center gap-4 mt-4">
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

      <!-- Driver vehicle logic -->
      <div v-if="form.transport_type === 'driver'" class="mt-4 space-y-4">
        <div v-if="vehicles.length">
          <Label for="vehicleSelect">Choose Vehicle</Label>
          <Select v-model="form.vehicle_id">
            <SelectTrigger id="vehicleSelect">
              <SelectValue placeholder="Select Vehicle…" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="v in vehicles" :key="v.id" :value="v.id">
                {{ v.description }} ({{ v.passenger_seats }} seats)
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div v-else class="space-y-2">
          <div class="grid grid-cols-2 items-center gap-4">
            <Label>Year</Label><Input v-model="newVehicle.year" />
          </div>
          <div class="grid grid-cols-2 items-center gap-4">
            <Label>Make</Label><Input v-model="newVehicle.make" />
          </div>
          <div class="grid grid-cols-2 items-center gap-4">
            <Label>Model</Label><Input v-model="newVehicle.model" />
          </div>

          <NumberField v-model="newVehicle.passenger_seats" :min="1" :default-value="1">
            <Label class="font-semibold">Passenger Capacity</Label>
            <NumberFieldContent class="max-w-1/4">
              <NumberFieldDecrement /><NumberFieldInput /><NumberFieldIncrement />
            </NumberFieldContent>
          </NumberField>

          <Button @click="addVehicle">Add Vehicle</Button>
        </div>
      </div>

      <DialogFooter class="mt-6">
        <Button variant="outline" @click="open = false">Cancel</Button>
        <Button @click="onSave">Add</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
