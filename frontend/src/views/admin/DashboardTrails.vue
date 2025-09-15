<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/lib/auth.js'
import TrailsTable from "@/components/admin/TrailsTable.vue";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card/index.js";
import {SidebarInset, SidebarProvider, SidebarTrigger} from "@/components/ui/sidebar/index.js";
import AppSidebar from "@/components/admin/AppSidebar.vue";
import {Skeleton} from "@/components/ui/skeleton/index.js";
import TrailsForm from "@/components/admin/TrailsForm.vue";

const { state: signOut, fetchWithAuth } = useAuth()
const router = useRouter()

const loading = ref(true)
const response = ref([])

async function loadTrails() {
  loading.value = true
  try {
    const res = await fetchWithAuth('/admin/trails')
    response.value = await res.json()
    console.info(response.value)
  } catch {
      console.log( "error")
    response.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadTrails)
</script>

<template>
  <section class="p-6">
    <h1 class="text-3xl text-white font-bold mb-3">HikeUCI Dashboard Trails</h1>
    <hr class="h-px mb-8 bg-gray-200 border-0 dark:bg-gray-700" />
    <Card class="mx-auto space-y-6">
      <CardHeader>
        <CardTitle class="text-2xl">Trails</CardTitle>
        <hr class="h-px bg-gray-200 border-0 dark:bg-gray-700" />
      </CardHeader>
      <CardContent>
        <!-- Loading Skeleton -->
        <div v-if="loading">
          <Skeleton class="h-6 w-3/5 mb-4" />
          <Skeleton class="space-y-2">
            <Skeleton class="h-4 w-full" />
            <Skeleton class="h-4 w-4/5" />
            <Skeleton class="h-4 w-2/3" />
          </Skeleton>
        </div>
        <TrailsForm :is-open="false"/>
        <TrailsTable :trails-data="response"/>

      </CardContent>
    </Card>
  </section>
</template>


