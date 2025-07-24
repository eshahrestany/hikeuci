<script setup>
import { ref, computed } from 'vue'
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

// Hardcoded user data for now
const name = ref('Peter Anteater')
const email = ref('peter.anteater@uci.edu')
const phoneNumber = ref('123-456-7890')
const transportation = ref('arrange-own')
const driverConfirmationName = ref('')

const isDriver = computed(() => transportation.value === 'can-drive')
const isDriverConfirmed = computed(() => {
  return isDriver.value ? driverConfirmationName.value === name.value : true
})

const parsedDescription = computed(() => {
  return marked(props.description)
})
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
          <h1
            class="text-center text-3xl font-bold text-uci-blue tracking-tight sm:text-4xl font-montserrat"
          >
            {{ title }}
          </h1>
          <div
            class="prose prose-sm max-w-none mt-4 text-left text-base leading-relaxed text-midnight/90"
            v-html="parsedDescription"
          />
        </CardHeader>
        <CardContent class="p-6 pt-0">
          <div class="space-y-6">
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div class="space-y-2">
                <Label for="name" class="font-semibold text-midnight">Name</Label>
                <Input
                  id="name"
                  type="text"
                  :value="name"
                  disabled
                />
              </div>
              <div class="space-y-2">
                <Label for="email" class="font-semibold text-midnight">Email</Label>
                <Input
                  id="email"
                  type="email"
                  :value="email"
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
              />
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
                    >I will arrange my own transportation to the event.</Label
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
                    <Label for="passengers" class="font-semibold text-midnight">How many people are you able to bring to the hike, not including yourself?</Label>
                    <Input id="passengers" type="number" min="1" />
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
        <CardFooter class="p-6 pt-0">
          <Button class="w-full bg-uci-blue text-lg font-semibold text-white hover:bg-uci-blue/90" :disabled="!isDriverConfirmed">
            Submit
          </Button>
        </CardFooter>
      </Card>
    </div>
  </section>
</template> 