<template>
  <div class="mx-auto px-6">
    <Card class="mx-auto w-fit bg-slate-200 border-0">
      <CardContent class="relative text-midnight px-10 py-6" id="about">
        <h2 class="flex justify-center items-center mb-4 text-3xl sm:text-4xl lg:text-5xl font-bold text-uci-blue font-montserrat">
          About the UCI Hiking Club
        </h2>
        <div class="max-w-4xl flex flex-col lg:flex-row gap-12 items-center">
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

          <div class="w-full lg:w-1/2 flex flex-col gap-6">

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
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import img from '@/assets/about_img.jpg';
import {Card, CardContent} from "@/components/ui/card";

const props = defineProps({
  image: {
    type: String,
    default: img,
  },
});
</script>