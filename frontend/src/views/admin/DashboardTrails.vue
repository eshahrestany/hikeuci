<script setup>
import TrailsTable from "@/components/admin/TrailsTable.vue";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card/index.js";
</script>

<template>
  <section class="p-6">
    <h1 class="text-3xl text-white font-bold mb-3">HikeUCI Dashboard Trails</h1>
    <hr class="h-px mb-8 bg-gray-200 border-0 dark:bg-gray-700" />
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <CardTitle class="text-2xl">Trails</CardTitle>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>
      <CardContent>
        <TrailsTable/>
      </CardContent>
    </Card>
  </section>
</template>


