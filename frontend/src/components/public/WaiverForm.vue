<script setup>
import {Card, CardContent} from "@/components/ui/card/index.js"
import {Skeleton} from "@/components/ui/skeleton/index.js"
import backgroundImage from '@/assets/hiking_bg.jpg'
import {onMounted, ref, createApp, nextTick, h, computed, watch} from "vue";
import {VueSignaturePad} from '@selemondev/vue3-signature-pad'
import {
  NumberField,
  NumberFieldContent,
  NumberFieldInput,
  NumberFieldIncrement,
  NumberFieldDecrement
} from "@/components/ui/number-field/index.js";
import {Button} from "@/components/ui/button/index.js";
import {Input} from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog/index.js";
import {Checkbox} from "@/components/ui/checkbox/index.js";
import {Label} from "@/components/ui/label/index.js";

const loading = ref(true)
const error = ref(null)
const tokenRef = ref(null)
const waiverContent = ref(null)

const sig1HasInk = ref(false)
const sig2HasInk = ref(false)
const signaturesTouched = computed(() => sig1HasInk.value && sig2HasInk.value)

const allowSubmit = computed(() => signaturesTouched.value && !!printName.value && agreePolicy.value)

const signature1 = ref(null)
const signature2 = ref(null)
const isMinor = ref(false)
const agreePolicy = ref(false)
const age = ref(17)
const printName = ref(null)

const submitSuccess = ref(false)
const alreadySigned = ref(false)
const cancelSuccess = ref(false)

const cancelDialogOpen = ref(false)
const confirmCancelChecked = ref(false)

function mountESignSlots() {
  // helper to replace a slot with a mounted VueSignaturePad + Clear button
  const mountSig = (slotId, targetRef, inkFlagRef) => {
    const oldEl = document.getElementById(slotId)
    if (!oldEl) return
    const mountPoint = document.createElement('div')
    oldEl.replaceWith(mountPoint)

    const app = createApp({
      setup() {
        const handleClear = () => {
          targetRef?.value?.clearCanvas?.()
          inkFlagRef.value = false
        }
        return {handleClear}
      },
      render() {
        return h('div', {class: 'space-y-1'}, [
          h('div', {class: 'relative w-[240px] h-[80px] border border-stone-400'}, [
            h(VueSignaturePad, {
              ref: targetRef,
              maxWidth: 1,
              onBeginStroke: () => {
                inkFlagRef.value = true
              },
              onEndStroke: () => {
                inkFlagRef.value = !targetRef?.value?.isEmpty?.()
              }
            }),
            h('button', {
              type: 'button',
              class: 'absolute top-1 right-1 px-2 py-1 text-xs bg-white border border-stone-300 rounded-md shadow-sm hover:bg-stone-50',
              onClick: this.handleClear
            }, 'Clear')
          ]),
          h('p', {class: 'text-xs text-stone-600'},
              ['Signature of User or Parent/Guardian if Minor',
                      // Required Indicator
                      h('span', {
                        'aria-hidden': 'true',
                        class: 'ml-2 text-xs font-medium text-rose-600'
                      }, '* Required')]),
        ])
      }
    })
    app.mount(mountPoint)
  }

  // Signature pads (use your existing refs: signature1 / signature2)
  mountSig('esign-slot-1', signature1, sig1HasInk)
  mountSig('esign-slot-2', signature2, sig2HasInk)

  // Print name (plain text input)
  const printNameSlot = document.getElementById('print-name-slot')
  if (printNameSlot) {
    const app = createApp({
      setup() {
        return {printName}
      },
      render() {
        return h(Input, {
          id: 'printName',
          placeholder: 'Print Name (required)',
          modelValue: this.printName,
          'onUpdate:modelValue': (n) => (this.printName = n),
        })
      }
    })
    app.mount(printNameSlot)
  }

  // isMinor checkbox and age input
  const ageSlot = document.getElementById('age-input-slot')
  if (ageSlot) {
    const mountPoint = document.createElement('div')
    ageSlot.replaceWith(mountPoint)

    const app = createApp({
      setup() {
        const toggle = (e) => {
          const el = e.target
          isMinor.value = !!el.checked
        }
        const onUpdate = (v) => (age.value = v)
        return {isMinor, age, toggle, onUpdate}
      },
      render() {
        return h('div', {class: 'flex items-center gap-4'}, [
          // Checkbox: v-model="isMinor"
          h('label', {class: 'flex items-center gap-2 text-sm text-midnight'}, [
            h('input', {
              type: 'checkbox',
              checked: this.isMinor,
              onChange: this.toggle,
              class: 'h-4 w-4 rounded border-stone-300'
            }),
            h('span', 'Participant is Minor (under 18)')
          ]),
          // NumberField shown only if isMinor === true
          this.isMinor
              ? h('div', {class: 'flex items-center gap-2'}, [
                h('span', {class: 'text-sm text-stone-600'}, 'Age'),
                h(
                    NumberField,
                    {
                      id: 'age',
                      class: 'w-[80px]',
                      modelValue: this.age,
                      'onUpdate:modelValue': this.onUpdate,
                      min: 0,
                      max: 17,
                      defaultValue: 17
                    },
                    {
                      default: () =>
                          h(NumberFieldContent, null, {
                            default: () => [
                              h(NumberFieldDecrement),
                              h(NumberFieldInput),
                              h(NumberFieldIncrement)
                            ]
                          })
                    }
                )
              ])
              : null
        ])
      }
    })
    app.mount(mountPoint)
  }

  const policySlot = document.getElementById('policy-slot')
  if (policySlot) {
    const mountPoint = document.createElement('div')
    policySlot.replaceWith(mountPoint)

    const app = createApp({
      setup() {
        const toggle = (e) => {
          const el = e.target
          agreePolicy.value = !!el.checked
        }
        const onUpdate = (v) => (age.value = v)
        return { agreePolicy, toggle, onUpdate }
      },
      render() {
        return h('div', { class: 'flex items-center gap-4' }, [
          // Checkbox: v-model="agreePolicy" (required)
          h('label', { class: 'flex items-center gap-2 text-sm text-midnight' }, [
            h('input', {
              id: 'agree-policy',
              type: 'checkbox',
              checked: this.agreePolicy,
              onChange: this.toggle,
              class: 'h-4 w-4 rounded border-stone-300',
              required: true,
            }),
            h('span', { class: 'gap-1' }, [
              "I have read and agree to the Hiking Club at UCI ",
              h("a", { href: "/privacy-policy", target: "_blank" }, "Privacy Policy"),
              " and ",
              h("a", { href: "/esign-policy", target: "_blank" }, "Electronic Records and Signatures Policy."),
              // Screen-reader hint
              h('span', { id: 'agree-policy-required', class: 'sr-only' }),
              h('div', {
              'aria-hidden': 'true',
              class: 'block text-xs font-medium text-rose-600'
            }, '* Required')
            ])
          ])
        ])
      }
    })
    app.mount(mountPoint)
  }
}


function getSignatureDataURL(sigRef) {
  const api = sigRef?.value
  if (!api) return null
  if (typeof api.isEmpty === 'function' && api.isEmpty()) return null
  const url = api.saveSignature?.()
  return typeof url === 'string' ? url : null
}

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

    const res = await fetch(`/api/hike-waiver?token=${token}`)
    if (!res.ok) {
      let errMessage = `HTTP error! status: ${res.status}`
      try {
        const errData = await res.json()
        errMessage = errData.error || errMessage
      } catch (e) {
        // ignore JSON parse errors
      }
      throw new Error(errMessage)
    }
    const jsonResponse = await res.json()

    if (jsonResponse.status === 'ready') {
      waiverContent.value = jsonResponse.content
    } else if (jsonResponse.status === 'signed') {
      alreadySigned.value = true
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
  await nextTick()
  mountESignSlots()
})

async function submitForm() {
  const signature_1_data = getSignatureDataURL(signature1)
  const signature_2_data = getSignatureDataURL(signature2)

  const payload = {
    name: printName.value,
    is_minor: isMinor.value,
    signature1: signature_1_data,
    signature2: signature_2_data
  }
  if (isMinor.value) payload.age = age.value

  try {
    loading.value = true
    error.value = null

    const res = await fetch(`/api/hike-waiver?token=${tokenRef.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      let errMessage = `HTTP error! status: ${res.status}`
      try {
        const errData = await res.json()
        errMessage = errData.error || errMessage
      } catch {}
      throw new Error(errMessage)
    }

    const jsonResponse = await res.json()
    if (jsonResponse.success) {
      submitSuccess.value = true
    } else {
      throw new Error(jsonResponse.error || 'Unknown error occurred')
    }
  } catch (e) {
    error.value = e.message || 'Submission failed'
  } finally {
    loading.value = false
  }
}

async function submitCancelRequest() {
  try {
    loading.value = true
    error.value = null

    const res = await fetch(`/api/hike-waiver/cancel?token=${tokenRef.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })

    if (!res.ok) {
      let errMessage = `HTTP error! status: ${res.status}`
      try {
        const errData = await res.json()
        errMessage = errData.error || errMessage
      } catch {}
      throw new Error(errMessage)
    }

    const jsonResponse = await res.json()
    if (jsonResponse.success) {
      cancelSuccess.value = true
    } else {
      throw new Error(jsonResponse.error || 'Unknown error occurred')
    }
  } catch (e) {
    error.value = e.message || 'Request failed'
  } finally {
    loading.value = false
  }
}

async function confirmCancelAction() {
  await submitCancelRequest()
  cancelDialogOpen.value = false
  confirmCancelChecked.value = false
}

watch(cancelDialogOpen, (isOpen) => {
  if (!isOpen) {
    confirmCancelChecked.value = false
  }
})

</script>

<template>
  <section
      class="relative bg-cover bg-center py-20 bg-fixed flex-grow place-content-center"
      :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <div class="absolute inset-0"/>
    <div class="relative mx-auto w-fit px-2">
      <Card class="relative bg-white border">
        <Button
          v-if="waiverContent && !loading && !error && !submitSuccess && !cancelSuccess"
          size="sm"
          variant="outline"
          class="absolute top-3 right-3 z-10 shadow-md border-red-500 text-red-600 hover:bg-red-50"
          aria-label="Changed your mind? Open cancellation dialog"
          @click="cancelDialogOpen = true"
        >
          Changed your mind?
        </Button>
        <CardContent class="px-6 py-2">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
          </div>
          <div v-else-if="error" class="text-red-500 text-center">
            {{ error }}
          </div>
          <div v-else-if="submitSuccess" class="text-center">
            Your waiver has been submitted successfully. See you there!
          </div>
          <div v-else-if="cancelSuccess" class="text-center">
            Successfully canceled.
          </div>
          <div v-else-if="alreadySigned" class="text-center text-stone-700">
            <p v-if="cancelSuccess">Successfully canceled.</p>
            <p v-else class="text-lg font-medium">
              You have already submitted your waiver. If you need to cancel, please click the button below.
            </p>
            <p class="text-sm text-red-500 mt-2">By cancelling you will be forfeiting your spot and won't be able to sign back up!</p>
            <div v-if="!cancelSuccess" class="mt-6">
              <Button type="button" variant="destructive" @click="cancelDialogOpen = true">Cancel My Signup</Button>
            </div>
          </div>
          <div v-else class="space-y-6">
            <div v-html="waiverContent" class="prose max-w-none"></div>
            <div class="text-center">
              <Button class="w-full bg-uci-blue text-lg font-semibold text-white hover:bg-uci-blue/90"
                      :disabled="!allowSubmit"
                      @click="submitForm">
                Submit
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </section>

  <Dialog v-model:open="cancelDialogOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Cancel Signup?</DialogTitle>
        <DialogDescription>
          By cancelling you will be forfeiting your spot and won't be able to sign back up!
        </DialogDescription>
      </DialogHeader>
      <div class="flex items-center gap-2 py-2">
        <Checkbox id="confirm-cancel" v-model="confirmCancelChecked"/>
        <Label for="confirm-cancel">I understand and still want to cancel my signup.</Label>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="cancelDialogOpen = false">Nevermind</Button>
        <Button
          variant="destructive"
          :disabled="!confirmCancelChecked || loading"
          @click="confirmCancelAction"
        >
          Cancel my signup
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>