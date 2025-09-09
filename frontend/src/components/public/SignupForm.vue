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
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select/index.js";
import { SPhoneInput } from "@/components/ui/phone-input";
import { PlusCircle } from "lucide-vue-next";
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from "@/components/ui/tooltip/index.js";

const props = defineProps({
  title: {
    type: String,
    default: 'Event Signup'
  },
})

const hikeTitle = ref(props.title)
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
    }
    else if (jsonResponse.status === "ready") {
      const data = jsonResponse.formData
      console.log(data)
      name.value = data.name
      email.value = data.email
      phoneNumber.value = data.tel || ''
      phoneNumberAlreadySet.value = !!data.tel
      phoneTouched.value = !!data.tel

      vehicles.value = jsonResponse.vehicles || []
      hikeTitle.value = jsonResponse.hike.title
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
    <div class="absolute inset-0"/>
    <div class="relative mx-auto max-w-2xl px-4">
      <Card class="bg-white border">
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
            <h1 class="text-center text-3xl font-bold text-uci-blue tracking-tight sm:text-4xl font-montserrat">
              {{ hikeTitle }}
            </h1>
          </template>
        </CardHeader>
        <CardContent class="p-6 pt-0">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
          </div>
          <div v-else-if="error" class="text-red-500 text-center">
            {{ error }}
          </div>
          <div v-else-if="signupSuccess" class="text-center text-stone-700">
            <p class="text-lg font-medium">You have succesfully signed up for this hike.</p>
            <p class="text-sm text-stone-600 mt-2">You can return to this link before the signup deadline to cancel if needed.</p>
          </div>
          <div v-else-if="alreadySigned" class="text-center text-stone-700">
            <p v-if="cancelSuccess">Successfully canceled.</p>
            <p v-else class="text-lg font-medium">
              You have already signed up for this event. If you need to cancel your signup, please click the button below.
            </p>
            <p class="text-sm text-stone-600 mt-2">You can still re-sign up for the hike before the signup submission deadline.</p>
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
              <Input v-if="phoneNumber" v-model="phoneNumber" disabled/>
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
            <div v-if="isDriver" class="border-t border-stone-200 pt-6 space-y-6">
              <!-- Vehicle Input (dynamic) -->
              <div class="space-y-4">
                <!-- Existing vehicles: choose one -->
                <div v-if="hasVehicles" class="grid grid-cols-2">
                  <div class="space-y-2">
                    <Label for="vehicleSelect" class="font-semibold text-midnight">Choose your vehicle</Label>
                    <Select v-model="selectedVehicleId" :disabled="addingNewVehicle">
                      <SelectTrigger id="vehicleSelect">
                        <SelectValue placeholder="Select Vehicle…"/>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem v-for="v in vehicles" :key="v.id" :value="v.id">
                          {{ v.description || `${v.year} ${v.make} ${v.model}` }}
                          ({{ v.passenger_seats }} passengers)
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div class="space-y-2">
                    <Label for="vehicleSelect" class="font-semibold text-midnight">Or add a new one</Label>
                    <Button class="items-center" type="button" variant="outline" @click="startAddVehicle">
                      <PlusCircle/>
                      Add new vehicle
                    </Button>
                  </div>
                </div>

                <!-- New vehicle form -->
                <div v-if="!hasVehicles || addingNewVehicle" class="space-y-2">
                  <p v-if="!hasVehicles" class="text-sm text-stone-600">
                    We don’t have a vehicle on file for you yet. Add one below:
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
                    <div class="max-w-[80px] min-w-[120px]">
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
                            <p class="text-sm">This number represents the number of passengers you can carry, not including yourself.</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                  </div>
                </div>
                <div class="flex gap-2" v-if="hasVehicles && addingNewVehicle">
                  <Button type="button" variant="secondary" @click="cancelAddVehicle">Cancel</Button>
                </div>
              </div>

              <div class="space-y-3 text-sm text-stone-700 p-4 bg-stone-100 rounded-lg">
                <p class="font-semibold text-midnight">As a member who is willing and able to carpool other members for
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