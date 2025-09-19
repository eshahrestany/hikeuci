<template>
  <section class="relative bg-stone-400 text-midnight py-20">
    <div class="max-w-6xl mx-auto px-6">
      <!-- Header -->
      <header class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between mb-10">
        <div>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-uci-blue font-montserrat">
            UCI Hiking Club – Privacy Policy
          </h1>
          <p class="mt-2 text-midnight/80">
            This page explains what information we collect, why we collect it, and how you can manage your data.
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
            The UCI Hiking Club (“the Club”) is committed to protecting the privacy of its members. This policy explains
            how we collect, use, store, and share personal information.
          </p>
        </section>

        <!-- Information We Collect -->
        <section id="collected-info" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Information We Collect</h2>
          <p class="leading-relaxed text-midnight/90">
            We may collect the following information when you join or participate in the Club:
          </p>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>Contact details (name, email address, phone number, student ID).</li>
            <li>Vehicle information if you sign up as a driver.</li>
            <li>Participation records (event sign-ups, waivers, attendance).</li>
            <li>Photos or videos taken at Club events.</li>
          </ul>
        </section>

        <!-- How We Use Your Information -->
        <section id="info-usage" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">How We Use Your Information</h2>
          <p class="leading-relaxed text-midnight/90">
            We use collected information to:
          </p>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>Register members and manage Club communications.</li>
            <li>Organize and administer hikes, trips, and events.</li>
            <li>Ensure participant safety</li>
            <li>Comply with UC Irvine and legal requirements.</li>
            <li>Promote Club activities through photos or event summaries.</li>
          </ul>
        </section>

        <!-- Information Sharing -->
        <section id="info-sharing" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Information Sharing</h2>
          <p class="leading-relaxed text-midnight/90">
            The club will not sell or rent member information.
            We may share information only with:
          </p>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>UC Irvine and other associated entities (e.g. other clubs in the event of a collaboration) .</li>
            <li>Emergency responders (if necessary for health or safety).</li>
            <li>Service Providers used to manage forms securely</li>
          </ul>
        </section>

        <!-- Data Retention -->
        <section id="data-retention" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Data Retention</h2>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>Membership records will be stored for the duration of your active membership and up to three (3) years after.</li>
            <li>Liability waivers will be retained for at least seven (7) years in line with best practices.</li>
            <li>Photos/videos may be retained indefinitely unless a member requests removal.</li>
          </ul>
        </section>

        <!-- Member Rights -->
        <section id="member-rights" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Member Rights</h2>
          <p class="leading-relaxed text-midnight/90">
            Members have the right to:
          </p>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>Access and update their personal information.</li>
            <li>Request deletion of records (unless retention is required for legal purposes e.g. liability waivers).</li>
            <li>Opt out of photos/videos being used in Club promotions.</li>
          </ul>
        </section>

        <!-- Security -->
        <section id="security" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Security</h2>
          <p class="leading-relaxed text-midnight/90">
            We use storage tools (e.g., UCI Google Drive, HikeUCI Platform) to protect records. Access is limited to authorized Club officers.
          </p>
        </section>

         <!-- "Contact" -->
        <section id="member-rights" class="space-y-3">
          <h2 class="text-2xl font-bold text-uci-blue font-montserrat">Contact</h2>
          <ul class="list-disc pl-6 space-y-2 text-midnight/90">
            <li>
              Questions or privacy requests can be directed to
              <a
                href="mailto:hikingclub@uci.edu"
                class="underline decoration-uci-blue/40 underline-offset-2 hover:decoration-uci-blue"
              >hikingclub@uci.edu</a>.
            </li>
          </ul>
        </section>
        <!-- Footer / Adoption -->
        <section id="adoption" class="space-y-1">
          <p class="text-midnight/90"><span class="font-semibold">Adopted by:</span> UCI Hiking Club Board</p>
          <p class="text-midnight/90"><span class="font-semibold">Date:</span> September 2025</p>
        </section>
      </article>
    </div>
  </section>
</template>

<script setup>
import {ArrowLeft, Printer} from 'lucide-vue-next';
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
