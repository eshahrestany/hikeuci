<template>
  <section
    class="relative bg-stone/20 text-midnight py-20"
    id="leadership"
    ref="sectionRef"
  >
    <div class="max-w-6xl mx-auto px-6 flex flex-col items-center gap-12">
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-uci-blue font-montserrat">
        Meet Our Leadership
      </h2>

      <!-- Carousel wrapper -->
      <div ref="wrapperRef" class="relative w-full overflow-hidden pb-5">
        <!-- Slides -->
        <div
          class="flex transition-transform duration-700 ease-in-out"
          :style="{ transform: translate }"
          aria-live="polite"
        >
          <div
            v-for="(officer, index) in officers"
            :key="index"
            class="flex-shrink-0 flex justify-center px-4"
            :style="containerStyle"
          >
            <div
              class="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center gap-4 leadership-card w-full"
              :style="cardStyle"
            >
              <img
                :src="officer.photo"
                :alt="`Photo of ${officer.name}`"
                class="w-32 h-32 object-cover rounded-full border-4 border-uci-gold shadow-md"
                loading="lazy"
                width="128"
                height="128"
              />
              <h3 class="text-xl font-bold text-midnight font-montserrat text-center">
                <span class="block">{{ splitName(officer.name).first }}</span>
                <span class="block">{{ splitName(officer.name).last }}</span>
              </h3>
              <p class="text-lg text-uci-blue font-medium text-center">{{ officer.title }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, defineExpose } from 'vue';
import { useIntervalFn, useResizeObserver, useIntersectionObserver } from '@vueuse/core';

interface Officer {
  name: string;
  title: string;
  photo: string;
}

/* ------------------------------------------------------------------
 * Props
 * ---------------------------------------------------------------- */
const props = defineProps({
  officers: {
    type: Array as () => Officer[],
    default: () => [
      { name: 'Aleksander Weihermuller', title: 'Co-President', photo: '/src/assets/petr.png' },
      { name: 'Anna Kapp',              title: 'Co-President', photo: '/src/assets/petr.png' },
      { name: 'Eric Miao',              title: 'Treasurer',    photo: '/src/assets/petr.png' },
      { name: 'Zoe Glenn',              title: 'General Officer', photo: '/src/assets/petr.png' },
      { name: 'Jake Gerber',            title: 'General Officer', photo: '/src/assets/petr.png' },
      { name: 'Evan Shahrestany',       title: 'General Officer', photo: '/src/assets/petr.png' },
    ],
  },
  intervalMs: {
    type: Number,
    default: 3000,
  },
});

/* ------------------------------------------------------------------
 * Helper – split full name into first & remainder (last/middle)
 * ---------------------------------------------------------------- */
function splitName(full: string) {
  const parts = full.trim().split(/\s+/);
  const first = parts.shift() ?? '';
  const last = parts.join(' ');
  return { first, last };
}

/* ------------------------------------------------------------------
 * Responsive columns
 * ---------------------------------------------------------------- */
const cardsPerView = ref(1);
function getCardsPerView(width: number) {
  if (width >= 1280) return 4; // xl
  if (width >= 1024) return 3; // lg
  if (width >= 640)  return 2; // sm / md
  return 1;                     // phones
}

/* ------------------------------------------------------------------
 * Refs & observers
 * ---------------------------------------------------------------- */
const wrapperRef = ref<HTMLElement | null>(null);
const sectionRef = ref<HTMLElement | null>(null);
const containerWidth = ref(0);

// ResizeObserver – updates container width & cards-per-view reactively
useResizeObserver(wrapperRef, (entries) => {
  const entry = entries[0];
  if (!entry) return;
  containerWidth.value = entry.contentRect.width;
  cardsPerView.value = getCardsPerView(window.innerWidth);
});

/* ------------------------------------------------------------------
 * Carousel translate logic – shift by exactly one visible card each tick
 * ---------------------------------------------------------------- */
const currentIndex = ref(0);
const translate = computed(() => `translateX(-${currentIndex.value * (100 / cardsPerView.value)}%)`);

// Interval with pause/resume
const { pause, resume } = useIntervalFn(() => {
  const maxIndex = Math.max(props.officers.length - cardsPerView.value, 0);
  currentIndex.value = currentIndex.value >= maxIndex ? 0 : currentIndex.value + 1;
}, props.intervalMs, { immediate: false });

// Pause the carousel when the section scrolls out of view
useIntersectionObserver(sectionRef, ([{ isIntersecting }]) => {
  isIntersecting ? resume() : pause();
});

/* ------------------------------------------------------------------
 * Dynamic sizing – measure widest natural card once
 * ---------------------------------------------------------------- */
const maxCardNaturalWidth = ref(0);
function measureNaturalWidths() {
  nextTick(() => {
    if (!wrapperRef.value) return;
    const cardEls = wrapperRef.value.querySelectorAll<HTMLElement>('.leadership-card');
    if (!cardEls.length) return;
    let widest = 0;
    cardEls.forEach(el => {
      const original = el.style.width;
      el.style.width = 'auto';
      widest = Math.max(widest, el.offsetWidth);
      el.style.width = original;
    });
    maxCardNaturalWidth.value = widest;
  });
}

// Re‑measure on officers change
watch(() => props.officers, measureNaturalWidths, { deep: true, immediate: true });

/* Width calculations */
const columnWidth = computed(() => (containerWidth.value ? containerWidth.value / cardsPerView.value : 0));
const cardWidth = computed(() => {
  if (!columnWidth.value) return undefined;
  return Math.min(maxCardNaturalWidth.value, columnWidth.value);
});

const containerStyle = computed(() => ({
  flex: `0 0 ${100 / cardsPerView.value}%`,
}));
const cardStyle = computed(() => (cardWidth.value ? { width: `${cardWidth.value}px` } : {}));

/* ------------------------------------------------------------------
 * Expose state for potential external controls / debugging
 * ---------------------------------------------------------------- */
defineExpose({ currentIndex });
</script>

<style scoped>
/* Enable momentum scrolling on iOS */
section {
  -webkit-overflow-scrolling: touch;
}

.leadership-card {
  transition: width 0.2s ease;
  max-width: 100%;
}
</style>
