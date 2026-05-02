<script setup>
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import AppSidebar from "@/components/admin/AppSidebar.vue"
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const pageTitle = computed(() => route.meta.title || 'Dashboard')

onMounted(() => document.body.classList.add('admin-layout'))
onUnmounted(() => document.body.classList.remove('admin-layout'))
</script>

<template>
  <div class="admin-layout">
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset class="min-w-0 overflow-x-hidden">
        <header class="admin-page-header">
          <SidebarTrigger
            class="h-8 w-8 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-all duration-150"
          />
          <div class="h-4 w-px bg-border" aria-hidden="true" />
          <span class="text-sm font-semibold text-foreground/75 tracking-tight">{{ pageTitle }}</span>
        </header>
        <router-view />
      </SidebarInset>
    </SidebarProvider>
  </div>
</template>
