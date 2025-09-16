<script setup>
import MembersTable from "@/components/admin/MembersTable.vue";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card/index.js";
import {Skeleton} from "@/components/ui/skeleton/index.js";
</script>

<template>
  <section class="p-6">
    <h1 class="text-3xl text-white font-bold mb-3">HikeUCI Dashboard Members</h1>
    <hr class="h-px mb-8 bg-gray-200 border-0 dark:bg-gray-700" />
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <CardTitle class="text-2xl">Members</CardTitle>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>
      <CardContent>
        <!-- Loading Skeleton -->
        <div v-if="loading">
          <Skeleton class="h-6 w-3/5 mb-4" />
          <Skeleton class="space-y-2">
            <Skeleton class="h-4 w-full" />
            <Skeleton class="h-4 w-4/5" />
            <Skeleton class="h-4 w-2/3" />
          </Skeleton>
        </div>

        <MembersTable />

      </CardContent>
    </Card>
  </section>
</template>


