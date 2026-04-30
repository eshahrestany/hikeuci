<script setup>
import OfficersTable from "@/components/admin/OfficersTable.vue";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield } from 'lucide-vue-next'
</script>

<template>
  <section class="p-4 md:p-6">
    <Card class="mx-auto">
      <CardHeader class="pb-3">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Shield class="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle class="text-xl">Officers</CardTitle>
            <p class="text-xs text-muted-foreground mt-0.5">Manage admin access and ownership</p>
          </div>
        </div>
      </CardHeader>
      <hr class="h-px mx-6 bg-border border-0" />
      <CardContent class="pt-5">
        <OfficersTable/>
      </CardContent>
    </Card>
  </section>
</template>
