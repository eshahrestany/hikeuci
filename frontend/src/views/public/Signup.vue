<script setup>
import NavBar from '../../components/public/Navbar.vue'
import SignupForm from '../../components/public/SignupForm.vue'
import Footer from '../../components/public/Footer.vue'

const hikeDescription = `### Hike Details
This Saturday, we will be hiking **Santiago Creek Trail and Barnham Ridge** which is in Santiago Oaks Park. The hike is around **6 miles** and should take around **2.5 hours** to complete. This hike is classified as **Moderate**. We will meet at the Chipotle/Chick Fil A area in UTC at **7:45 AM** and carpools will be arranged. We will be leaving UTC at **8:00 AM**.

**PLEASE remember this survey does not guarantee you a spot on the hike**, but shows your interest in going. This does not apply if you are a driver. **All drivers are guaranteed a spot**. This form will be closed **Thursday evening** (sometime around 5 or 5:30 PM). We will email you with an update on whether you got in or not on Thursday night.

### Important: Hydration
We **strongly recommend bringing water** for this hike. The general rule is to have a liter of water for every two hours, so for this hike, we recommend you to have **at least 1 liter of water**. This is for your safety so that we don't run into any issues with dehydration/heat exhaustion with warmer weather.`
</script>

<template>
  <NavBar :overlay-navbar="false" />
  <SignupForm
    title="Santiago Creek Trail & Barnham Ridge"
    :description="hikeDescription"
  />
  <Footer />
</template> 