<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: { type: Object, default: null },
})

const name = computed(() => props.user?.name || null)
const email = computed(() => props.user?.email || null)

const initials = computed(() => {
  if (!name.value) return email.value?.[0]?.toUpperCase() || '?'
  const parts = name.value.trim().split(/\s+/)
  const first = parts[0]?.[0] || ''
  const last = parts.length > 1 ? parts[parts.length - 1][0] : ''
  return (first + last).toUpperCase()
})

const hasIdentity = computed(() => !!(name.value || email.value))
</script>

<template>
  <div
    v-if="hasIdentity"
    class="flex items-center gap-2.5 rounded-lg border border-sidebar-border bg-sidebar-accent/30 px-2.5 py-2"
  >
    <div
      class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-uci-gold to-amber-500 text-[10px] font-bold text-midnight shadow-sm ring-1 ring-black/10"
      aria-hidden="true"
    >
      {{ initials }}
    </div>
    <div class="min-w-0 flex-1 leading-tight">
      <div v-if="name" class="truncate text-xs font-semibold text-sidebar-foreground">
        {{ name }}
      </div>
      <div
        v-if="email"
        :title="email"
        class="truncate text-[11px] text-sidebar-foreground/50"
      >
        {{ email }}
      </div>
    </div>
  </div>
</template>
