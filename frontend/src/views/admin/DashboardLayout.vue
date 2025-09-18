<script setup lang="ts">

import {SidebarInset, SidebarProvider} from "@/components/ui/sidebar";
import AppSidebar from "@/components/admin/AppSidebar.vue";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const pageTitle = computed(() => (route.meta.title as string) || 'HikeUCI Dashboard')

</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <div class="px-3 py-4 sm:p-6">
        <h1 class="text-3xl text-white font-bold flex items-center gap-2">
          <SidebarTrigger class="text-white" />
          {{ pageTitle }}
        </h1>
        <hr class="h-px mb-8 bg-gray-200 border-0 dark:bg-gray-700" />
      </div>
      <router-view />
    </SidebarInset>
  </SidebarProvider>
</template>


<style scoped>

</style>