<template>
  <section class="relative bg-stone/50 text-midnight py-20" id="about">
    <div class="max-w-6xl mx-auto px-6 flex flex-col lg:flex-row gap-12 items-center">
      <!-- Image / Illustration -->
      <div class="w-full lg:w-1/2">
        <img
          :src="image"
          alt="Group of hikers enjoying a summit view"
          class="w-full rounded-2xl shadow-lg"
          loading="lazy"
          width="1200"
          height="800"
        />
      </div>

      <!-- Text content -->
      <div class="w-full lg:w-1/2 flex flex-col gap-6">
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-uci-blue font-montserrat">
          About the UCI Hiking Club
        </h2>

        <p class="text-lg leading-relaxed text-midnight/90">
          <span class="font-semibold">Founded in 2015</span>, our club has grown from a small group of outdoor enthusiasts into one of UCI’s most active student organizations. Over the past decade, we've logged thousands of trail miles and fostered a supportive community that welcomes hikers of all experience levels.
        </p>

        <p class="text-lg leading-relaxed text-midnight/90">
          Our mission is simple: <span class="italic">“Make the outdoors accessible, safe, and enjoyable for everyone.”</span> We believe exploring nature builds resilience, cultivates stewardship, and strengthens friendships. Whether you’re looking to decompress with a sunset stroll or challenge yourself on a multi‑day trek, we’ve got you covered.
        </p>

        <p class="text-lg leading-relaxed text-midnight/90">
          Today, we host <span class="font-semibold">weekly local hikes</span>, <span class="font-semibold">quarterly retreats</span>, stewardship events with park partners, and skills workshops on everything from navigation to Leave No Trace ethics. Come hike with us—and discover what adventure means to you!
        </p>

        <!-- Keeping the button emit for now; swap to <router-link> when routing is ready -->
        <button
          @click="$emit('join-click')"
          class="self-start mt-4 inline-flex items-center gap-2 px-6 py-3 rounded-2xl text-lg font-semibold text-white bg-forest hover:bg-forest/80 transition duration-200"
          type="button"
        >
          Join a Hike
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            class="w-5 h-5"
          >
            <path
              fill-rule="evenodd"
              d="M12.293 5.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 11-1.414-1.414L16.586 13H4a1 1 0 110-2h12.586l-4.293-4.293a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import defaultImage from '../../assets/hiking_bg.jpg';

const props = defineProps({
  image: {
    type: String,
    default: defaultImage,
  },
});
</script>

<style scoped>
/* Add component‑specific styles here if needed */
</style>
