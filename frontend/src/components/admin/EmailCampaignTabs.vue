<script setup>
import { computed } from 'vue'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'

const TYPE_ORDER = ['voting', 'signup', 'waiver', 'waitlist']
const TYPE_LABEL = { voting: 'Voting', signup: 'Signup', waiver: 'Waiver', waitlist: 'Waitlist' }

const props = defineProps({
  campaigns: { type: Array, required: true },
  modelValue: { type: String, default: null },
})
const emit = defineEmits(['update:modelValue'])

const ordered = computed(() => {
  const byType = new Map(props.campaigns.map(c => [c.type, c]))
  return TYPE_ORDER.filter(t => byType.has(t)).map(t => byType.get(t))
})
</script>

<template>
  <Tabs
    :model-value="modelValue"
    @update:model-value="(v) => emit('update:modelValue', v)"
  >
    <TabsList>
      <TabsTrigger v-for="c in ordered" :key="c.type" :value="c.type">
        <span>{{ TYPE_LABEL[c.type] }}</span>
        <Badge variant="secondary" class="ml-2">{{ c.counts.total }}</Badge>
        <Badge
          v-if="c.in_progress"
          variant="outline"
          class="ml-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
        >
          In progress
        </Badge>
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
