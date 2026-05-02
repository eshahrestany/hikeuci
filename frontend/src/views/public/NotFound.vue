<template>
  <div class="public-layout">
    <NavBar :sticky="true" />
    <div class="relative min-h-screen flex flex-col">
      <!-- Background -->
      <div
        class="fixed inset-0 bg-cover bg-center"
        :style="{ backgroundImage: `url(${background})` }"
        aria-hidden="true"
      ></div>
      <div class="pg-scrim" aria-hidden="true"></div>

      <!-- Centered content -->
      <div class="relative z-10 flex-1 flex items-center justify-center px-6 py-24">
        <div
          class="text-center rounded-3xl p-10 sm:p-14 max-w-md w-full"
          style="
            background: rgba(8,16,34,0.55);
            backdrop-filter: blur(28px) saturate(1.5);
            -webkit-backdrop-filter: blur(28px) saturate(1.5);
            border: 1px solid rgba(255,255,255,0.16);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.24), 0 30px 70px -20px rgba(0,0,0,0.60);
          "
        >
          <img
            :src="petrImg"
            alt="Petr the anteater mascot"
            class="mx-auto w-36 sm:w-44 drop-shadow-md mb-6"
          />
          <h1 class="text-4xl sm:text-5xl font-bold font-montserrat text-white mb-3" style="text-shadow:0 2px 8px rgba(0,0,0,0.5)">
            Page not found
          </h1>
          <p class="text-base mb-8" style="color:#c8d0de">
            We couldn't find that page. It may have moved or no longer exists.
          </p>

          <div class="flex items-center justify-center gap-3">
            <router-link
              to="/"
              class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-white transition-all text-sm"
              style="background:rgba(63,156,53,0.80);border:1px solid rgba(118,185,164,0.40);box-shadow:inset 0 1px 0 rgba(255,255,255,0.22);"
              aria-label="Back to homepage"
            >
              <ArrowLeft :size="15" />Home
            </router-link>

            <button
              type="button"
              class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold transition-all text-sm"
              style="background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.20);color:#f5f7fb;"
              @click="goBack"
              aria-label="Go back"
            >
              <Undo2 :size="15" />Go back
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ArrowLeft, Undo2 } from 'lucide-vue-next';
import NavBar from '@/components/public/Navbar.vue';
import petrImg from '@/assets/petr.png';
import background from '@/assets/bg.jpg';

const router = useRouter();

function goBack() {
  if (window.history.length > 1) router.back();
  else router.replace('/');
}
</script>
