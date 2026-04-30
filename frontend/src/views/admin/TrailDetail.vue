<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useColorMode } from '@vueuse/core'
import { useAuth } from '@/lib/auth.js'
import { toast } from 'vue-sonner'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  NumberField, NumberFieldContent,
  NumberFieldDecrement, NumberFieldInput, NumberFieldIncrement,
} from '@/components/ui/number-field'
import {
  Dialog, DialogContent, DialogDescription,
  DialogFooter, DialogHeader, DialogTitle,
} from '@/components/ui/dialog'
import ElevationChart from '@/components/common/ElevationChart.vue'
import DifficultyBadge from '@/components/common/DifficultyBadge.vue'

import {
  ArrowLeft, MapPin, Save, Trash2, TriangleAlert,
  ImagePlus, BarChart2, ExternalLink,
} from 'lucide-vue-next'

const props = defineProps({ trailId: { type: String, required: true } })

const router = useRouter()
const { fetchWithAuth, getAuthHeaders } = useAuth()
const colorMode = useColorMode()
const dark = computed(() => colorMode.value === 'dark')

const loading = ref(true)
const saving = ref(false)
const deleting = ref(false)
const deleteOpen = ref(false)
const trail = ref(null)

const difficultyOptions = [
  { value: 0, label: 'Easy' },
  { value: 1, label: 'Moderate' },
  { value: 2, label: 'Difficult' },
  { value: 3, label: 'Very Difficult' },
]

const form = reactive({
  name: '',
  location: '',
  length_mi: 0,
  estimated_time_hr: 0,
  required_water_liters: 0,
  driving_distance_mi: null,
  difficulty: 1,
  alltrails_url: '',
  trailhead_gmaps_url: '',
  trailhead_amaps_url: '',
  description: '',
})

const selectedPhotoFile = ref(null)
const selectedElevationFile = ref(null)
const elevationData = ref(null)

async function load() {
  loading.value = true
  try {
    const res = await fetchWithAuth(`/api/admin/trails/${props.trailId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    trail.value = await res.json()
    Object.assign(form, trail.value)

    if (trail.value.has_elevation_data) {
      const elRes = await fetchWithAuth(`/api/admin/trails/${props.trailId}/elevation`)
      if (elRes.ok) {
        const elData = await elRes.json()
        elevationData.value = elData.elevation_data
      }
    }
  } catch (e) {
    toast.error('Failed to load trail')
    router.replace({ name: 'Dashboard Trails' })
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    const res = await fetchWithAuth(`/api/admin/trails/${props.trailId}`, {
      method: 'PUT',
      body: JSON.stringify(form),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    trail.value = await res.json()

    if (selectedPhotoFile.value) {
      const fd = new FormData()
      fd.append('file', selectedPhotoFile.value)
      await fetch(`/api/images/uploads/${props.trailId}`, {
        method: 'POST',
        headers: { ...getAuthHeaders() },
        body: fd,
      })
      selectedPhotoFile.value = null
    }

    if (selectedElevationFile.value) {
      const fd = new FormData()
      fd.append('file', selectedElevationFile.value)
      const elRes = await fetch(`/api/admin/trails/${props.trailId}/elevation`, {
        method: 'POST',
        headers: { ...getAuthHeaders() },
        body: fd,
      })
      if (elRes.ok) {
        const elData = await fetchWithAuth(`/api/admin/trails/${props.trailId}/elevation`)
        if (elData.ok) elevationData.value = (await elData.json()).elevation_data
      }
      selectedElevationFile.value = null
    }

    toast.success('Trail saved')
  } catch (e) {
    toast.error('Failed to save trail')
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  deleting.value = true
  try {
    const res = await fetchWithAuth(`/api/admin/trails/${props.trailId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    toast.success('Trail deleted')
    router.push({ name: 'Dashboard Trails' })
  } catch (e) {
    toast.error('Failed to delete trail — it may be referenced by an active hike')
    deleteOpen.value = false
  } finally {
    deleting.value = false
  }
}

const imageUrl = computed(() => `/api/images/uploads/${props.trailId}?t=${Date.now()}`)

onMounted(load)
</script>

<template>
  <section class="p-4 md:p-6 space-y-6">
    <!-- Loading skeleton -->
    <template v-if="loading">
      <Skeleton class="h-9 w-48" />
      <Skeleton class="h-56 w-full rounded-xl" />
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Skeleton class="h-10 w-full" v-for="n in 6" :key="n" />
      </div>
    </template>

    <template v-else-if="trail">
      <!-- Page header -->
      <div class="flex items-center gap-3">
        <Button variant="ghost" size="icon" class="shrink-0" @click="router.push({ name: 'Dashboard Trails' })">
          <ArrowLeft class="h-4 w-4" />
        </Button>
        <div class="flex-1 min-w-0">
          <h1 class="text-xl font-semibold truncate">{{ trail.name }}</h1>
          <p class="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
            <MapPin class="h-3 w-3" />{{ trail.location }}
          </p>
        </div>
        <DifficultyBadge :difficulty="trail.difficulty" />
      </div>

      <!-- Hero image -->
      <div class="relative h-52 md:h-64 rounded-xl overflow-hidden bg-muted border">
        <img
          :src="imageUrl"
          :alt="trail.name"
          class="h-full w-full object-cover"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
        <label
          class="absolute bottom-3 right-3 flex items-center gap-1.5 cursor-pointer rounded-lg bg-black/60 px-3 py-1.5 text-xs text-white hover:bg-black/80 transition-colors backdrop-blur-sm"
        >
          <ImagePlus class="h-3.5 w-3.5" />
          Replace image
          <input type="file" accept="image/png,image/jpeg" class="hidden" @change="e => selectedPhotoFile = e.target.files[0]" />
        </label>
        <div v-if="selectedPhotoFile" class="absolute bottom-3 left-3 rounded-lg bg-primary/90 px-3 py-1.5 text-xs text-primary-foreground">
          {{ selectedPhotoFile.name }}
        </div>
      </div>

      <!-- Form -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main form col (2/3 width) -->
        <div class="lg:col-span-2 space-y-6">

          <!-- Basic info -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-base">Basic Info</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="space-y-1.5">
                  <Label for="name" class="text-xs font-medium text-muted-foreground">Trail Name</Label>
                  <Input id="name" v-model="form.name" placeholder="e.g., Tenaja Falls" />
                </div>
                <div class="space-y-1.5">
                  <Label for="location" class="text-xs font-medium text-muted-foreground">Location</Label>
                  <Input id="location" v-model="form.location" placeholder="e.g., Cleveland National Forest" />
                </div>
                <div class="space-y-1.5 sm:col-span-2">
                  <Label for="difficulty" class="text-xs font-medium text-muted-foreground">Difficulty</Label>
                  <Select v-model="form.difficulty">
                    <SelectTrigger id="difficulty">
                      <SelectValue placeholder="Select difficulty" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem v-for="opt in difficultyOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Stats -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-base">Trail Stats</CardTitle>
            </CardHeader>
            <CardContent class="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div class="space-y-1.5">
                <Label class="text-xs font-medium text-muted-foreground">Length (mi)</Label>
                <NumberField v-model="form.length_mi" :min="0" :step="0.1">
                  <NumberFieldContent>
                    <NumberFieldDecrement /><NumberFieldInput /><NumberFieldIncrement />
                  </NumberFieldContent>
                </NumberField>
              </div>
              <div class="space-y-1.5">
                <Label class="text-xs font-medium text-muted-foreground">Est. Time (hrs)</Label>
                <NumberField v-model="form.estimated_time_hr" :min="0" :step="0.25">
                  <NumberFieldContent>
                    <NumberFieldDecrement /><NumberFieldInput /><NumberFieldIncrement />
                  </NumberFieldContent>
                </NumberField>
              </div>
              <div class="space-y-1.5">
                <Label class="text-xs font-medium text-muted-foreground">Water (liters)</Label>
                <NumberField v-model="form.required_water_liters" :min="0" :step="0.5">
                  <NumberFieldContent>
                    <NumberFieldDecrement /><NumberFieldInput /><NumberFieldIncrement />
                  </NumberFieldContent>
                </NumberField>
              </div>
              <div class="space-y-1.5">
                <Label class="text-xs font-medium text-muted-foreground">Drive (mi)</Label>
                <NumberField v-model="form.driving_distance_mi" :min="0" :step="0.1">
                  <NumberFieldContent>
                    <NumberFieldDecrement /><NumberFieldInput /><NumberFieldIncrement />
                  </NumberFieldContent>
                </NumberField>
              </div>
            </CardContent>
          </Card>

          <!-- Links -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-base">Links</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="space-y-1.5">
                <Label class="text-xs font-medium text-muted-foreground">AllTrails URL</Label>
                <div class="relative">
                  <Input v-model="form.alltrails_url" type="url" placeholder="https://www.alltrails.com/…" class="pr-9" />
                  <a v-if="form.alltrails_url" :href="form.alltrails_url" target="_blank" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                    <ExternalLink class="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
              <div class="space-y-1.5">
                <Label class="text-xs font-medium text-muted-foreground">Google Maps Trailhead</Label>
                <div class="relative">
                  <Input v-model="form.trailhead_gmaps_url" type="url" placeholder="https://maps.app.goo.gl/…" class="pr-9" />
                  <a v-if="form.trailhead_gmaps_url" :href="form.trailhead_gmaps_url" target="_blank" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                    <ExternalLink class="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
              <div class="space-y-1.5">
                <Label class="text-xs font-medium text-muted-foreground">Apple Maps Trailhead</Label>
                <div class="relative">
                  <Input v-model="form.trailhead_amaps_url" type="url" placeholder="https://maps.apple.com/…" class="pr-9" />
                  <a v-if="form.trailhead_amaps_url" :href="form.trailhead_amaps_url" target="_blank" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                    <ExternalLink class="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
              <div class="space-y-1.5">
                <Label class="text-xs font-medium text-muted-foreground">Trail Warning (optional)</Label>
                <Input v-model="form.description" placeholder="e.g., Expect to get wet — bring waterproof shoes" />
              </div>
            </CardContent>
          </Card>

        </div>

        <!-- Side col (1/3 width) -->
        <div class="space-y-6">

          <!-- Elevation -->
          <Card>
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-base">Elevation Data</CardTitle>
                <Badge v-if="trail.has_elevation_data || selectedElevationFile" variant="secondary" class="text-xs">
                  {{ selectedElevationFile ? 'Pending upload' : 'Uploaded' }}
                </Badge>
              </div>
            </CardHeader>
            <CardContent class="space-y-3">
              <ElevationChart v-if="elevationData" :elevationData="elevationData" />
              <div v-else class="flex flex-col items-center justify-center h-24 rounded-lg border border-dashed bg-muted/30 text-muted-foreground text-xs gap-2">
                <BarChart2 class="h-5 w-5 opacity-40" />
                No elevation data
              </div>
              <label class="flex items-center gap-2 cursor-pointer rounded-lg border px-3 py-2 text-xs hover:bg-muted/50 transition-colors">
                <BarChart2 class="h-3.5 w-3.5 text-muted-foreground" />
                <span class="text-muted-foreground">{{ selectedElevationFile ? selectedElevationFile.name : (trail.has_elevation_data ? 'Replace elevation .json' : 'Upload elevation .json') }}</span>
                <input type="file" accept=".json,.js,application/json" class="hidden" @change="e => selectedElevationFile = e.target.files[0]" />
              </label>
            </CardContent>
          </Card>

          <!-- Save -->
          <Button class="w-full" :disabled="saving" @click="save">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving…' : 'Save Changes' }}
          </Button>

          <!-- Danger zone -->
          <Card class="border-destructive/30">
            <CardHeader class="pb-3">
              <CardTitle class="text-base text-destructive flex items-center gap-2">
                <TriangleAlert class="h-4 w-4" />
                Danger Zone
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p class="text-xs text-muted-foreground mb-3">
                Permanently delete this trail and all associated data. This cannot be undone. Trails referenced by existing hikes cannot be deleted.
              </p>
              <Button variant="destructive" class="w-full" @click="deleteOpen = true">
                <Trash2 class="h-4 w-4" />
                Delete Trail
              </Button>
            </CardContent>
          </Card>

        </div>
      </div>
    </template>

    <!-- Delete confirm dialog -->
    <Dialog v-model:open="deleteOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete "{{ trail?.name }}"?</DialogTitle>
          <DialogDescription>
            This will permanently remove the trail from the catalog. Trails that are referenced by past or active hikes cannot be deleted.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" @click="deleteOpen = false">Cancel</Button>
          <Button variant="destructive" :disabled="deleting" @click="confirmDelete">
            {{ deleting ? 'Deleting…' : 'Delete Trail' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </section>
</template>
