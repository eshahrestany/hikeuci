<script setup>
import { computed, ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import {
  Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList,
} from '@/components/ui/command'
import { CheckIcon, ChevronsUpDownIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils.js'

const props = defineProps({
  hikes: { type: Array, required: true },
  modelValue: { type: [Number, null], default: null },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)

function formatHikeDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

function hikeLabel(h) {
  const d = formatHikeDate(h.hike_date)
  return h.trail_name ? `${d} · ${h.trail_name}` : d
}

const selected = computed(() => props.hikes.find(h => h.id === props.modelValue) || null)
const selectedLabel = computed(() => selected.value ? hikeLabel(selected.value) : 'Select a hike…')

function onSelect(id) {
  emit('update:modelValue', id)
  open.value = false
}
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        role="combobox"
        :aria-expanded="open"
        class="w-[320px] justify-between"
      >
        <span class="truncate">{{ selectedLabel }}</span>
        <ChevronsUpDownIcon class="opacity-50 shrink-0" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[320px] p-0">
      <Command>
        <CommandInput class="h-9" placeholder="Search hikes…" />
        <CommandList>
          <CommandEmpty>No hikes found.</CommandEmpty>
          <CommandGroup>
            <CommandItem
              v-for="h in hikes"
              :key="h.id"
              :value="hikeLabel(h)"
              @select="onSelect(h.id)"
            >
              <span class="truncate">{{ hikeLabel(h) }}</span>
              <CheckIcon
                :class="cn('ml-auto', modelValue === h.id ? 'opacity-100' : 'opacity-0')"
              />
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>
