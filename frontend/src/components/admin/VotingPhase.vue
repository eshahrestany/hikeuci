<template>
  <div>
    <p class="font-semibold text-xl mb-2">
      Current Phase: <Badge class="text-md">Voting</Badge>
    </p>
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Card v-for="candidate in votingData.candidates" :key="candidate.candidate_id">
        <CardHeader>
          <img
            class="h-24 w-full object-cover rounded-md mb-2"
            :src="`/api/images/uploads/${candidate.trail_id}.png`"
            :alt="candidate.trail_name"
          />
          <CardTitle>{{ candidate.trail_name }}</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-sm mb-1">
            Votes:
            {{ candidate.candidate_num_votes }}
            ({{ votePercentage(candidate) }}%)
          </p>
          <Progress :value="parseFloat(votePercentage(candidate))" class="mb-2" />
          <Button
            variant="outline"
            class="mb-2 p-0"
            @click="showVoters[candidate.candidate_id] = !showVoters[candidate.candidate_id]"
          >
            <ChevronDown v-if="showVoters[candidate.candidate_id]" />
            <ChevronRight v-else />
            {{
              showVoters[candidate.candidate_id]
                ? 'Hide Votes'
                : 'See Votes'
            }}
          </Button>
          <ul
            v-if="showVoters[candidate.candidate_id]"
            class="list-disc list-inside text-sm space-y-1"
          >
            <li
              v-for="(name, idx) in candidate.candidate_voters"
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
import { reactive, computed } from 'vue'
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
  props.votingData.candidates.reduce((sum, c) => sum + c.candidate_num_votes, 0)
)

function votePercentage(candidate) {
  if (totalVotes.value === 0) return 0
  return ((candidate.candidate_num_votes / totalVotes.value) * 100).toFixed(1)
}
</script>
