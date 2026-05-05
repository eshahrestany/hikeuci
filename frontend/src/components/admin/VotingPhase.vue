<template>
  <div class="space-y-5">
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="trail in votingData.trails"
        :key="trail.trail_id"
        class="group relative overflow-hidden rounded-xl border bg-card shadow-sm transition-shadow hover:shadow-md flex flex-col"
      >
        <!-- Trail image -->
        <div class="relative h-36 shrink-0 overflow-hidden bg-muted">
          <img
            class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            :src="`/api/images/uploads/${trail.trail_id}`"
            :alt="trail.trail_name"
          />
          <!-- Vote count chip -->
          <div class="absolute top-2 right-2 rounded-full bg-black/60 px-2.5 py-1 text-xs font-semibold text-white backdrop-blur-sm">
            {{ trail.trail_num_votes }} vote{{ trail.trail_num_votes !== 1 ? 's' : '' }}
          </div>
        </div>

        <!-- Card body -->
        <div class="p-4 flex flex-col flex-1 gap-3">
          <div>
            <h3 class="font-semibold text-sm leading-tight">{{ trail.trail_name }}</h3>
            <div class="flex items-center gap-3 mt-1 flex-wrap">
              <Link v-if="trail.trail_alltrails_url" :to="trail.trail_alltrails_url" text="AllTrails" :new-tab="true" :size="12"/>
              <RouterLink :to="{ name: 'Trail Detail', params: { trailId: String(trail.trail_id) } }" class="text-xs text-blue-400 hover:underline">Trail info</RouterLink>
            </div>
          </div>

          <!-- Progress -->
          <div class="mt-auto space-y-1.5">
            <div class="flex items-center justify-between text-xs text-muted-foreground">
              <span>Vote share</span>
              <span class="font-medium tabular-nums">{{ votePercentage(trail) }}%</span>
            </div>
            <Progress :model-value="Number(votePercentage(trail))" class="h-2" />
          </div>

          <!-- Voter list toggle -->
          <button
            class="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            @click="showVoters[trail.trail_id] = !showVoters[trail.trail_id]"
          >
            <ChevronDown
              class="h-3.5 w-3.5 transition-transform duration-200"
              :class="showVoters[trail.trail_id] ? 'rotate-0' : '-rotate-90'"
            />
            {{ showVoters[trail.trail_id] ? 'Hide voters' : 'Show voters' }}
          </button>

          <ul
            v-if="showVoters[trail.trail_id]"
            class="space-y-1 border-t pt-2"
          >
            <li
              v-for="(name, idx) in trail.trail_voters"
              :key="idx"
              class="text-xs text-muted-foreground pl-1"
            >
              {{ name }}
            </li>
            <li v-if="!trail.trail_voters.length" class="text-xs text-muted-foreground italic pl-1">No votes yet</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { Progress } from '@/components/ui/progress'
import { ChevronDown } from 'lucide-vue-next'
import Link from "@/components/common/Link.vue"

const props = defineProps({
  votingData: { type: Object, required: true }
})

const showVoters = reactive({})
const totalVotes = computed(() =>
  props.votingData.trails.reduce((sum, c) => sum + c.trail_num_votes, 0)
)

function votePercentage(trail) {
  if (totalVotes.value === 0) return 0
  return ((trail.trail_num_votes / totalVotes.value) * 100).toFixed(1)
}
</script>
