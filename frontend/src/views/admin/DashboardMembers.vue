<script setup>
import MembersTable from "@/components/admin/MembersTable.vue";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ExportEmailButton from "@/components/admin/ExportEmailButton.vue";
import { Users } from 'lucide-vue-next'
</script>

<template>
  <section class="p-4 md:p-6">
    <Card class="mx-auto">
      <CardHeader class="pb-3">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Users class="h-5 w-5 text-primary" />
          </div>
          <div class="flex-1">
            <CardTitle class="text-xl">Members</CardTitle>
            <p class="text-xs text-muted-foreground mt-0.5">Manage club membership roster</p>
          </div>
          <ExportEmailButton mode="all"/>
        </div>
      </CardHeader>
      <hr class="h-px mx-6 bg-border border-0" />
      <CardContent class="pt-5">
        <MembersTable/>
      </CardContent>
    </Card>
  </section>
</template>
