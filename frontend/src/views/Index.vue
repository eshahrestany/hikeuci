<script setup>
import NavBar from "../components/Navbar.vue"
import Hero from "../components/Hero.vue"
import About from "../components/AboutSection.vue";
import Leadership from "../components/Leadership.vue";
import Footer from "../components/Footer.vue"
import router from "../router/index.js";

</script>

<template>
  <NavBar :overlay-navbar="true"/>
  <Hero/>
  <About/>
  <Leadership/>
  <Footer/>
</template>
