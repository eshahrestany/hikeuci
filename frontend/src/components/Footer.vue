<template>
  <footer class="bg-midnight text-stone font-montserrat">
    <div class="max-w-7xl mx-auto px-6 py-12 grid gap-12 md:grid-cols-3">
      <!-- UCI Logo & address -->
      <div class="flex flex-col gap-4">
        <img
          :src="uciLogo"
          alt="University of California, Irvine"
          loading="lazy"
        />
        <address class="not-italic text-sm leading-relaxed">
          Hiking Club @ UCI<br />
          University of California, Irvine<br />
          Irvine, CA&nbsp;92697
        </address>
      </div>

      <!-- Quick links -->
      <nav aria-label="Footer navigation" class="grid gap-2">
        <router-link to="/" class="hover:text-uci-gold">Home</router-link>
        <router-link to="/about" class="hover:text-uci-gold">About Us</router-link>
        <router-link to="/leadership" class="hover:text-uci-gold">Leadership</router-link>
        <router-link to="/login" class="hover:text-uci-gold">Member Portal</router-link>
      </nav>

      <!-- Contact & meta -->
      <div class="flex flex-col gap-4">
        <!-- Social / contact -->
        <div>
          <p class="font-semibold text-uci-gold">Connect</p>
          <div class="flex gap-4 mt-2">
            <!-- Email -->
            <a
              href="mailto:hikingclub@uci.edu"
              aria-label="Email"
              class="hover:text-uci-gold transition-colors"
            >
              <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 16 16"
                  class="w-6 h-6"
              >
                <path
                    fill="currentColor"
                    fill-rule="evenodd"
                    d="M2 3.5h12a.5.5 0 0 1 .5.5v.572L8 8.286L1.5 4.572V4a.5.5 0 0 1 .5-.5Zm-.5 2.8V12a.5.5 0 0 0 .5.5h12a.5.5 0 0 0 .5-.5V6.3L8.372 9.8L8 10.014L7.628 9.8L1.5 6.3ZM0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4Z" clip-rule="evenodd"/>
              </svg>
            </a>

            <!-- Instagram -->
            <a
              href="https://instagram.com/hikingclubatucirvine"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Instagram"
              class="hover:text-uci-gold transition-colors"
            >
              <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-6 h-6"
                  viewBox="0 0 24 24"
              >
                <path
                    fill="currentColor"
                    d="M17.34 5.46a1.2 1.2 0 1 0 1.2 1.2a1.2 1.2 0 0 0-1.2-1.2Zm4.6 2.42a7.59 7.59 0 0 0-.46-2.43a4.94 4.94 0 0 0-1.16-1.77a4.7 4.7 0 0 0-1.77-1.15a7.3 7.3 0 0 0-2.43-.47C15.06 2 14.72 2 12 2s-3.06 0-4.12.06a7.3 7.3 0 0 0-2.43.47a4.78 4.78 0 0 0-1.77 1.15a4.7 4.7 0 0 0-1.15 1.77a7.3 7.3 0 0 0-.47 2.43C2 8.94 2 9.28 2 12s0 3.06.06 4.12a7.3 7.3 0 0 0 .47 2.43a4.7 4.7 0 0 0 1.15 1.77a4.78 4.78 0 0 0 1.77 1.15a7.3 7.3 0 0 0 2.43.47C8.94 22 9.28 22 12 22s3.06 0 4.12-.06a7.3 7.3 0 0 0 2.43-.47a4.7 4.7 0 0 0 1.77-1.15a4.85 4.85 0 0 0 1.16-1.77a7.59 7.59 0 0 0 .46-2.43c0-1.06.06-1.4.06-4.12s0-3.06-.06-4.12ZM20.14 16a5.61 5.61 0 0 1-.34 1.86a3.06 3.06 0 0 1-.75 1.15a3.19 3.19 0 0 1-1.15.75a5.61 5.61 0 0 1-1.86.34c-1 .05-1.37.06-4 .06s-3 0-4-.06a5.73 5.73 0 0 1-1.94-.3a3.27 3.27 0 0 1-1.1-.75a3 3 0 0 1-.74-1.15a5.54 5.54 0 0 1-.4-1.9c0-1-.06-1.37-.06-4s0-3 .06-4a5.54 5.54 0 0 1 .35-1.9A3 3 0 0 1 5 5a3.14 3.14 0 0 1 1.1-.8A5.73 5.73 0 0 1 8 3.86c1 0 1.37-.06 4-.06s3 0 4 .06a5.61 5.61 0 0 1 1.86.34a3.06 3.06 0 0 1 1.19.8a3.06 3.06 0 0 1 .75 1.1a5.61 5.61 0 0 1 .34 1.9c.05 1 .06 1.37.06 4s-.01 3-.06 4ZM12 6.87A5.13 5.13 0 1 0 17.14 12A5.12 5.12 0 0 0 12 6.87Zm0 8.46A3.33 3.33 0 1 1 15.33 12A3.33 3.33 0 0 1 12 15.33Z"/>
              </svg>
            </a>

            <!-- Discord -->
            <a
              href="https://discord.gg/jWcN8dWQzC"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Discord"
              class="hover:text-uci-gold transition-colors"
            >
              <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 16 16"
                  class="w-6 h-6"
              >
                <path
                    fill="currentColor"
                    d="M13.553 3.016A13.233 13.233 0 0 0 10.253 2a9.068 9.068 0 0 0-.423.86a12.293 12.293 0 0 0-3.664 0A9.112 9.112 0 0 0 5.744 2A13.358 13.358 0 0 0 2.44 3.018C.351 6.108-.215 9.123.068 12.094a13.306 13.306 0 0 0 4.048 2.033a9.78 9.78 0 0 0 .867-1.399a8.605 8.605 0 0 1-1.365-.652c.115-.083.227-.168.335-.251a9.51 9.51 0 0 0 8.094 0c.11.09.222.175.335.251a8.648 8.648 0 0 1-1.368.654a9.7 9.7 0 0 0 .867 1.396a13.248 13.248 0 0 0 4.051-2.03c.332-3.446-.568-6.433-2.379-9.08Zm-8.21 7.25c-.79 0-1.442-.715-1.442-1.596c0-.881.63-1.603 1.439-1.603s1.456.722 1.442 1.603c-.014.88-.636 1.597-1.44 1.597Zm5.315 0c-.79 0-1.44-.715-1.44-1.596c0-.881.63-1.603 1.44-1.603c.81 0 1.452.722 1.438 1.603c-.014.88-.634 1.597-1.438 1.597Z"/>
              </svg>
            </a>
            <!-- Github -->
            <a
              href="https://github.com/eshahrestany/hikeuci"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Github"
              class="hover:text-uci-gold transition-colors"
            >
              <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 432 416"
                  class="w-6 h-6"
              >
                <path
                    fill="currentColor"
                    d="M213.5 0q88.5 0 151 62.5T427 213q0 70-41 125.5T281 416q-14 2-14-11v-58q0-27-15-40q44-5 70.5-27t26.5-77q0-34-22-58q11-26-2-57q-18-5-58 22q-26-7-54-7t-53 7q-18-12-32.5-17.5T107 88h-6q-12 31-2 57q-22 24-22 58q0 55 27 77t70 27q-11 10-13 29q-42 18-62-18q-12-20-33-22q-2 0-4.5.5t-5 3.5t8.5 9q14 7 23 31q1 2 2 4.5t6.5 9.5t13 10.5T130 371t30-2v36q0 13-14 11q-64-22-105-77.5T0 213q0-88 62.5-150.5T213.5 0z"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- Copyright -->
        <p class="text-sm text-stone/70">
          © {{ year }} Hiking Club @ UCI. All rights reserved.
        </p>

        <!-- Watermark -->
        <p class="text-xs text-stone/50">
          Made by {{ creators }}.
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import uciLogo from '../assets/uci_logo.png';
const props = defineProps({
  /**
   * Comma‑separated list or sentence of creators to display in the watermark.
   */
  creators: {
    type: String,
    default: 'Evan Shahrestany and Gabriel Dodge',
  },
});

/**
 * Current year – avoids having to update the template annually.
 */
const year = new Date().getFullYear();
</script>