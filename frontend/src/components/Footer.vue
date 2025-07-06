<template>
  <footer class="bg-midnight text-stone font-montserrat">
    <div class="max-w-7xl mx-auto px-6 py-12 grid gap-12 md:grid-cols-3">
      <!-- UCI Logo & address -->
      <div class="flex flex-col gap-4">
        <!-- Replace with the correct path to your logo asset -->
        <img
          src="../assets/uci_logo.png"
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
                viewBox="0 0 24 24"
                fill="currentColor"
                class="w-6 h-6"
              >
                <path
                  d="M2.25 6.75A2.25 2.25 0 0 1 4.5 4.5h15a2.25 2.25 0 0 1 2.25 2.25v10.5A2.25 2.25 0 0 1 19.5 19.5H4.5A2.25 2.25 0 0 1 2.25 17.25V6.75Zm1.86.19a.75.75 0 0 0-.36.64v.16l7.71 5.68a1.5 1.5 0 0 0 1.78 0l7.71-5.68v-.16a.75.75 0 0 0-.36-.64.75.75 0 0 0-.38-.11H4.49a.75.75 0 0 0-.38.11ZM20.25 8.9l-6.9 5.09a3 3 0 0 1-3.7 0L2.75 8.9v8.35c0 .414.336.75.75.75h15a.75.75 0 0 0 .75-.75V8.9Zm-9 4.22"/>
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
                viewBox="0 0 24 24"
                fill="currentColor"
                class="w-6 h-6"
              >
                <path
                  d="M7.75 2a5.75 5.75 0 0 0-5.75 5.75v8.5A5.75 5.75 0 0 0 7.75 22h8.5A5.75 5.75 0 0 0 22 16.25v-8.5A5.75 5.75 0 0 0 16.25 2h-8.5Zm0 1.5h8.5A4.25 4.25 0 0 1 20.5 7.75v8.5A4.25 4.25 0 0 1 16.25 20.5h-8.5A4.25 4.25 0 0 1 3.5 16.25v-8.5A4.25 4.25 0 0 1 7.75 3.5Zm8.5 2.5a1 1 0 1 0 0 2 1 1 0 0 0 0-2ZM12 7.25A4.75 4.75 0 1 0 12 16.75 4.75 4.75 0 0 0 12 7.25Zm0 1.5a3.25 3.25 0 1 1 0 6.5 3.25 3.25 0 0 1 0-6.5Z"/>
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