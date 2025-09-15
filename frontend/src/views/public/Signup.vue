<script setup>
import NavBar from '../../components/public/Navbar.vue'
import SignupForm from '../../components/public/SignupForm.vue'
import Footer from '../../components/public/Footer.vue'

</script>

<template>
  <div class="flex flex-col min-h-screen">
    <NavBar :overlay-navbar="false" />
    <SignupForm class="flex-grow place-content-center"/>
    <Footer />
  </div>
</template> 