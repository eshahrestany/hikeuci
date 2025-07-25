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
          ref="slidesRef"
          class="flex"
          :style="slidesStyle"
          aria-live="polite"
        >
          <div
            v-for="(officer, index) in loopedOfficers"
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
import { ref, computed, nextTick, watch, defineExpose, onMounted, onUnmounted } from 'vue';
import { useIntervalFn, useResizeObserver, useIntersectionObserver } from '@vueuse/core';

/* -------------------------------------------------------------
 * Types
 * -----------------------------------------------------------*/
interface Officer {
  name: string;
  title: string;
  photo: string; // Resolved URL to an image asset
}

/* -------------------------------------------------------------
 * Props
 * -----------------------------------------------------------*/
const props = defineProps({
  officers: {
    type: Array as () => Officer[],
    default: () => [
      { name: 'Aleksander Weihermuller', title: 'Co-President',   photo: '../assets/petr.png' },
      { name: 'Anna Kapp',              title: 'Co-President',   photo: '../assets/petr.png' },
      { name: 'Eric Miao',              title: 'Treasurer',      photo: '../assets/petr.png' },
      { name: 'Zoe Glenn',              title: 'General Officer', photo: '../assets/petr.png' },
      { name: 'Jake Gerber',            title: 'General Officer', photo: '../assets/petr.png' },
      { name: 'Evan Shahrestany',       title: 'General Officer', photo: '../assets/petr.png' },
    ],
  },
  intervalMs: {
    type: Number,
    default: 3000,
  },
});

/* -------------------------------------------------------------
 * Import **only image files** from assets so CSS / audio / etc. are ignored.
 * -----------------------------------------------------------*/
const importedImages = import.meta.glob(
  '../assets/**/*.{png,jpg,jpeg,webp,avif,gif,svg}',
  { eager: true, import: 'default' },
) as Record<string, string>; // key = relative path, value = resolved URL

/** Normalise the user‑supplied path so it matches the keys produced by
 *  import.meta.glob. The keys always start with "../assets/".
 */
function toGlobKey(path: string) {
  // Remove any leading "./" or "../" then ensure prefix "../assets/"
  const trimmed = path.replace(/^\.\/?/, '').replace(/^\.\/?/, '');
  return trimmed.startsWith('assets/') ? `../${trimmed}` : `../assets/${trimmed}`;
}

/** Map the original officers list ➜ list whose `photo` is a valid URL.
 *  If an entry isn't found in `importedImages`, we fall back to the raw string.
 */
const displayedOfficers = computed<Officer[]>(() =>
  props.officers.map((o) => {
    const key = toGlobKey(o.photo);
    return { ...o, photo: importedImages[key] ?? o.photo };
  }),
);

/* -------------------------------------------------------------
 * Duplicate list to enable seamless looping
 * -----------------------------------------------------------*/
const loopedOfficers = computed<Officer[]>(() => [
  ...displayedOfficers.value,
  ...displayedOfficers.value,
]);

/* -------------------------------------------------------------
 * Helper – split full name into first & remainder (last/middle)
 * -----------------------------------------------------------*/
function splitName(full: string) {
  const parts = full.trim().split(/\s+/);
  const first = parts.shift() ?? '';
  const last = parts.join(' ');
  return { first, last };
}

/* -------------------------------------------------------------
 * Responsive columns
 * -----------------------------------------------------------*/
const cardsPerView = ref(1);
function getCardsPerView(width: number) {
  if (width >= 1280) return 4; // xl
  if (width >= 1024) return 3; // lg
  if (width >= 640)  return 2; // sm / md
  return 1;                     // phones
}

/* -------------------------------------------------------------
 * Refs & observers
 * -----------------------------------------------------------*/
const wrapperRef = ref<HTMLElement | null>(null);
const sectionRef = ref<HTMLElement | null>(null);
const containerWidth = ref(0);

// Capture initial dimensions right after mount so card sizing is available
onMounted(() => {
  if (wrapperRef.value) {
    // Set width synchronously instead of waiting for ResizeObserver
    containerWidth.value = wrapperRef.value.clientWidth;
  }
  cardsPerView.value = getCardsPerView(window.innerWidth);
  // Measure once the DOM has stabilized
  measureNaturalWidths();

  // Handle seamless looping once the slide transition completes
  slidesRef.value?.addEventListener('transitionend', () => {
    const originalLength = displayedOfficers.value.length;
    if (currentIndex.value >= originalLength) {
      transitionEnabled.value = false; // temporarily disable animation
      currentIndex.value = currentIndex.value - originalLength;
      nextTick(() => {
        // Force reflow so the browser registers the style change
        void slidesRef.value?.offsetWidth;
        transitionEnabled.value = true; // re-enable animation
      });
    }
  });
});

onUnmounted(() => {
  slidesRef.value?.removeEventListener('transitionend', () => {});
});

// ResizeObserver – updates container width & cards-per-view reactively
useResizeObserver(wrapperRef, (entries) => {
  const entry = entries[0];
  if (!entry) return;
  containerWidth.value = entry.contentRect.width;
  cardsPerView.value = getCardsPerView(window.innerWidth);
});

/* -------------------------------------------------------------
 * Carousel translate logic – shift by exactly one visible card each tick
 * -----------------------------------------------------------*/
const currentIndex = ref(0);
const translate = computed(() => `translateX(-${currentIndex.value * (100 / cardsPerView.value)}%)`);

// Interval with pause/resume
const { pause, resume } = useIntervalFn(() => {
  // Advance by exactly one card each tick
  currentIndex.value += 1;
}, props.intervalMs, { immediate: false });

// Pause the carousel when the section scrolls out of view
useIntersectionObserver(sectionRef, ([{ isIntersecting }]) => {
  isIntersecting ? resume() : pause();
});

/* -------------------------------------------------------------
 * Dynamic sizing – measure widest natural card once
 * -----------------------------------------------------------*/
const maxCardNaturalWidth = ref(0);
function measureNaturalWidths() {
  nextTick(() => {
    if (!wrapperRef.value) return;
    const cardEls = wrapperRef.value.querySelectorAll<HTMLElement>('.leadership-card');
    if (!cardEls.length) return;
    let widest = 0;
    cardEls.forEach((el) => {
      // Temporarily clear any inline width so we read the element's natural size
      const previous = el.style.width;
      el.style.width = 'auto';
      widest = Math.max(widest, el.offsetWidth);
      // Restore prior width if one existed; otherwise leave it to Vue's reactive binding
      if (previous) {
        el.style.width = previous;
      } else {
        el.style.removeProperty('width');
      }
    });
    maxCardNaturalWidth.value = widest;
  });
}

// Re-measure on officers change
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

/* -------------------------------------------------------------
 * Refs for infinite scroll behaviour
 * -----------------------------------------------------------*/
const slidesRef = ref<HTMLElement | null>(null);
const transitionEnabled = ref(true);
const slidesStyle = computed(() => ({
  transform: translate.value,
  transition: transitionEnabled.value ? 'transform 0.7s ease-in-out' : 'none',
}));

/* -------------------------------------------------------------
 * Expose state for potential external controls / debugging
 * -----------------------------------------------------------*/
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
