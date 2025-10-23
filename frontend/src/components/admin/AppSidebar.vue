<script setup>
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar'
import { Button } from "@/components/ui/button"
import ThemeToggle from "@/components/admin/ThemeToggle.vue";
import { LogOut } from 'lucide-vue-next'
import { useAuth } from '@/lib/auth.js'
const { signOut } = useAuth()

const props = defineProps()
const data = {
  navMain: [
    {
      items: [
        {
          title: 'Home',
          route: {name: 'Dashboard'},
        },
        {
          title: 'Manage Members',
          route: {name: 'Dashboard Members'},
        },
        {
          title: 'Manage Trails',
          route: {name: 'Dashboard Trails'},
        },
        {
          title: 'Hike History',
          route: {name: 'Dashboard History'},
        },
      ],
    },
  ],
}
</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <div class="w-fit"><ThemeToggle/></div>
    </SidebarHeader>

    <SidebarContent>
      <SidebarGroup v-for="item in data.navMain">
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="childItem in item.items" :key="childItem.title">
              <SidebarMenuButton as-child :is-active="childItem.isActive">
                <router-link :to="childItem.route">{{ childItem.title }}</router-link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton as-child>
            <Button variant="ghost" @click="signOut()">
              <LogOut class="h-4 w-4"/>
              <span>Sign out</span>
            </Button>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>

    <SidebarRail/>
  </Sidebar>
</template>
