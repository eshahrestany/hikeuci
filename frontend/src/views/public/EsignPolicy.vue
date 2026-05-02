<template>
  <div class="public-layout">
    <NavBar :sticky="true" />

    <div class="relative min-h-screen">
      <!-- Background -->
      <div
        class="fixed inset-0 bg-cover bg-center"
        :style="{ backgroundImage: `url(${background})` }"
        aria-hidden="true"
      ></div>
      <div class="pg-scrim" aria-hidden="true"></div>

      <!-- Content -->
      <div class="relative z-10 pt-24 pb-16 px-4 sm:px-6">
        <div class="max-w-4xl mx-auto">
          <!-- Page header -->
          <header class="mb-8">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h1 class="text-3xl sm:text-4xl font-bold font-montserrat text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.7)]">
                  Electronic Records & Signatures Policy
                </h1>
                <p class="mt-2 text-sm" style="color:#c8d0de">
                  How the Club uses electronic records and signatures, your rights, and how consent works.
                </p>
              </div>
              <div class="flex items-center gap-3 flex-shrink-0">
                <router-link
                  to="/"
                  class="inline-flex items-center gap-2 px-4 py-2 rounded-xl font-semibold text-white transition-all text-sm"
                  style="background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.20);backdrop-filter:blur(10px);"
                  aria-label="Back to homepage"
                >
                  <ArrowLeft :size="15" />Home
                </router-link>
                <button
                  type="button"
                  class="inline-flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all text-sm"
                  style="background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.20);backdrop-filter:blur(10px);color:#f5f7fb;"
                  @click="onPrint"
                  aria-label="Print this policy"
                >
                  <Printer :size="15" />Print
                </button>
              </div>
            </div>

            <!-- TOC pills -->
            <nav class="mt-6">
              <ul class="flex flex-wrap gap-2">
                <li v-for="item in toc" :key="item.href">
                  <a
                    :href="item.href"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                    style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14);color:#c8d0de;"
                  >
                    <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" style="background:#4f88d6"></span>
                    {{ item.label }}
                  </a>
                </li>
              </ul>
            </nav>
          </header>

          <!-- Glass article card -->
          <article
            class="rounded-2xl p-6 sm:p-10 space-y-8 animate-fade-in"
            style="
              background: rgba(8,16,34,0.55);
              backdrop-filter: blur(28px) saturate(1.5);
              -webkit-backdrop-filter: blur(28px) saturate(1.5);
              border: 1px solid rgba(255,255,255,0.16);
              box-shadow: inset 0 1px 0 rgba(255,255,255,0.24), 0 30px 70px -20px rgba(0,0,0,0.60);
              color: #e6ecf7;
            "
          >
            <section id="purpose" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Purpose</h2>
              <p class="leading-relaxed">
                The UCI Hiking Club ("the Club") uses electronic records and electronic signatures to streamline membership,
                event registration, liability waivers, and communications. This policy explains how electronic records and
                signatures are used, how members' rights are protected, and what consent means.
              </p>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="legal-effect" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Legal Effect</h2>
              <p class="leading-relaxed">In accordance with the Electronic Signatures in Global and National Commerce Act (E-SIGN Act):</p>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>Electronic signatures collected by the Club are legally binding and enforceable.</li>
                <li>Electronic records (including but not limited to event agreements) have the same legal validity as paper documents.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="consent" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Consent to Electronic Records</h2>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>By participating in Club activities or submitting forms electronically, members agree to receive, sign, and store records in electronic form.</li>
                <li>Members have the right to request paper copies of any record at no additional cost.</li>
                <li>
                  Members may withdraw consent to electronic records at any time by notifying the Club in writing (email or paper notice).
                  Withdrawal will not affect the validity of records already signed.
                </li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="delivery" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Delivery and Accessibility</h2>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>Electronic records will be provided via this website (the HikeUCI platform).</li>
                <li>Members must ensure they have access to the necessary technology (computer, smartphone, internet connection, and PDF reader).</li>
                <li>Records will remain available in electronic format for at least three (3) years after signing.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="security" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Authentication and Security</h2>
              <p class="leading-relaxed">To protect members and the Club:</p>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>Each electronic signature must be linked to a unique identifier (an email address).</li>
                <li>Audit trails (including time, date, and signer identity) will be preserved.</li>
                <li>Records will be stored securely in accordance with HikeUCI Data Retention policies.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="member-rights" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Member Rights</h2>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>
                  Members may request copies of signed electronic records by emailing the Club at
                  <a href="mailto:hikingclub@uci.edu" style="color:#a8c5ec;text-decoration:underline;text-underline-offset:3px;">hikingclub@uci.edu</a>.
                </li>
                <li>Members may revoke consent for future electronic records at any time, without penalty.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="adoption" class="space-y-1 text-sm" style="color:#8a9ab8">
              <p><span class="font-semibold" style="color:#c8d0de">Adopted by:</span> UCI Hiking Club Board</p>
              <p><span class="font-semibold" style="color:#c8d0de">Date:</span> September 23, 2025</p>
            </section>
          </article>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Printer, ArrowLeft } from 'lucide-vue-next';
import NavBar from '@/components/public/Navbar.vue';
import Footer from '@/components/public/Footer.vue';
import background from '@/assets/bg.jpg';

const toc = ref([
  { href: '#purpose',      label: 'Purpose' },
  { href: '#legal-effect', label: 'Legal Effect' },
  { href: '#consent',      label: 'Consent' },
  { href: '#delivery',     label: 'Delivery & Accessibility' },
  { href: '#security',     label: 'Security' },
  { href: '#member-rights',label: 'Member Rights' },
]);

function onPrint() {
  window.print();
}
</script>

<style scoped>
:root { scroll-behavior: smooth; }
@keyframes fade-in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 300ms ease-out; }
</style>
