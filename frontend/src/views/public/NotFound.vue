<template>
  <section class="relative bg-stone-400 text-midnight min-h-screen flex flex-col">
    <div class="max-w-6xl mx-auto w-full px-6 flex-1 flex items-center">
      <div class="w-full grid gap-6 text-center">
        <img :src="petrImg" alt="Petr the anteater mascot" class="mx-auto w-40 sm:w-48 md:w-56 drop-shadow-md" />
        <div class="space-y-2">
          <h1 class="text-4xl sm:text-5xl font-bold font-montserrat text-uci-blue">Page not found</h1>
          <p class="text-midnight/80 text-lg">We couldn't find that page. It may have moved or no longer exists.</p>
        </div>

        <div class="flex items-center justify-center gap-3">
          <router-link
            to="/"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-2xl font-semibold text-white bg-forest hover:bg-forest/80 transition h-9 border border-transparent"
            aria-label="Back to homepage"
          >
            <ArrowLeft size="16" />
            Home
          </router-link>

          <Button
            type="button"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-2xl font-semibold text-uci-blue bg-white hover:bg-white/90 border border-stone-200 transition"
            @click="goBack"
            aria-label="Go back"
          >
            <Undo2 size="16" />
            Go back
          </Button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft, Undo2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import petrImg from '@/assets/petr.png'

const router = useRouter()
function goBack() {
  if (window.history.length > 1) router.back()
  else router.replace('/')
}
</script>

<style scoped>
</style>


