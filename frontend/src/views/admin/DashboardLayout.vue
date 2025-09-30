<script setup>

import {SidebarInset, SidebarProvider} from "@/components/ui/sidebar";
import AppSidebar from "@/components/admin/AppSidebar.vue";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const pageTitle = computed(() => route.meta.title || 'HikeUCI Dashboard')

</script>

<template>
  <SidebarProvider>
    <AppSidebar/>
    <SidebarInset>
      <div class="px-3 py-4 md:p-6">
        <h1 class="text-2xl md:text-4xl font-extrabold flex items-center gap-2">
          <SidebarTrigger/>
          {{ pageTitle }}
        </h1>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700"/>
      </div>
      <router-view/>
    </SidebarInset>
  </SidebarProvider>
</template>