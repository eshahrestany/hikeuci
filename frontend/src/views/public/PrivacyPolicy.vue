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
                  Privacy Policy
                </h1>
                <p class="mt-2 text-sm" style="color:#c8d0de">
                  What information we collect, why we collect it, and how you can manage your data.
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
                The UCI Hiking Club ("the Club") is committed to protecting the privacy of its members. This policy explains
                how we collect, use, store, and share personal information.
              </p>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="collected-info" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Information We Collect</h2>
              <p class="leading-relaxed">We may collect the following information when you join or participate in the Club:</p>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>Contact details (name, email address, phone number).</li>
                <li>Vehicle information if you sign up as a driver.</li>
                <li>Participation records (event sign-ups, waivers, attendance).</li>
                <li>Photos or videos taken at Club events.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="info-usage" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">How We Use Your Information</h2>
              <p class="leading-relaxed">We use collected information to:</p>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>Register members and manage Club communications.</li>
                <li>Organize and administer hikes, trips, and events.</li>
                <li>Ensure participant safety.</li>
                <li>Comply with UC Irvine and legal requirements.</li>
                <li>Promote Club activities through photos or event summaries.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="info-sharing" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Information Sharing</h2>
              <p class="leading-relaxed">The club will not sell or rent member information. We may share information only with:</p>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>UC Irvine and other associated entities (e.g. other clubs in the event of a collaboration).</li>
                <li>Emergency responders (if necessary for health or safety).</li>
                <li>Service providers used to manage forms securely.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="data-retention" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Data Retention</h2>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>Membership records will be stored for the duration of your active membership and up to three (3) years after.</li>
                <li>Liability waivers will be retained for at least seven (7) years in line with best practices.</li>
                <li>Photos/videos may be retained indefinitely unless a member requests removal.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="member-rights" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Member Rights</h2>
              <p class="leading-relaxed">Members have the right to:</p>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>Access and update their personal information.</li>
                <li>Request deletion of records (unless retention is required for legal purposes e.g. liability waivers).</li>
                <li>Opt out of photos/videos being used in Club promotions.</li>
              </ul>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="security" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Security</h2>
              <p class="leading-relaxed">
                We use storage tools (e.g., UCI Google Drive, HikeUCI Platform) to protect records. Access is limited to authorized Club officers.
              </p>
            </section>

            <hr style="border-color:rgba(255,255,255,0.10)" />

            <section id="contact" class="space-y-3">
              <h2 class="text-xl font-bold font-montserrat" style="color:#a8c5ec">Contact</h2>
              <ul class="list-disc pl-6 space-y-1.5" style="color:#d4dcea">
                <li>
                  Questions or privacy requests can be directed to
                  <a href="mailto:hikingclub@uci.edu" style="color:#a8c5ec;text-decoration:underline;text-underline-offset:3px;">hikingclub@uci.edu</a>.
                </li>
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
import { ArrowLeft, Printer } from 'lucide-vue-next';
import NavBar from '@/components/public/Navbar.vue';
import Footer from '@/components/public/Footer.vue';
import background from '@/assets/bg.jpg';

const toc = ref([
  { href: '#purpose',        label: 'Purpose' },
  { href: '#collected-info', label: 'Information We Collect' },
  { href: '#info-usage',     label: 'How We Use It' },
  { href: '#info-sharing',   label: 'Information Sharing' },
  { href: '#data-retention', label: 'Data Retention' },
  { href: '#member-rights',  label: 'Member Rights' },
  { href: '#security',       label: 'Security' },
  { href: '#contact',        label: 'Contact' },
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
