<script setup>
import { ref, computed, onMounted } from 'vue'
import { marked } from 'marked'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Button } from '@/components/ui/button'
import backgroundImage from '@/assets/hiking_bg.jpg'
import {NumberField, NumberFieldContent, NumberFieldInput, NumberFieldIncrement, NumberFieldDecrement} from "@/components/ui/number-field/index.js";
import { Skeleton } from '@/components/ui/skeleton'
import { parsePhoneNumberFromString } from 'libphonenumber-js'

const props = defineProps({
  title: {
    type: String,
    default: 'Event Signup'
  },
  description: {
    type: String,
    default: 'Fill out the form below to sign up for the event.'
  }
})

const parsedDescription = computed(() => {
  return marked(props.description)
})

const hikeTitle = ref(props.title)
const hikeDescription = ref(props.description)
const parsedHikeDescription = computed(() => marked(hikeDescription.value))

// Add loading and error refs after parsedDescription
const loading = ref(true)
const error = ref(null)

// Replace the fetch block (lines around 38-64) with onMounted fetch logic
onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    const params = new URLSearchParams(window.location.search)
    const token = params.get("token")
    if (!token) {
      throw new Error("No token provided in URL")
    }
    const res = await fetch(`/api/hike-signup?token=${token}`)
    if (!res.ok) {
      let errMessage = `HTTP error! status: ${res.status}`
      try {
        const errData = await res.json()
        errMessage = errData.error || errMessage
      } catch {}
      throw new Error(errMessage)
    }
    const jsonResponse = await res.json()

    if (jsonResponse.formData === null) {
      const status = jsonResponse.status
      let message = status || 'Data is null'
      if (status === 'not_found') {
        message = 'The signup link you visited is invalid. The token provided does not exist. Please check your email for the correct link or contact the club for assistance.'
      }
      throw new Error(message)
    }
    const data = jsonResponse.formData
    name.value = data.name
    email.value = data.email
    phoneNumber.value = data.tel || ''
    phoneTouched.value = !!data.tel

    if (jsonResponse.hike) {
      hikeTitle.value = jsonResponse.hike.title
      hikeDescription.value = jsonResponse.hike.description
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

// Update refs to initialize empty
const name = ref('')
const email = ref('')
const phoneNumber = ref('')

const transportation = ref('arrange-own')
const driverConfirmationName = ref('')

const isDriver = computed(() => transportation.value === 'can-drive')
const isDriverConfirmed = computed(() => {
  return isDriver.value ? driverConfirmationName.value.toLowerCase() === name.value.toLowerCase() : true
})

// After phoneNumber ref add validation logic
const phoneTouched = ref(false)
const e164Phone = computed(() => {
  const input = phoneNumber.value
  if (!input) return null
  const parsed = parsePhoneNumberFromString(input, 'US')
  return parsed && parsed.isValid() ? parsed.format('E.164') : null
})
const isPhoneValid = computed(() => !!e164Phone.value)
</script>

<template>
  <section
    class="relative bg-cover bg-center py-20 bg-fixed"
    :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <div class="absolute inset-0" />
    <div class="relative mx-auto max-w-2xl px-4">
      <Card class="bg-white border">
        <CardHeader class="p-6">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-9 w-3/4 mx-auto" />
            <div class="space-y-2">
              <Skeleton class="h-4 w-full" />
              <Skeleton class="h-4 w-full" />
              <Skeleton class="h-4 w-2/3" />
            </div>
          </div>
          <template v-else>
            <h1
              class="text-center text-3xl font-bold text-uci-blue tracking-tight sm:text-4xl font-montserrat"
            >
              {{ hikeTitle }}
            </h1>
            <div
              class="prose prose-sm max-w-none mt-4 text-left text-base leading-relaxed text-midnight/90"
              v-html="parsedHikeDescription"
            />
          </template>
        </CardHeader>
        <CardContent class="p-6 pt-0">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-4 w-full" />
            <Skeleton class="h-4 w-full" />
            <Skeleton class="h-4 w-full" />
          </div>
          <div v-else-if="error" class="text-red-500 text-center">
            {{ error }}
          </div>
          <div v-else class="space-y-6">
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div class="space-y-2">
                <Label for="name" class="font-semibold text-midnight">Name</Label>
                <Input
                  id="name"
                  type="text"
                  v-model="name"
                  disabled
                />
              </div>
              <div class="space-y-2">
                <Label for="email" class="font-semibold text-midnight">Email</Label>
                <Input
                  id="email"
                  type="email"
                  v-model="email"
                  disabled
                />
              </div>
            </div>
            <div class="space-y-2">
              <Label for="phone" class="font-semibold text-midnight">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                v-model="phoneNumber"
                placeholder="e.g., (123) 456-7890"
                @blur="phoneTouched = true"
              />
            </div>
            <div v-if="phoneTouched && !isPhoneValid" class="text-red-500 text-sm mt-1">
              Please enter a valid phone number. Country codes are allowed (e.g., +1 (123) 456-7890).
            </div>
            <div class="space-y-3 pt-2">
              <Label class="font-semibold text-midnight"
                >Are you interested in getting after-hike food?</Label
              >
              <RadioGroup default-value="no" class="flex items-center gap-6">
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="food-yes" value="yes" />
                  <Label for="food-yes" class="font-normal">Yes</Label>
                </div>
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="food-no" value="no" />
                  <Label for="food-no" class="font-normal">No</Label>
                </div>
              </RadioGroup>
            </div>
            <div class="space-y-3 pt-2">
              <Label class="font-semibold text-midnight"
                >How do you plan on getting to the event?</Label
              >
              <RadioGroup v-model="transportation" default-value="arrange-own" class="grid gap-3">
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="drive-yes" value="can-drive" />
                  <Label for="drive-yes" class="font-normal"
                    >I can drive and I am willing to transport other members</Label
                  >
                </div>
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="drive-no" value="need-ride" />
                  <Label for="drive-no" class="font-normal"
                    >I do not have my own transportation and need to carpool with other
                    members</Label
                  >
                </div>
                <div class="flex items-center gap-2">
                  <RadioGroupItem id="drive-self" value="arrange-own" />
                  <Label for="drive-self" class="font-normal"
                    >I will arrange my own transportation to the trailhead.</Label
                  >
                </div>
              </RadioGroup>
            </div>

            <!-- Dynamic Driver Section -->
            <div v-if="isDriver" class="border-t border-stone-200 pt-6 space-y-6">
                 <div class="space-y-2">
                    <Label for="vehicle" class="font-semibold text-midnight">What is the year, make, and model of your vehicle?</Label>
                    <Input id="vehicle" type="text" placeholder="e.g., 2022 Toyota Camry" />
                </div>
                <div class="space-y-2">
                  <NumberField id="passengers" :default-value="1" :min="1">
                    <Label for="passengers" class="font-semibold text-midnight">How many people are you able to bring to the hike, not including yourself?</Label>
                      <NumberFieldContent class="max-w-1/4">
                        <NumberFieldDecrement />
                        <NumberFieldInput />
                        <NumberFieldIncrement />
                      </NumberFieldContent>
                  </NumberField>
                </div>
                <div class="space-y-3 text-sm text-stone-700 p-4 bg-stone-100 rounded-lg">
                    <p class="font-semibold text-midnight">As a member who is willing and able to carpool other members for this hike, you attest that:</p>
                    <ul class="list-disc list-inside space-y-1">
                        <li>You have a valid driver's license.</li>
                        <li>You have insurance.</li>
                        <li>Your vehicle is in working condition and is safe to operate.</li>
                    </ul>
                    <p>Additionally, if you have to cancel for whatever reason as a driver, you promise to inform the club through email, discord, or instagram as soon as possible.</p>
                </div>
                 <div class="space-y-2">
                    <Label for="confirm-name" class="font-semibold text-midnight">Print your name below to confirm that you understand.</Label>
                    <Input id="confirm-name" type="text" v-model="driverConfirmationName" :placeholder="`Type '${name}' to confirm`" />
                </div>
            </div>
          </div>
        </CardContent>
        <CardFooter v-if="!loading && !error" class="p-6 pt-0">
          <Button class="w-full bg-uci-blue text-lg font-semibold text-white hover:bg-uci-blue/90" :disabled="!isDriverConfirmed || !isPhoneValid">
            Submit
          </Button>
        </CardFooter>
      </Card>
    </div>
  </section>
</template> 