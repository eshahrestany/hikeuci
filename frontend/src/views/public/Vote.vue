<script setup>
import NavBar from '../../components/public/Navbar.vue'
import VoteForm from '../../components/public/VoteForm.vue'
import Footer from '../../components/public/Footer.vue'

</script>
<template>
  <div class="flex flex-col min-h-screen">
    <NavBar :overlay-navbar="false"/>
    <VoteForm class="flex-grow place-content-center"/>
    <Footer/>
  </div>
</template>