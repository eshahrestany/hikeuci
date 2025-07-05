<script setup>
import {onMounted} from "vue";


onMounted(async() => {
  console.log("Hello World!");
})

</script>

<style>
/* Subtle entrance animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.8s ease-out both;
}
</style>

<template>
  <!-- Full‑screen gradient background -->
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
    <!-- Frosted‑glass card -->
    <div class="bg-white/30 backdrop-blur-md shadow-2xl rounded-2xl p-12 max-w-md w-full animate-fadeIn">
      <h1 class="text-5xl font-extrabold text-white drop-shadow-md">
        Hello&nbsp;World!
      </h1>
      <p class="mt-4 text-lg text-white/90">
        Welcome to your Vue&nbsp;3&nbsp;+&nbsp;Tailwind&nbsp;CSS app.
      </p>
    </div>
  </div>
</template>
