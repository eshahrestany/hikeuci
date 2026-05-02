<script setup>
import {ref, computed, onMounted, reactive, watch} from 'vue'
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader
} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {RadioGroup, RadioGroupItem} from '@/components/ui/radio-group'
import {Button} from '@/components/ui/button'
import backgroundImage from '@/assets/hiking_bg.jpg'
import {
  NumberField,
  NumberFieldContent,
  NumberFieldInput,
  NumberFieldIncrement,
  NumberFieldDecrement
} from "@/components/ui/number-field/index.js";
import {Skeleton} from '@/components/ui/skeleton'
import {parsePhoneNumberFromString} from 'libphonenumber-js'
import {SPhoneInput} from "@/components/ui/phone-input";
import {PlusCircle, X, ChevronDown, Check} from "lucide-vue-next";
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from "@/components/ui/tooltip/index.js";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover/index.js"
import HikeStatsBar from '@/components/common/HikeStatsBar.vue';

const props = defineProps({
  title: {
    type: String,
    default: 'Event Signup'
  },
})

const hikeTitle = ref(props.title)
const trailStats = ref(null)
const loading = ref(true)
const error = ref(null)
const signupSuccess = ref(false)
const alreadySigned = ref(false)
const cancelSuccess = ref(false)

const vehicles = ref([])
const tokenRef = ref('')
const selectedVehicleId = ref(null)

const name = ref('')
const email = ref('')
const phoneNumber = ref('')
const phoneNumberAlreadySet = ref(false)
const foodPreference = ref(null)
const transportation = ref(null)
const driverConfirmationName = ref('')
const phoneTouched = ref(false)

const newVehicle = reactive({
  year: '',
  make: '',
  model: '',
  passenger_seats: 1
})

const hasVehicles = computed(() => Array.isArray(vehicles.value) && vehicles.value.length > 0)
const validNewVehicle = computed(() =>
    Number(newVehicle.year) >= 1960 &&
    Number(newVehicle.year) <= new Date().getFullYear() + 1 &&
    !!newVehicle.make &&
    !!newVehicle.model &&
    Number(newVehicle.passenger_seats) >= 1 &&
    Number(newVehicle.passenger_seats) <= 7
)
const isDriver = computed(() => transportation.value === 'is_driver')
const addingNewVehicle = ref(false)
const vehicleDropdownOpen = ref(false)
const selectedVehicle = computed(() => vehicles.value.find(v => v.id === selectedVehicleId.value) ?? null)
const driverInfoValid = computed(() => {
  if (driverConfirmationName.value !== name.value) return false
  if (hasVehicles.value && !addingNewVehicle.value) {
    return !!selectedVehicleId.value
  }
  return validNewVehicle.value
})

const isPhoneValid = computed(() => !!phone.value)
const phone = computed(() => {
  const input = phoneNumber.value
  if (!input) return null
  const parsed = parsePhoneNumberFromString(input, 'US')
  return parsed && parsed.isValid() ? parsed.format('E.164') : null
})

const allowSubmit = computed(() => {
  if (!name.value || !email.value || !foodPreference.value || !transportation.value || !isPhoneValid.value) return false
  if (isDriver.value && !driverInfoValid.value) return false
  return true
})

// Clear vehicle selection when user toggles off driver
watch(transportation, v => {
  if (v !== 'is_driver') selectedVehicleId.value = null
})

function updatePhoneNumber(newValue) {
  phoneNumber.value = newValue
  phoneTouched.value = true
}

function startAddVehicle() {
  addingNewVehicle.value = true
  selectedVehicleId.value = null
}

function cancelAddVehicle() {
  addingNewVehicle.value = false
}

function pickExistingVehicle(id) {
  selectedVehicleId.value = id
  addingNewVehicle.value = false
  vehicleDropdownOpen.value = false
}

const deletingVehicleId = ref(null)

async function deleteVehicle(vehicleId) {
  deletingVehicleId.value = vehicleId
  try {
    const res = await fetch(`/api/hike-signup/vehicle/${vehicleId}?token=${tokenRef.value}`, {
      method: 'DELETE',
    })
    if (!res.ok) return
    vehicles.value = vehicles.value.filter(v => v.id !== vehicleId)
    if (selectedVehicleId.value === vehicleId) selectedVehicleId.value = null
  } finally {
    deletingVehicleId.value = null
  }
}

// Fetch signup data
onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    const params = new URLSearchParams(window.location.search)
    const token = params.get("token")
    if (!token) {
      throw new Error("No token provided in URL")
    }
    tokenRef.value = token

    const res = await fetch(`/api/hike-signup?token=${token}`)
    if (!res.ok) {
      let errMessage = `HTTP error! status: ${res.status}`
      try {
        const errData = await res.json()
        errMessage = errData.error || errMessage
      } catch { /* ignore */
      }
      throw new Error(errMessage)
    }
    const jsonResponse = await res.json()

    if (jsonResponse.formData === null) {
      const status = jsonResponse.status
      let message = status || 'Data is null'
      throw new Error(message)
    }

    if (jsonResponse.status === "signed") {
      alreadySigned.value = true
      trailStats.value = jsonResponse.trail || null
      if (jsonResponse.hike?.title) hikeTitle.value = jsonResponse.hike.title
    } else if (jsonResponse.status === "ready") {
      const data = jsonResponse.formData
      name.value = data.name
      email.value = data.email
      phoneNumber.value = data.tel || ''
      phoneNumberAlreadySet.value = !!data.tel
      phoneTouched.value = !!data.tel

      vehicles.value = jsonResponse.vehicles || []
      hikeTitle.value = jsonResponse.hike.title
      trailStats.value = jsonResponse.trail || null
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function submitForm() {
  if (!allowSubmit.value) return

  const payload = {
    tel: phone.value,
    food: foodPreference.value,
    transportation: transportation.value,
  }

  if (isDriver.value) {
    if (hasVehicles.value && !addingNewVehicle.value) {   // <-- missing paren fixed
      payload.vehicle_id = selectedVehicleId.value
    } else {
      payload.vehicle_id = 'new'
      payload.new_vehicle = {
        year: newVehicle.year,
        make: newVehicle.make,
        model: newVehicle.model,
        passenger_seats: Number(newVehicle.passenger_seats),
      }
    }
  }

  try {
    loading.value = true
    error.value = null

    const res = await fetch(`/api/hike-signup?token=${tokenRef.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      let errMessage = `HTTP error! status: ${res.status}`
      try {
        const errData = await res.json()
        errMessage = errData.error || errMessage
      } catch { /* ignore */
      }
      throw new Error(errMessage)
    }

    const jsonResponse = await res.json()
    if (jsonResponse.success) {
      signupSuccess.value = true
    } else {
      throw new Error(jsonResponse.error || 'Unknown error occurred')
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function submitCancelRequest() {
  try {
    loading.value = true
    error.value = null

    const res = await fetch(`/api/hike-signup/cancel?token=${tokenRef.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!res.ok) {
      let errMessage = `HTTP error! status: ${res.status}`
      try {
        const errData = await res.json()
        errMessage = errData.error || errMessage
      } catch {
      }
      throw new Error(errMessage)
    }

    const jsonResponse = await res.json()
    if (jsonResponse[0].success) {
      cancelSuccess.value = true
    } else {
      throw new Error(jsonResponse.error || 'Unknown error occurred')
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

</script>


<template>
  <section
      class="relative bg-cover bg-center py-20 bg-fixed"
      :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <div class="pg-scrim" aria-hidden="true"/>
    <div class="relative mx-auto max-w-2xl px-4">
      <Card>
        <CardHeader class="p-6">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-9 w-3/4 mx-auto"/>
            <div class="space-y-2">
              <Skeleton class="h-4 w-full"/>
              <Skeleton class="h-4 w-full"/>
              <Skeleton class="h-4 w-2/3"/>
            </div>
          </div>
          <template v-else>
            <h1 class="text-center text-3xl font-bold tracking-tight sm:text-4xl font-montserrat" style="color:#f5f7fb">
              {{ hikeTitle }}
            </h1>
            <HikeStatsBar :trail="trailStats" class="mt-4" />
          </template>
        </CardHeader>
        <CardContent class="p-6 pt-0">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
          </div>
          <div v-else-if="error" class="text-red-500 text-center">
            <img
              src="@/assets/petr.png"
              class="mx-auto max-h-[150px] mb-2"
              alt=""
            />
            {{ error }}
          </div>
          <div v-else-if="signupSuccess" class="text-center">
            <p class="text-lg font-medium" style="color:#f5f7fb">You have succesfully signed up for this hike.</p>
            <p class="text-sm mt-2" style="color:#c8d0de">You can return to this link before the signup deadline to cancel if
              needed.</p>
          </div>
          <div v-else-if="alreadySigned" class="text-center">
            <p v-if="cancelSuccess" style="color:#f5f7fb">Successfully canceled.</p>
            <p v-else class="text-lg font-medium" style="color:#f5f7fb">
              You have already signed up for this event. If you need to cancel your signup, please click the button
              below.
            </p>
            <p class="text-sm mt-2" style="color:#c8d0de">You can still re-sign up for the hike before the signup submission deadline.</p>
            <div v-if="!cancelSuccess" class="mt-6">
              <Button type="button" variant="destructive" @click="submitCancelRequest">Cancel My Signup</Button>
            </div>
          </div>
          <div v-else class="space-y-6">
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div class="space-y-2">
                <Label for="name" class="font-semibold text-midnight">Name</Label>
                <Input id="name" type="text" v-model="name" disabled/>
              </div>
              <div class="space-y-2">
                <Label for="email" class="font-semibold text-midnight">Email</Label>
                <Input id="email" type="email" v-model="email" disabled/>
              </div>
            </div>
            <div class="space-y-2">
              <Label for="phone" class="font-semibold text-midnight">Phone Number</Label>
              <Input v-if="phoneNumberAlreadySet" v-model="phoneNumber" disabled/>
              <SPhoneInput v-else @update:model-value="updatePhoneNumber"/>
            </div>
            <div v-if="phoneTouched && !isPhoneValid" class="text-red-500 text-sm mt-1">
              Please enter a valid phone number.
            </div>
            <div class="space-y-3 pt-2">
              <Label class="font-semibold text-midnight">
                Are you interested in getting after-hike food?
              </Label>
              <RadioGroup v-model="foodPreference" class="flex items-center gap-6">
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="food-yes" value="yes"/>
                  <Label for="food-yes" class="font-normal">Yes</Label>
                </div>
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="food-no" value="no"/>
                  <Label for="food-no" class="font-normal">No</Label>
                </div>
              </RadioGroup>
            </div>
            <div class="space-y-3 pt-2">
              <Label class="font-semibold text-midnight">
                How do you plan on getting to the event?
              </Label>
              <RadioGroup v-model="transportation" class="grid gap-3">
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="driver" value="is_driver"/>
                  <Label for="driver" class="font-normal">
                    I can drive and I am willing to transport other members
                  </Label>
                </div>
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="passenger" value="is_passenger"/>
                  <Label for="passenger" class="font-normal">
                    I do not have my own transportation and need to carpool with other members
                  </Label>
                </div>
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="self-transport" value="is_self-transport"/>
                  <Label for="self-transport" class="font-normal">
                    I will arrange my own transportation to the trailhead.
                  </Label>
                </div>
              </RadioGroup>
            </div>

            <!-- Dynamic Driver Section -->
            <Transition name="expand-section">
              <div v-if="isDriver" class="expand-section">
                <div class="expand-section-inner border-t pt-6 space-y-6" style="border-color: rgba(255,255,255,0.14)">
                  <!-- Vehicle Input (dynamic) -->
                  <div class="space-y-4">
                    <!-- Existing vehicles: choose one. "Add new vehicle" is the
                         final option inside the dropdown when vehicles exist. -->
                    <div v-if="hasVehicles" class="space-y-2">
                      <Label for="vehicleSelect" class="font-semibold text-midnight">Choose your vehicle</Label>
                      <Popover v-model:open="vehicleDropdownOpen">
                        <PopoverTrigger as-child>
                          <button
                            id="vehicleSelect"
                            type="button"
                            class="border-input flex w-full items-center justify-between gap-2 rounded-md border bg-transparent px-3 py-2 text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 h-9"
                          >
                            <span :class="!selectedVehicle && !addingNewVehicle ? 'text-muted-foreground' : ''">
                              <template v-if="addingNewVehicle">Adding a new vehicle…</template>
                              <template v-else-if="selectedVehicle">
                                {{ selectedVehicle.description || `${selectedVehicle.year} ${selectedVehicle.make} ${selectedVehicle.model}` }}
                                ({{ selectedVehicle.passenger_seats }} passengers)
                              </template>
                              <template v-else>Select Vehicle…</template>
                            </span>
                            <ChevronDown class="size-4 opacity-50 flex-shrink-0" />
                          </button>
                        </PopoverTrigger>
                        <PopoverContent
                          align="start"
                          :side-offset="4"
                          class="public-glass-popover p-1 w-[var(--reka-popover-trigger-width,16rem)] min-w-[8rem]"
                        >
                          <div
                            v-for="v in vehicles"
                            :key="v.id"
                            class="flex items-center gap-1.5 rounded-sm px-2 py-1.5 text-sm cursor-pointer select-none hover:bg-accent hover:text-accent-foreground transition-colors"
                            @click="pickExistingVehicle(v.id)"
                          >
                            <Check v-if="selectedVehicleId === v.id && !addingNewVehicle" class="h-4 w-4 flex-shrink-0" />
                            <span v-else class="h-4 w-4 flex-shrink-0" />
                            <span class="flex-1 min-w-0 truncate">
                              {{ v.description || `${v.year} ${v.make} ${v.model}` }}
                              ({{ v.passenger_seats }} passengers)
                            </span>
                            <button
                              type="button"
                              class="flex-shrink-0 rounded p-0.5 text-muted-foreground hover:bg-muted hover:text-destructive transition-colors disabled:opacity-40"
                              :disabled="deletingVehicleId === v.id"
                              @click.stop="deleteVehicle(v.id)"
                              :aria-label="`Remove ${v.description || v.model}`"
                            >
                              <X class="h-3.5 w-3.5" />
                            </button>
                          </div>
                          <div class="my-1 h-px" style="background: rgba(255,255,255,0.12);" />
                          <div
                            class="flex items-center gap-1.5 rounded-sm px-2 py-1.5 text-sm cursor-pointer select-none hover:bg-accent hover:text-accent-foreground transition-colors"
                            :class="{ 'text-accent-foreground': addingNewVehicle }"
                            @click="startAddVehicle(); vehicleDropdownOpen = false"
                          >
                            <Check v-if="addingNewVehicle" class="h-4 w-4 flex-shrink-0" />
                            <PlusCircle v-else class="h-4 w-4 flex-shrink-0" />
                            <span class="flex-1 min-w-0 truncate font-medium">Add new vehicle</span>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </div>

                    <!-- New vehicle form (animated open/close) -->
                    <Transition name="expand-section">
                      <div v-if="!hasVehicles || addingNewVehicle" class="expand-section">
                        <div class="expand-section-inner space-y-2 pt-1">
                          <p v-if="!hasVehicles" class="text-sm" style="color:#c8d0de">
                            We don't have a vehicle on file for you yet. Add one below:
                          </p>

                          <div class="grid grid-cols-2 items-center gap-4">
                            <Label for="vehicleYear" class="font-semibold text-midnight">Year</Label>
                            <Input id="vehicleYear" v-model="newVehicle.year" placeholder="2021"/>
                          </div>
                          <div class="grid grid-cols-2 items-center gap-4">
                            <Label for="vehicleMake" class="font-semibold text-midnight">Make</Label>
                            <Input id="vehicleMake" v-model="newVehicle.make" placeholder="Toyota"/>
                          </div>
                          <div class="grid grid-cols-2 items-center gap-4">
                            <Label for="vehicleModel" class="font-semibold text-midnight">Model</Label>
                            <Input id="vehicleModel" v-model="newVehicle.model" placeholder="Corolla"/>
                          </div>
                          <div class="grid grid-cols-2 items-center gap-4">
                            <Label for="passengers" class="font-semibold text-midnight">Passenger Capacity</Label>
                            <div class="max-w-[80px]">
                              <TooltipProvider>
                                <Tooltip>
                                  <TooltipTrigger as-child>
                                    <NumberField
                                        id="passengers"
                                        v-model="newVehicle.passenger_seats"
                                        :min="1"
                                        :max="7"
                                        :default-value="1">
                                      <NumberFieldContent>
                                        <NumberFieldDecrement/>
                                        <NumberFieldInput/>
                                        <NumberFieldIncrement/>
                                      </NumberFieldContent>
                                    </NumberField>
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p class="text-sm">This number represents the number of passengers you can carry, not
                                      including yourself.</p>
                                  </TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                            </div>
                          </div>
                          <div v-if="hasVehicles" class="flex gap-2 pt-1">
                            <Button type="button" variant="outline" size="sm" @click="cancelAddVehicle">Cancel</Button>
                          </div>
                        </div>
                      </div>
                    </Transition>
                  </div>

                  <div class="public-attest-card space-y-3 text-sm p-4" style="color:#dde4f0">
                <p class="font-semibold" style="color:#a8c5ec">As a member who is willing and able to carpool other members for
                  this hike, you attest that:</p>
                <ul class="list-disc list-inside space-y-1">
                  <li>You have a valid driver's license.</li>
                  <li>You have insurance.</li>
                  <li>Your vehicle is in working condition and is safe to operate.</li>
                </ul>
                <p>Additionally, if you have to cancel for whatever reason as a driver, you promise to return to this
                  link and cancel your signup.</p>
              </div>
                  <div class="space-y-2">
                    <Label for="confirm-name" class="font-semibold text-midnight">Print your name below to confirm that you
                      understand.</Label>
                    <Input id="confirm-name" type="text" v-model="driverConfirmationName"
                           :placeholder="`Type '${name}' to confirm`"/>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </CardContent>
        <CardFooter v-if="!loading && !signupSuccess && !alreadySigned && !error" class="p-6 pt-0">
          <Button class="w-full bg-uci-blue text-lg font-semibold text-white hover:bg-uci-blue/90"
                  :disabled="!allowSubmit"
                  @click="submitForm"
          >
            Submit
          </Button>
        </CardFooter>
      </Card>
    </div>
  </section>
</template>