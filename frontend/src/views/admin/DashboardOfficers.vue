<script setup>
import OfficersTable from "@/components/admin/OfficersTable.vue";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card/index.js";
</script>

<template>
  <section class="p-6">
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <CardTitle class="text-2xl">Officers</CardTitle>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>
      <CardContent>
        <OfficersTable/>
      </CardContent>
    </Card>
  </section>
</template>
