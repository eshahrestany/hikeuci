<script setup>
import {Card, CardContent, CardHeader} from "@/components/ui/card/index.js";
import {Skeleton} from "@/components/ui/skeleton/index.js";
import backgroundImage from '@/assets/hiking_bg.jpg'
import {onMounted, ref} from "vue";

const loading = ref(true);
const error = ref(null);
const tokenRef = ref(null);
const waiver_content = ref(null);


// Fetch waiver data
onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    const params = new URLSearchParams(window.location.search)
    const token = params.get("token")
    if (!token) {
      throw new Error("No token provided in URL")
    }
    tokenRef.value = token

    const res = await fetch(`/api/hike-waiver?token=${token}`)
    if (!res.ok) {
      let errMessage = `HTTP error! status: ${res.status}`
      try {
        const errData = await res.json()
        errMessage = errData.error || errMessage
      } catch (e) {
        // ignore JSON parse errors
      }
      throw new Error(errMessage)
    }
    const jsonResponse = await res.json()

    if (jsonResponse.status === 'ready') {
      waiver_content.value = jsonResponse.content
    }
    else if (jsonResponse.status === 'signed') {
      throw new Error('You have already signed this waiver. Thank you!')
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section
      class="relative bg-cover bg-center py-20 bg-fixed"
      :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <div class="absolute inset-0"/>
    <div class="relative mx-auto w-fit min-w-2xl px-2">
      <Card class="bg-white border">
        <CardContent class="p-6 pt-0">
          <div v-if="loading" class="space-y-4">
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
            <Skeleton class="h-4 w-full"/>
          </div>
          <div v-else-if="error" class="text-red-500 text-center">
            {{ error }}
          </div>
          <div v-else class="space-y-6">
            <div v-html="waiver_content" class="prose max-w-none"></div>
            <div class="text-center">
              <a
                  :href="`/sign-waiver?token=${tokenRef}`"
                  class="inline-block rounded bg-uci-blue px-6 py-3 text-white font-semibold hover:bg-uci-blue-dark transition"
              >Submit</a>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </section>
</template>