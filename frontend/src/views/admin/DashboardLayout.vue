<script setup lang="ts">

import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {SidebarInset, SidebarProvider, SidebarTrigger} from "@/components/ui/sidebar";
import {Button} from "@/components/ui/button";
import AppSidebar from "@/components/admin/AppSidebar.vue";
import VotingPhase from "@/components/admin/VotingPhase.vue";
import SignupPhase from "@/components/admin/SignupPhase.vue";
import {Skeleton} from "@/components/ui/skeleton";
import WaiverPhase from "@/components/admin/WaiverPhase.vue";
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarTrigger />
    <SidebarInset>
      <router-view />
    </SidebarInset>
  </SidebarProvider>
</template>


<style scoped>

</style>