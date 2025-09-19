<script setup>
import MembersTable from "@/components/admin/MembersTable.vue";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card/index.js";
import {Skeleton} from "@/components/ui/skeleton/index.js";
</script>

<template>
  <section class="p-6">
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <CardTitle class="text-2xl">Members</CardTitle>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>
      <CardContent>
        <MembersTable/>
      </CardContent>
    </Card>
  </section>
</template>


