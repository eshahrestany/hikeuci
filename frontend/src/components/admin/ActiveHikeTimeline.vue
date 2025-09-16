<script setup>
import { computed } from 'vue'

const props = defineProps({
  hasVote: { type: Boolean, required: true },
  currentPhase: { type: String, required: true }, // "awaiting_vote_start" | "voting" | "signup" | "waiver" | "hike"
  timestamps: { type: Object, required: true }    // { vote_date?, signup_date, waiver_date, hike_date }
})

function formatDate(d) {
  if (!d) return '—'
  const date = d instanceof Date ? d : new Date(d)
  return date.toLocaleString(undefined, {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

// Build labels dynamically depending on hasVote
const steps = computed(() => {
  if (props.hasVote) {
    return [
      { key: 'voting', label: 'Vote Initiated', at: props.timestamps.vote_date },
      { key: 'signup', label: 'Signup Opens',   at: props.timestamps.signup_date },
      { key: 'waiver', label: 'Waiver Opens',   at: props.timestamps.waiver_date },
      { key: 'hike',   label: 'Hike Day',       at: props.timestamps.hike_date },
    ]
  } else {
    return [
      { key: 'signup', label: 'Hike Initiated', at: props.timestamps.signup_date },
      { key: 'waiver', label: 'Waiver Opens',   at: props.timestamps.waiver_date },
      { key: 'hike',   label: 'Hike Day',       at: props.timestamps.hike_date },
    ]
  }
})

// Figure out where we are in the flow
const indicatorIndex = computed(() => {
  const idx = steps.value.findIndex(s => s.key === props.currentPhase)
  return idx === -1 ? 0 : idx
})
</script>

<template>
  <div class="flex flex-col space-y-6">
    <div class="flex items-start justify-between relative gap-4 sm:gap-8">
      <!-- horizontal connector line -->
      <div class="absolute top-3 left-0 right-0 h-0.5 bg-gray-300"></div>

      <div v-for="(step, idx) in steps" :key="step.key" class="flex-1 flex flex-col items-center relative z-10">
        <!-- Circle indicator -->
        <div
          class="w-6 h-6 rounded-full flex items-center justify-center"
          :class="[
            idx < indicatorIndex ? 'bg-green-500 text-white' :
            idx === indicatorIndex ? 'bg-blue-500 text-white' :
            'bg-gray-300 text-gray-600'
          ]"
        >
          {{ idx + 1 }}
        </div>
        <!-- Label + timestamp -->
        <span class="mt-3 text-sm font-medium text-center px-2">{{ step.label }}</span>
        <span class="text-xs text-gray-500 text-center px-2">{{ formatDate(step.at) }}</span>
      </div>
    </div>
  </div>
</template>
