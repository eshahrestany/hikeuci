<script setup lang="ts">
import SearchForm from '@/components/SearchForm.vue'
import VersionSwitcher from '@/components/VersionSwitcher.vue'

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

const props = defineProps<SidebarProps>()

// This is sample data.
const data = {
  navMain: [
    {
      items: [
        {
          title: 'Home',
          url: '#',
        },
        {
          title: 'Manage Members',
          url: '#',
        },
        {
          title: 'Manage Trails',
          url: '#',
        },
        {
          title: 'Hike History',
          url: '#',
        },
      ],
    },
  ],
}
</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup v-for="item in data.navMain">
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="childItem in item.items" :key="childItem.title">
              <SidebarMenuButton as-child :is-active="childItem.isActive">
                <a :href="childItem.url">{{ childItem.title }}</a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarRail />
  </Sidebar>
</template>
