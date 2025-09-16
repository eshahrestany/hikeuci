<!-- HeroSection.vue -->
<template>
  <section
    class="relative flex items-center justify-center text-center text-white min-h-screen bg-midnight overflow-hidden"
  >
    <!-- Background image -->
    <div class="absolute inset-0 bg-cover bg-center bg-kenburns" :style="{ backgroundImage: `url(${background})` }" aria-hidden="true"></div>

    <!-- Overlay for readability -->
    <div
      class="absolute inset-0 pointer-events-none bg-gradient-to-b from-uci-blue/50 via-black/40 to-black/80"
      aria-hidden="true"
    ></div>

    <!-- Content -->
    <div
      class="relative z-10 flex flex-col items-center justify-center px-6 py-24 gap-6"
    >
      <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold font-montserrat text-uci-gold drop-shadow-md">
        Adventure Starts with UCI
      </h1>

      <p class="max-w-md text-lg sm:text-xl font-medium text-stone">
        Join the Hiking Club at UCI to discover breathtaking trails, make lifelong
        friends, and engage with your local community. No experience required.
      </p>

      <!-- Social links -->
      <div class="mt-6 flex items-center gap-4">
        <TooltipProvider>
          <!-- Instagram -->
          <Tooltip>
            <TooltipTrigger as-child>
              <a
                href="https://instagram.com/hikingclubatucirvine"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Instagram"
                class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-uci-blue hover:bg-uci-blue/80 transition duration-200"
              >
                <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="w-6 h-6"
                        viewBox="0 0 24 24"
                    >
                      <path
                          fill="currentColor"
                          d="M17.34 5.46a1.2 1.2 0 1 0 1.2 1.2a1.2 1.2 0 0 0-1.2-1.2Zm4.6 2.42a7.59 7.59 0 0 0-.46-2.43a4.94 4.94 0 0 0-1.16-1.77a4.7 4.7 0 0 0-1.77-1.15a7.3 7.3 0 0 0-2.43-.47C15.06 2 14.72 2 12 2s-3.06 0-4.12.06a7.3 7.3 0 0 0-2.43.47a4.78 4.78 0 0 0-1.77 1.15a4.7 4.7 0 0 0-1.15 1.77a7.3 7.3 0 0 0-.47 2.43C2 8.94 2 9.28 2 12s0 3.06.06 4.12a7.3 7.3 0 0 0 .47 2.43a4.7 4.7 0 0 0 1.15 1.77a4.78 4.78 0 0 0 1.77 1.15a7.3 7.3 0 0 0 2.43.47C8.94 22 9.28 22 12 22s3.06 0 4.12-.06a7.3 7.3 0 0 0 2.43-.47a4.7 4.7 0 0 0 1.77-1.15a4.85 4.85 0 0 0 1.16-1.77a7.59 7.59 0 0 0 .46-2.43c0-1.06.06-1.4.06-4.12s0-3.06-.06-4.12ZM20.14 16a5.61 5.61 0 0 1-.34 1.86a3.06 3.06 0 0 1-.75 1.15a3.19 3.19 0 0 1-1.15.75a5.61 5.61 0 0 1-1.86.34c-1 .05-1.37.06-4 .06s-3 0-4-.06a5.73 5.73 0 0 1-1.94-.3a3.27 3.27 0 0 1-1.1-.75a3 3 0 0 1-.74-1.15a5.54 5.54 0 0 1-.4-1.9c0-1-.06-1.37-.06-4s0-3 .06-4a5.54 5.54 0 0 1 .35-1.9A3 3 0 0 1 5 5a3.14 3.14 0 0 1 1.1-.8A5.73 5.73 0 0 1 8 3.86c1 0 1.37-.06 4-.06s3 0 4 .06a5.61 5.61 0 0 1 1.86.34a3.06 3.06 0 0 1 1.19 .8a3.06 3.06 0 0 1 .75 1.1a5.61 5.61 0 0 1 .34 1.9c.05 1 .06 1.37 .06 4s-.01 3-.06 4ZM12 6.87A5.13 5.13 0 1 0 17.14 12A5.12 5.12 0 0 0 12 6.87Zm0 8.46A3.33 3.33 0 1 1 15.33 12A3.33 3.33 0 0 1 12 15.33Z"/>
                    </svg>
              </a>
            </TooltipTrigger>
            <TooltipContent>Follow us on Instagram</TooltipContent>
          </Tooltip>

          <!-- Discord -->
          <Tooltip>
            <TooltipTrigger as-child>
              <a
                href="https://discord.gg/jWcN8dWQzC"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Discord"
                class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-uci-blue hover:bg-uci-blue/80 transition duration-200"
              >
                <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 16 16"
                        class="w-6 h-6"
                    >
                      <path
                          fill="currentColor"
                          d="M13.553 3.016A13.233 13.233 0 0 0 10.253 2a9.068 9.068 0 0 0-.423.86a12.293 12.293 0 0 0-3.664 0A9.112 9.112 0 0 0 5.744 2A13.358 13.358 0 0 0 2.44 3.018C.351 6.108-.215 9.123.068 12.094a13.306 13.306 0 0 0 4.048 2.033a9.78 9.78 0 0 0 .867-1.399a8.605 8.605 0 0 1-1.365-.652c.115-.083.227-.168.335-.251a9.51 9.51 0 0 0 8.094 0c.11 .09 .222 .175 .335 .251a8.648 8.648 0 0 1-1.368 .654a9.7 9.7 0 0 0 .867 1.396a13.248 13.248 0 0 0 4.051-2.03c.332-3.446-.568-6.433-2.379-9.08Zm-8.21 7.25c-.79 0-1.442-.715-1.442-1.596c0-.881.63-1.603 1.439-1.603s1.456 .722 1.442 1.603c-.014 .88-.636 1.597-1.44 1.597Zm5.315 0c-.79 0-1.44-.715-1.44-1.596c0-.881 .63-1.603 1.44-1.603c.81 0 1.452 .722 1.438 1.603c-.014 .88-.634 1.597-1.438 1.597Z"/>
                    </svg>
              </a>
            </TooltipTrigger>
            <TooltipContent>Join our Discord</TooltipContent>
          </Tooltip>

          <!-- Linktree -->
          <Tooltip>
            <TooltipTrigger as-child>
              <a
                href="https://linktr.ee/hikingclubatuci"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Linktree"
                class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-uci-blue hover:bg-uci-blue/80 transition duration-200"
              >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-6 h-6"
                    viewBox="0 0 24 24">
                  <path
                      fill="currentColor"
                      d="m13.736 5.853l4.005-4.117l2.325 2.38l-4.2 4.005h5.908v3.305h-5.937l4.229 4.108l-2.325 2.334l-5.74-5.769l-5.741 5.769l-2.325-2.325l4.229-4.108H2.226V8.121h5.909l-4.2-4.004l2.324-2.381l4.005 4.117V0h3.472zm-3.472 10.306h3.472V24h-3.472z"/>
                </svg>
              </a>
            </TooltipTrigger>
            <TooltipContent>All our links</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  </section>
</template>

<script setup>
import background from "@/assets/hiking_bg.jpg";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
</script>

<style scoped>
@keyframes kenburns {
  0% { transform: scale(1); }
  100% { transform: scale(1.07); }
}

.bg-kenburns {
  animation: kenburns 18s ease-out forwards;
}
</style>
