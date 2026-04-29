<script setup>
import TrailsTable from "@/components/admin/TrailsTable.vue";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card/index.js";
</script>

<template>
  <section class="p-4 md:p-6">
    <Card class="mx-auto">
      <CardHeader>
        <CardTitle>Trails</CardTitle>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>
      <CardContent>
        <TrailsTable/>
      </CardContent>
    </Card>
  </section>
</template>


