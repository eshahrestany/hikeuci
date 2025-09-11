<script setup>
import NavBar from '../../components/public/Navbar.vue'
import WaiverForm from '../../components/public/WaiverForm.vue'
import Footer from '../../components/public/Footer.vue'
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <NavBar :overlay-navbar="false" />
    <WaiverForm class="flex-grow place-content-center"/>
    <Footer/>
  </div>
</template>