<template>
  <div>
    <p class="flex justify-center items-center font-semibold text-xl mb-2">
      Current Phase:
      <Badge class="text-md ml-2">Voting</Badge>
    </p>
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Card v-for="trail in votingData.trails" :key="trail.trail_id">
        <CardHeader>
          <img
            class="h-24 w-full object-cover rounded-md mb-2"
            :src="`/api/images/uploads/${trail.trail_id}`"
            :alt="trail.trail_name"
          />
          <CardTitle>{{ trail.trail_name }}</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-sm mb-1">
            Votes:
            {{ trail.trail_num_votes }}
            ({{ votePercentage(trail) }}%)
          </p>
          <Progress :v-model="votePercentsRef[trail]" class="mb-2" />
          <Button
            variant="outline"
            class="mb-2 p-0"
            @click="showVoters[trail.trail_id] = !showVoters[trail.trail_id]"
          >
            <ChevronDown v-if="showVoters[trail.trail_id]" />
            <ChevronRight v-else />
            {{
              showVoters[trail.trail_id]
                ? 'Hide Votes'
                : 'See Votes'
            }}
          </Button>
          <ul
            v-if="showVoters[trail.trail_id]"
            class="list-disc list-inside text-sm space-y-1"
          >
            <li
              v-for="(name, idx) in trail.trail_voters"
              :key="idx"
            >
              {{ name }}
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ChevronDown, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  votingData: { type: Object, required: true }
})

const showVoters = reactive({})
const totalVotes = computed(() =>
  props.votingData.trails.reduce((sum, c) => sum + c.trail_num_votes, 0)
)

const votePercentsRef = ref({})
props.votingData.trails.forEach((trail) => {
  votePercentsRef.value[trail] = votePercentage(trail)
})

function votePercentage(trail) {
  if (totalVotes.value === 0) return 0
  return ((trail.trail_num_votes / totalVotes.value) * 100).toFixed(1)
}
</script>
