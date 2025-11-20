<script setup>
import MembersTable from "@/components/admin/MembersTable.vue";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card/index.js";
import ExportEmailButton from "@/components/admin/ExportEmailButton.vue";
</script>

<template>
  <section class="p-6">
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <div class="inline-flex">
          <CardTitle class="text-2xl">Members</CardTitle>
          <ExportEmailButton mode="all" class="ml-auto"/>
        </div>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>
      <CardContent>
        <MembersTable/>
      </CardContent>
    </Card>
  </section>
</template>


