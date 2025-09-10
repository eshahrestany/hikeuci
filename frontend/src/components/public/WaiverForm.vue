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

const loading = ref(true)
const error = ref(null)
const tokenRef = ref(null)
const waiverContent = ref(null)

const sig1HasInk = ref(false)
const sig2HasInk = ref(false)
const signaturesTouched = computed(() => sig1HasInk.value && sig2HasInk.value)

const allowSubmit = computed(() => signaturesTouched.value && !!printName.value)

const signature1 = ref(null)
const signature2 = ref(null)
const isMinor = ref(false)
const age = ref(17)
const printName = ref(null)

const submitSuccess = ref(false)

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
              ref: targetRef,       // your existing signature1 / signature2 refs
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
          h('p', {class: 'text-xs text-stone-600'}, 'Signature of User or Parent/Guardian if Minor')
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
          placeholder: 'Print Name',
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
      throw new Error('You have already signed this waiver. Thank you!')
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

</script>

<template>
  <section
      class="relative bg-cover bg-center py-20 bg-fixed"
      :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <div class="absolute inset-0"/>
    <div class="relative mx-auto w-fit min-w-2xl px-2">
      <Card class="bg-white border">
        <CardContent class="p-6 pt-0">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
          </div>
          <div v-else-if="error" class="text-red-500 text-center">
            {{ error }}
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
</template>