<script setup>
import {ref, reactive, onMounted, watch} from 'vue'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogFooter, DialogDescription
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Combobox, ComboboxAnchor, ComboboxInput,
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
import { Check, Search } from 'lucide-vue-next'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'
import {Input} from "@/components/ui/input";
import {cn} from "@/lib/utils.js";
import {RadioGroup, RadioGroupItem} from "@/components/ui/radio-group";

const emit  = defineEmits(['close', 'added'])
const open  = ref(true)

watch(open, v => { if (!v) emit('close') })

const { fetchWithAuth, postWithAuth } = useAuth()

const props = defineProps({
  mode: {type: String, required: true} // 'new' or 'late'
})
const modeCapital = props.mode.charAt(0).toUpperCase() + props.mode.slice(1)

const lateMode = ref('userlink') // 'userlink' or 'manual'

// ─── Emails ─────────────────────────────────────────────────────────────────
const emailOptions = ref([])           // [{member_id, email}]
const selected    = ref(null)          // whole option object

onMounted(loadEmails)
async function loadEmails() {
  const res = await fetchWithAuth(`/api/admin/list-emails-not-in-hike`)
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
  const res = await fetchWithAuth(`/api/vehicles?member_id=${selected.value.member_id}`)
  vehicles.value = res.ok ? await res.json() : []
}

async function addVehicle() {
  try {
    const res  = await postWithAuth('/api/vehicles', {
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
async function submitNew() {
  if (!selected.value) return toast.error('Select a member')
  try {
    const payload = {
      member_id: selected.value.member_id,
    }
    const res = await postWithAuth('/api/admin/add-user', payload)
    if (!res.ok) throw new Error(await res.text())
    toast.success('New signup added')
    open.value = false
  } catch {
    toast.error('Add signup failed')
  }
}

async function submitLate() {
  if (!selected.value) return toast.error('Select a member')
  try {
    const payload = {
      member_id: selected.value.member_id,
      signup_mode: lateMode.value
    }

    if (lateMode.value === 'manual') {
      payload.transport_type = form.transport_type
      payload.vehicle_id = form.transport_type === 'driver' ? form.vehicle_id : null
    }

    const res = await postWithAuth('/api/admin/add-user', payload)
    if (!res.ok) throw new Error(await res.text())

    if (lateMode === 'manual') {
      const added = await res.json()   // backend returns new user object
      toast.success('Late signup added')
      emit('added', added)
    }
    else { toast.success('Late signup email sent') }

    open.value = false
  } catch (error) {
    toast.error(`Add failed: ${error}`)
  }
}
</script>

<template>
  <Dialog v-model:open="open" aria-describedby="undefined">
    <DialogContent class="sm:max-w-[450px]" aria-describedby="undefined">
      <DialogHeader>
        <DialogTitle>Add {{modeCapital}} Signup</DialogTitle>
        <DialogDescription v-if="props.mode === 'new'">Select member by email</DialogDescription>
      </DialogHeader>

      <template v-if="props.mode === 'late'">
        <p class="text-sm">Select a member, then select the signup mode.</p>
        <p class="text-xs text-primary/60">
          <span class="font-bold">User Signup Link</span> will immediately send the user a special late signup link via email.
          As soon as they submit the signup email, they will immediately receive a waiver by email.
        </p>
        <p class="text-xs text-primary/60">
          <span class="font-bold">Manual Officer Signup</span> can be used if we already know the member's signup transport info.
          On submission, the member will immediately receive a waiver by email.
        </p>
      </template>

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
            <ComboboxItem v-for="opt in emailOptions" :key="opt.value" :value="opt">
              {{ opt.label }}
              <ComboboxItemIndicator>
                <Check :class="cn('ml-auto h-4 w-4')" />
              </ComboboxItemIndicator>
            </ComboboxItem>
          </ComboboxGroup>
        </ComboboxList>
      </Combobox>


      <template v-if="props.mode === 'late'">
        <RadioGroup v-model="lateMode" :orientation="'vertical'">
          <p class="font-semibold">Signup Mode</p>
          <div class="flex items-center space-x-2">
            <RadioGroupItem id="r1" value="userlink" />
            <Label for="r1">User Signup Link</Label>
          </div>
          <div class="flex items-center space-x-2">
            <RadioGroupItem id="r2" value="manual" />
            <Label for="r2">Manual Officer Signup</Label>
          </div>
        </RadioGroup>

        <template v-if="lateMode === 'manual'">
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
              <Label for="vehicleSelect" class="mb-2">Choose Vehicle</Label>
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

            <div v-if="vehicles.length" class="mb-2">Or add a new one below</div>
            <div class="space-y-2">
              <div class="grid grid-cols-2 items-center gap-4">
                <Label>Year</Label><Input v-model="newVehicle.year" />
              </div>
              <div class="grid grid-cols-2 items-center gap-4">
                <Label>Make</Label><Input v-model="newVehicle.make" />
              </div>
              <div class="grid grid-cols-2 items-center gap-4">
                <Label>Model</Label><Input v-model="newVehicle.model" />
              </div>

              <NumberField
                  v-model="newVehicle.passenger_seats"
                  :min="1"
                  :default-value="1"
                  class="grid grid-cols-2 items-center gap-4"
              >
                <Label class="font-semibold">Passenger Capacity</Label>
                <NumberFieldContent class="max-w-[80px]">
                  <NumberFieldDecrement /><NumberFieldInput /><NumberFieldIncrement />
                </NumberFieldContent>
              </NumberField>

              <Button @click="addVehicle">Add Vehicle</Button>
            </div>
          </div>
        </template>
      </template>

      <DialogFooter class="mt-6">
        <Button variant="outline" @click="open = false">Cancel</Button>
        <Button v-if="props.mode === 'new'" @click="submitNew">Submit</Button>
        <Button v-else @click="submitLate">Submit</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
