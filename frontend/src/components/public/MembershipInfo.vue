<template>
  <section id="membership" class="text-white py-8">
    <div class="max-w-5xl mx-auto px-6">
      <h2 class="text-center text-3xl sm:text-4xl lg:text-5xl font-bold text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.7)] font-montserrat mb-8">
        Join today!
      </h2>

      <!-- Outer glass island -->
      <div
        class="relative rounded-3xl overflow-hidden p-8 sm:p-10"
        style="
          background: rgba(8,16,48,0.58);
          backdrop-filter: blur(28px) saturate(1.55);
          -webkit-backdrop-filter: blur(28px) saturate(1.55);
          border: 1px solid rgba(255,255,255,0.16);
          box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.22),
            inset 0 -1px 0 rgba(0,0,0,0.18),
            0 32px 80px -20px rgba(0,0,0,0.70);
        "
      >
        <!-- ambient glow -->
        <div
          class="absolute -bottom-10 -right-10 w-72 h-72 rounded-full pointer-events-none opacity-50"
          style="background: radial-gradient(circle, rgba(26,57,49,0.60) 0%, transparent 70%);"
          aria-hidden="true"
        ></div>

        <!-- T-shirt banner -->
        <div class="relative mb-6 select-none">
          <div
            class="rounded-xl px-4 sm:px-6 py-2 sm:py-3 font-montserrat text-center"
            style="
              background: linear-gradient(155deg, rgba(26,57,49,0.80) 0%, rgba(26,57,49,0.55) 100%);
              border: 1px solid rgba(118,185,164,0.40);
              box-shadow: inset 0 1px 0 rgba(255,255,255,0.18), 0 10px 30px -10px rgba(0,0,0,0.45);
            "
          >
            <span class="block font-extrabold tracking-wide leading-none text-lg sm:text-xl lg:text-2xl text-white">
              MEMBERSHIP COMES WITH A FREE T-SHIRT!
            </span>
          </div>
        </div>

        <!-- Two floating island cards -->
        <div class="mt-8 sm:mt-10 grid gap-6 md:grid-cols-[1fr_auto_1fr] items-stretch">
          <!-- Venmo card -->
          <div
            class="rounded-2xl p-6 sm:p-8 flex flex-col justify-center"
            style="
              background: rgba(255,255,255,0.88);
              border: 1px solid rgba(255,255,255,0.70);
              box-shadow: inset 0 1px 0 rgba(255,255,255,0.95), 0 16px 40px -12px rgba(0,0,0,0.40);
            "
          >
            <p class="text-lg font-extrabold uppercase tracking-wide font-montserrat text-midnight">Venmo $12 to</p>
            <p class="mt-1 text-2xl font-extrabold text-uci-blue font-montserrat">@hikingclubatuci</p>
            <div class="mt-4">
              <p class="font-semibold text-midnight">Include your:</p>
              <ul class="mt-1 space-y-1 font-bold text-midnight">
                <li>Full name and</li>
                <li>School email (Open to all college students!)</li>
              </ul>
            </div>
          </div>

          <div class="flex items-center justify-center">
            <span class="text-white text-4xl font-extrabold font-montserrat" style="text-shadow:0 2px 8px rgba(0,0,0,0.5)">OR</span>
          </div>

          <!-- Alt payment card -->
          <div
            class="rounded-2xl p-6 sm:p-8 flex flex-col justify-center"
            style="
              background: rgba(255,255,255,0.88);
              border: 1px solid rgba(255,255,255,0.70);
              box-shadow: inset 0 1px 0 rgba(255,255,255,0.95), 0 16px 40px -12px rgba(0,0,0,0.40);
            "
          >
            <p class="text-lg font-extrabold uppercase tracking-wide font-montserrat text-midnight">Don't have Venmo?</p>
            <p class="mt-3 text-base leading-relaxed text-midnight">
              DM <span class="font-extrabold">@soap.p.suds</span> on Discord for
              Zelle or PayPal.
            </p>
          </div>
        </div>

        <p class="mt-10 text-center text-2xl sm:text-3xl font-extrabold font-montserrat text-white" style="text-shadow:0 2px 6px rgba(0,0,0,0.45)">
          Hike sign-ups come out Tuesday evening, so check your inbox then!
        </p>

        <p class="mt-6 text-center text-stone/80 italic font-semibold">
          Any questions? Didn't receive an email?
          DM any officer on Discord and we will help you out!
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
</script>
