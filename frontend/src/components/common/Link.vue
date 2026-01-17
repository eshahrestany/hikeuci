<script setup>
import { ExternalLink } from 'lucide-vue-next'

defineProps({
  to: { type: String, required: true },
  text: { type: String, required: true },
  size: { type: Number, default: 16 },
  newTab: {type: Boolean, default: false}
})
</script>

<template>
  <a
    :href="to"
    class="inline-flex items-center gap-1 text-blue-400 hover:underline cursor-pointer"
    :style="{ fontSize: `${size}px` }"
    :target="newTab ? '_blank' : undefined"
  >
    {{ text }}
    <ExternalLink :size="size" />
  </a>
</template>
