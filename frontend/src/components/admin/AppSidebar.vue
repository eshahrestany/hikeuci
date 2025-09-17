<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  type SidebarProps,
  SidebarRail,
} from '@/components/ui/sidebar'
import ThemeToggle from "@/components/admin/ThemeToggle.vue";
import {useRouter} from 'vue-router';


const props = defineProps<SidebarProps>()
const router = useRouter();
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
    <SidebarRail />
  </Sidebar>
</template>
