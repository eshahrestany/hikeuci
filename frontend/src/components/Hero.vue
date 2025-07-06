<!-- HeroSection.vue -->
<template>
  <section
    class="relative flex items-center justify-center text-center text-white min-h-screen bg-midnight overflow-hidden"
  >
    <!-- Background image -->
    <div
      class="absolute inset-0 bg-cover bg-center"
      :style="{ backgroundImage: `url(${background})` }"
      aria-hidden="true"
    />

    <!-- Overlay for readability. Disable pointer-events so it never blocks clicks. -->
    <div class="absolute inset-0 bg-black/50 pointer-events-none" aria-hidden="true"></div>

    <!-- Content -->
    <div
      class="relative z-10 flex flex-col items-center justify-center px-6 py-24 gap-6"
    >
      <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold font-montserrat text-uci-gold drop-shadow-md">
        Adventure Starts with UCI
      </h1>

      <p class="max-w-md text-lg sm:text-xl font-medium text-stone">
        Join the UCI Hiking Club to discover breathtaking trails, make lifelong
        friends, and engage with your local community.
      </p>

      <!-- Either an in-place scroll or a router link works fine -->
      <button
        @click="$emit('cta-click')"
        class="mt-4 inline-flex items-center gap-2 px-6 py-3 cursor-pointer rounded-2xl text-lg font-semibold bg-uci-blue hover:bg-uci-blue/80 transition duration-200"
        type="button"
      >
        About Us
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
          <path
            fill-rule="evenodd"
            d="M12.293 5.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 11-1.414-1.414L16.586 13H4a1 1 0 110-2h12.586l-4.293-4.293a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup>
import background from "../assets/hiking_bg.jpg";
</script>
