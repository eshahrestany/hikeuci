<template>
  <section class="relative bg-stone-400 text-midnight py-20">
    <div class="max-w-6xl mx-auto px-6">
      <!-- Header -->
      <header class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between mb-10">
        <div>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-uci-blue font-montserrat">
            UCI Hiking Club – Electronic Records and Signatures Policy
          </h1>
          <p class="mt-2 text-midnight/80">
            This page explains how the Club uses electronic records and signatures, your rights, and how consent works.
          </p>
        </div>

        <div class="flex items-center gap-3">
          <router-link
            to="/"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-2xl font-semibold text-white bg-forest hover:bg-forest/80 transition h-9 border border-transparent"
            aria-label="Back to homepage"
          >
            <!-- Arrow Left -->
            <ArrowLeft size="16"/>
            Home
          </router-link>

          <Button
            type="button"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-2xl font-semibold text-uci-blue bg-white hover:bg-white/90 border border-stone-200 transition"
            @click="onPrint"
            aria-label="Print this policy"
          >
            <!-- Printer -->
            <Printer size="16"/>
            Print
          </Button>
        </div>
      </header>

      <!-- Quick nav (anchors) -->
      <nav class="mb-8">
        <ul class="flex flex-wrap gap-2">
          <li v-for="item in toc" :key="item.href">
            <a
              :href="item.href"
              class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-stone-200 text-sm text-midnight/90 hover:bg-white/90 transition"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-uci-blue"></span>{{ item.label }}
            </a>
          </li>
        </ul>
      </nav>

      <!-- Policy Card -->
      <article
        class="rounded-2xl bg-white/80 backdrop-blur border border-stone-200 shadow-lg p-6 sm:p-8 space-y-8 animate-fade-in"
      >
        <!-- Purpose -->
        <section id="purpose" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Purpose</h2>
          <p class="text-lg leading-relaxed text-midnight/90">
            The UCI Hiking Club (“the Club”) uses electronic records and electronic signatures to streamline membership,
            event registration, liability waivers, and communications. This policy explains how electronic records and
            signatures are used, how members’ rights are protected, and what consent means.
          </p>
        </section>

        <!-- Legal Effect -->
        <section id="legal-effect" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Legal Effect</h2>
          <p class="leading-relaxed text-midnight/90">
            In accordance with the Electronic Signatures in Global and National Commerce Act (E-SIGN Act):
          </p>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>Electronic signatures collected by the Club are legally binding and enforceable.</li>
            <li>Electronic records (including but not limited to event agreements) have the same legal validity as paper documents.</li>
          </ul>
        </section>

        <!-- Consent to Electronic Records -->
        <section id="consent" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Consent to Electronic Records</h2>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>By participating in Club activities or submitting forms electronically, members agree to receive, sign, and store records in electronic form.</li>
            <li>Members have the right to request paper copies of any record at no additional cost.</li>
            <li>
              Members may withdraw consent to electronic records at any time by notifying the Club in writing (email or paper notice).
              Withdrawal will not affect the validity of records already signed.
            </li>
          </ul>
        </section>

        <!-- Delivery and Accessibility -->
        <section id="delivery" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Delivery and Accessibility</h2>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>Electronic records will be provided via this website (the HikeUCI platform).</li>
            <li>Members must ensure they have access to the necessary technology (computer, smartphone, internet connection, and PDF reader).</li>
            <li>Records will remain available in electronic format for at least three (3) years after signing.</li>
          </ul>
        </section>

        <!-- Authentication and Security -->
        <section id="security" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Authentication and Security</h2>
          <p class="leading-relaxed text-midnight/90">To protect members and the Club:</p>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>Each electronic signature must be linked to a unique identifier (an email address).</li>
            <li>Audit trails (including time, date, and signer identity) will be preserved.</li>
            <li>Records will be stored securely in accordance with HikeUCI Data Retention policies.</li>
          </ul>
        </section>

        <!-- Member Rights -->
        <section id="member-rights" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Member Rights</h2>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>
              Members may request copies of signed electronic records by emailing the Club at
              <a
                href="mailto:hikingclub@uci.edu"
                class="underline decoration-uci-blue/40 underline-offset-2 hover:decoration-uci-blue"
              >hikingclub@uci.edu</a>.
            </li>
            <li>Members may revoke consent for future electronic records at any time, without penalty.</li>
          </ul>
        </section>

        <!-- Footer / Adoption -->
        <section id="adoption" class="space-y-1">
          <p class="text-midnight/90"><span class="font-semibold">Adopted by:</span> UCI Hiking Club Board</p>
          <p class="text-midnight/90"><span class="font-semibold">Date:</span> September 23, 2025</p>
        </section>
      </article>
    </div>
  </section>
</template>

<script setup>
import { Printer, ArrowLeft } from 'lucide-vue-next';
import { Button } from "@/components/ui/button";
function onPrint() {
  window.print()
}
</script>

<style scoped>
/* Smooth anchor scrolling (if not set globally) */
:root { scroll-behavior: smooth; }

/* Simple fade-in on the policy card */
@keyframes fade-in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 300ms ease-out; }
</style>
