<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <p class="font-semibold text-xl">
        Current Phase: <Badge class="text-md">Waiver</Badge>
      </p>
    </div>

    <CardHeader class="flex items-start">
      <div class="basis-1/2">
        <img
          class="w-1/2 object-cover rounded-md"
          :src="`/api/images/uploads/${waiverData.trail_id}.png`"
          :alt="waiverData.trail_name"
        />
      </div>
      <div class="flex-1">
        <CardTitle class="mb-4">{{ waiverData.trail_name }}</CardTitle>
        <SignupStats
          :users="waiverData.users"
          :passenger-capacity="waiverData.passenger_capacity"
        />
      </div>
    </CardHeader>

    <WaiverTable :waiver-data="props.waiverData"/>
  </div>
</template>

<script setup>
import {ref, computed, h, onMounted, watch, shallowRef} from 'vue'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table'
import { useVueTable, getCoreRowModel, getFilteredRowModel } from '@tanstack/vue-table'
import { FlexRender } from '@tanstack/vue-table'
import {Check, ChevronsUpDown, Edit, MailPlus, Search, Trash} from "lucide-vue-next";
import { useAuth } from "@/lib/auth.js"
import { toast } from "vue-sonner";
import EditUserSignup from "@/components/admin/EditUserSignup.vue";
import SignupStats from "@/components/admin/SignupStats.vue";
import {CardHeader, CardTitle} from "@/components/ui/card/index.js";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter
} from '@/components/ui/dialog'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { PlusCircle } from 'lucide-vue-next'
import AddLateSignup from '@/components/admin/AddLateSignup.vue'
import WaiverTable from "@/components/admin/WaiverTable.vue";

const { postWithAuth } = useAuth()

const props = defineProps({waiverData: { type: Object, required: true }})

</script>
