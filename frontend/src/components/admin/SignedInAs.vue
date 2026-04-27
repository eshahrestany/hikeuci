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
    class="flex items-center gap-2.5 rounded-md border border-sidebar-border/60 bg-sidebar-accent/40 px-2 py-1.5"
  >
    <div
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-uci-gold to-amber-600 text-[11px] font-semibold text-black shadow-sm ring-1 ring-black/5"
      aria-hidden="true"
    >
      {{ initials }}
    </div>
    <div class="min-w-0 flex-1 leading-tight">
      <div v-if="name" class="truncate text-sm font-medium text-sidebar-foreground">
        {{ name }}
      </div>
      <div
        v-if="email"
        :title="email"
        class="truncate text-xs text-sidebar-foreground/60"
      >
        {{ email }}
      </div>
    </div>
  </div>
</template>
