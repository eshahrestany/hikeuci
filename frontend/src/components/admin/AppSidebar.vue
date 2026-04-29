<script setup>
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import ThemeToggle from '@/components/admin/ThemeToggle.vue'
import SignedInAs from '@/components/admin/SignedInAs.vue'
import {
  Mountain,
  Compass,
  Users,
  Route,
  BarChart3,
  Mail,
  ShieldCheck,
  LogOut,
} from 'lucide-vue-next'
import { computed } from 'vue'
import { useAuth } from '@/lib/auth.js'

const { state, signOut } = useAuth()

const props = defineProps()

const navItems = computed(() => [
  { title: 'Current Hike',    route: { name: 'Dashboard' },          icon: Compass },
  { title: 'Members',         route: { name: 'Dashboard Members' },  icon: Users },
  { title: 'Trails',          route: { name: 'Dashboard Trails' },   icon: Route },
  { title: 'Hike History',    route: { name: 'Dashboard History' },  icon: BarChart3 },
  { title: 'Emails',          route: { name: 'Dashboard Emails' },   icon: Mail },
  ...(state.user?.is_owner
    ? [{ title: 'Officers', route: { name: 'Dashboard Officers' }, icon: ShieldCheck }]
    : []),
])
</script>

<template>
  <Sidebar v-bind="props">
    <!-- Brand header -->
    <div class="admin-sidebar-brand">
      <div class="admin-brand-icon">
        <Mountain class="h-[18px] w-[18px] text-midnight" />
      </div>
      <div class="admin-brand-text">
        <span class="admin-brand-name">HikeUCI</span>
        <span class="admin-brand-sub">Admin</span>
      </div>
    </div>

    <!-- Navigation -->
    <SidebarContent class="pt-1">
      <SidebarGroup>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in navItems" :key="item.title">
              <SidebarMenuButton as-child size="default">
                <router-link :to="item.route" class="flex items-center gap-2.5 w-full">
                  <component :is="item.icon" class="h-4 w-4 shrink-0 opacity-70" />
                  <span class="text-sm">{{ item.title }}</span>
                </router-link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <!-- Footer -->
    <div class="admin-sidebar-footer">
      <SignedInAs :user="state.user" />

      <!-- Actions row -->
      <div class="admin-footer-actions">
        <ThemeToggle />
        <Button
          variant="ghost"
          size="sm"
          class="flex-1 justify-start gap-2 h-8 text-muted-foreground hover:text-foreground hover:bg-accent text-xs font-medium transition-all"
          @click="signOut()"
        >
          <LogOut class="h-3.5 w-3.5" />
          Sign out
        </Button>
      </div>
    </div>

    <SidebarRail />
  </Sidebar>
</template>
