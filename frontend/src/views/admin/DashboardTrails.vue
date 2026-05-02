<script setup>
import TrailsTable from "@/components/admin/TrailsTable.vue";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin } from 'lucide-vue-next'
</script>

<template>
  <section class="p-4 md:p-6">
    <Card class="mx-auto">
      <CardHeader class="pb-3">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <MapPin class="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle class="text-xl">Trails</CardTitle>
            <p class="text-xs text-muted-foreground mt-0.5">Manage trail catalog</p>
          </div>
        </div>
      </CardHeader>
      <hr class="h-px mx-6 bg-border border-0" />
      <CardContent class="pt-5">
        <TrailsTable/>
      </CardContent>
    </Card>
  </section>
</template>
