<template>
  <div class="mx-auto px-6 py-8">
    <div
      id="about"
      class="mx-auto max-w-5xl rounded-3xl px-8 sm:px-10 py-8 sm:py-10"
      style="
        background: linear-gradient(155deg,
          rgba(255,255,255,0.72) 0%,
          rgba(255,255,255,0.52) 40%,
          rgba(255,255,255,0.40) 100%);
        backdrop-filter: blur(24px) saturate(1.80);
        -webkit-backdrop-filter: blur(24px) saturate(1.80);
        border: 1px solid rgba(255,255,255,0.70);
        box-shadow:
          inset 0 1px 0 rgba(255,255,255,0.95),
          inset 0 -1px 0 rgba(0,34,68,0.06),
          0 24px 60px -12px rgba(0,0,0,0.28);
      "
    >
      <h2 class="text-center mb-8 text-3xl sm:text-4xl lg:text-5xl font-bold text-uci-blue font-montserrat">
        About Hiking Club
      </h2>

      <div class="flex flex-col lg:flex-row gap-10 items-center">
        <div class="w-full lg:w-1/2">
          <img
            :src="image"
            alt="Group of hikers"
            class="w-full rounded-2xl shadow-lg"
            loading="lazy"
            width="1200"
            height="800"
          />
        </div>

        <div class="w-full lg:w-1/2 flex flex-col gap-6">
          <p class="text-lg leading-relaxed text-midnight">
            <span class="font-semibold">Founded in 2015</span>, our club has grown from a small group of outdoor enthusiasts into one of UCI's most active student organizations. Over the past decade, we've logged thousands of trail miles and fostered a supportive community that welcomes hikers of all experience levels.
          </p>

          <p class="text-lg leading-relaxed text-midnight">
            Hiking club explores trails all across Orange County, and add new ones to our schedule every year. Whether you are looking to enjoy the scenery, challenge your hiking skills, or simply make new friends, we would love for you to join us.
          </p>

          <p class="text-lg leading-relaxed text-midnight">
            Today, we host <span class="font-semibold">weekly local hikes</span> every Saturday morning, lead by our Hike Leaders, and finish off with an optional group lunch. To learn more, find us on Instagram at @hikingclubatucirvine.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import img from '@/assets/about_img.jpg';

const props = defineProps({
  image: {
    type: String,
    default: img,
  },
});
</script>
