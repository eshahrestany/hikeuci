<script setup>

import {Badge} from "@/components/ui/badge";

const props = defineProps({
  difficulty: {
    type: Number,
    required: true
  }
})

const difficulties = {
  0: { label: 'Easy', style: 'bg-green-500 text-white' },
  1: { label: 'Moderate', style: 'bg-yellow-500 text-white' },
  2: { label: 'Difficult',  style: 'bg-orange-500 text-white' },
  3: { label: 'Very Difficult', style: 'bg-red-500 text-white' },
}
</script>

<template>
  <Badge
    :class="difficulties[props.difficulty]?.style || 'bg-gray-500 text-white'"
  >
    {{ difficulties[props.difficulty]?.label }}
  </Badge>
</template>