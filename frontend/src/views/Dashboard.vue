<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarTrigger>…</SidebarTrigger>
    <SidebarInset>…</SidebarInset>
  </SidebarProvider>

  <section class=""></section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuth } from '../lib/auth.js'
import NavBar from "../components/Navbar.vue"
import Footer from "../components/Footer.vue"

const router = useRouter()
const { state: authState, signOut, fetchWithAuth } = useAuth()

import AppSidebar from '@/components/AppSidebar.vue'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar'

function signOutAndReturn() {
  signOut()
  router.replace('/login')
}

async function testExampleRoute() {
  try {
    const res = await fetchWithAuth('/api/example/upcoming')
    const info = await res.json()
    console.log(info)
  } catch (e) {
    console.error(e.message)
  }
}
</script>

<style scoped>

</style> 