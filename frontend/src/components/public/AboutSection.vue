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
          Hiking club explores trails all across Orange County, and add new ones to our schedule every year. Whether you are looking to enjoy the scenery, challenge your hiking skills, or simply make new friends, we would love for you to join us.
        </p>

        <p class="text-lg leading-relaxed text-midnight/90">
          Today, we host <span class="font-semibold">weekly local hikes</span> every Saturday morning, lead by our Hike Leaders, and finish off with an optional group lunch. To learn more, find us on Instagram at @hikingclubatucirvine.
        </p>

        
      </div>
    </div>
  </section>
</template>

<script setup>
import defaultImage from '@/assets/hiking_bg.jpg';

const props = defineProps({
  image: {
    type: String,
    default: defaultImage,
  },
});
</script>