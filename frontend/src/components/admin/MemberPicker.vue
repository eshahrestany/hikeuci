<script setup>
import { computed } from 'vue'
import {
  Combobox, ComboboxAnchor, ComboboxInput,
  ComboboxList, ComboboxItem, ComboboxItemIndicator,
  ComboboxGroup, ComboboxEmpty,
} from '@/components/ui/combobox'
import { Check, Search } from 'lucide-vue-next'
import { cn } from '@/lib/utils.js'

const props = defineProps({
  modelValue: { type: Object, default: null },
  options: { type: Array, required: true }, // [{ member_id, name, email }]
  placeholder: { type: String, default: 'Search by name or email...' },
  emptyMessage: { type: String, default: 'No members found.' },
})
const emit = defineEmits(['update:modelValue'])

const enriched = computed(() =>
  props.options.map(o => ({
    ...o,
    value: o.email,
    label: `${o.name} (${o.email})`,
    searchText: `${o.name} ${o.email}`.toLowerCase(),
  }))
)

function filterMembers(options, term) {
  const q = term.toLowerCase()
  return options.filter(o => o.searchText.includes(q))
}
</script>

<template>
  <Combobox
    by="email"
    :model-value="modelValue"
    :filter-function="filterMembers"
    @update:model-value="(v) => emit('update:modelValue', v)"
  >
    <ComboboxAnchor class="w-full">
      <div class="relative w-full items-center">
        <ComboboxInput
          class="pl-9"
          :display-value="(val) => val ? `${val.name} (${val.email})` : ''"
          :placeholder="placeholder"
        />
        <span class="absolute start-0 inset-y-0 flex items-center justify-center px-3">
          <Search class="size-4 text-muted-foreground" />
        </span>
      </div>
    </ComboboxAnchor>
    <ComboboxList>
      <ComboboxEmpty>{{ emptyMessage }}</ComboboxEmpty>
      <ComboboxGroup>
        <ComboboxItem v-for="opt in enriched" :key="opt.member_id" :value="opt">
          <span>{{ opt.name }} <span class="text-muted-foreground">({{ opt.email }})</span></span>
          <ComboboxItemIndicator>
            <Check :class="cn('ml-auto h-4 w-4')" />
          </ComboboxItemIndicator>
        </ComboboxItem>
      </ComboboxGroup>
    </ComboboxList>
  </Combobox>
</template>
