<script setup>
import DifficultyBadge from './DifficultyBadge.vue'
import ElevationChart from './ElevationChart.vue'

defineProps({
  trail: { type: Object, default: null }
})
</script>

<template>
  <div v-if="trail" class="space-y-3 py-3 border-b" style="border-color: rgba(255,255,255,0.12)">
    <div class="flex flex-wrap gap-2 items-center">
      <DifficultyBadge :difficulty="trail.difficulty" />
      <div class="rounded-lg px-3 py-1.5 border text-sm" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12);">
        <span class="text-xs uppercase tracking-wide mr-1" style="color:#9aa6bb">Length</span>
        <span class="font-semibold" style="color:#f5f7fb">{{ trail.length_mi != null ? `${Number(trail.length_mi).toFixed(1)} mi` : '—' }}</span>
      </div>
      <div class="rounded-lg px-3 py-1.5 border text-sm" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12);">
        <span class="text-xs uppercase tracking-wide mr-1" style="color:#9aa6bb">Est. time</span>
        <span class="font-semibold" style="color:#f5f7fb">{{ trail.estimated_time_hr != null ? `${trail.estimated_time_hr} hr` : '—' }}</span>
      </div>
      <div class="rounded-lg px-3 py-1.5 border text-sm" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12);">
        <span class="text-xs uppercase tracking-wide mr-1" style="color:#9aa6bb">Water</span>
        <span class="font-semibold" style="color:#f5f7fb">{{ trail.required_water_liters != null ? `${trail.required_water_liters} L` : '—' }}</span>
      </div>
      <div v-if="trail.elevation_gain_ft != null" class="rounded-lg px-3 py-1.5 border text-sm" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12);">
        <span class="text-xs uppercase tracking-wide mr-1" style="color:#9aa6bb">Elev. gain</span>
        <span class="font-semibold" style="color:#f5f7fb">{{ trail.elevation_gain_ft.toLocaleString() }} ft</span>
      </div>
    </div>
    <ElevationChart v-if="trail.elevation_data" :elevationData="trail.elevation_data" />
  </div>
</template>
