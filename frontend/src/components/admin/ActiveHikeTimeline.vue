<script setup>
import { computed } from 'vue'
import { Check } from 'lucide-vue-next'

const props = defineProps({
  hasVote:      { type: Boolean, required: true },
  currentPhase: { type: String,  required: true },
  timestamps:   { type: Object,  required: true },
})

function formatDate(d) {
  if (!d) return '—'
  const date = d instanceof Date ? d : new Date(d)
  return date.toLocaleString(undefined, {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const steps = computed(() => {
  if (props.hasVote) {
    return [
      { key: 'voting', label: 'Vote',    at: props.timestamps.vote_date },
      { key: 'signup', label: 'Signup',  at: props.timestamps.signup_date },
      { key: 'waiver', label: 'Waiver',  at: props.timestamps.waiver_date },
      { key: 'hike',   label: 'Hike Day',at: props.timestamps.hike_date },
    ]
  }
  return [
    { key: 'signup', label: 'Signup',   at: props.timestamps.signup_date },
    { key: 'waiver', label: 'Waiver',   at: props.timestamps.waiver_date },
    { key: 'hike',   label: 'Hike Day', at: props.timestamps.hike_date },
  ]
})

const indicatorIndex = computed(() => {
  const idx = steps.value.findIndex(s => s.key === props.currentPhase)
  return idx === -1 ? 0 : idx
})
</script>

<template>
  <div class="relative select-none">
    <!-- Connector track -->
    <div
      class="absolute top-3.5 h-px bg-border"
      style="left: calc(100% / var(--steps) / 2); right: calc(100% / var(--steps) / 2);"
      :style="{ '--steps': steps.length }"
      aria-hidden="true"
    />

    <div class="relative flex justify-between gap-2">
      <div
        v-for="(step, idx) in steps"
        :key="step.key"
        class="flex flex-1 flex-col items-center gap-2"
      >
        <!-- Step indicator -->
        <div
          class="relative z-10 flex h-7 w-7 items-center justify-center rounded-full ring-4 transition-all duration-300"
          :class="[
            idx < indicatorIndex
              ? 'bg-green-500 ring-green-500/15 dark:ring-green-900/60'
              : idx === indicatorIndex
              ? 'bg-primary ring-primary/15 dark:ring-primary/20'
              : 'bg-muted ring-background border border-border',
          ]"
        >
          <Check
            v-if="idx < indicatorIndex"
            class="h-3.5 w-3.5 text-white"
            :stroke-width="2.5"
          />
          <div
            v-else-if="idx === indicatorIndex"
            class="h-2.5 w-2.5 rounded-full bg-white"
          />
          <div
            v-else
            class="h-2 w-2 rounded-full bg-muted-foreground/30"
          />
        </div>

        <!-- Label + timestamp -->
        <div class="flex flex-col items-center text-center gap-0.5">
          <span
            class="text-xs font-semibold leading-tight"
            :class="idx <= indicatorIndex ? 'text-foreground' : 'text-muted-foreground'"
          >{{ step.label }}</span>
          <span class="text-[11px] leading-tight text-muted-foreground">
            {{ formatDate(step.at) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
