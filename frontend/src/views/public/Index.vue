<script setup>
import NavBar from "../../components/public/Navbar.vue"
import Hero from "../../components/public/Hero.vue"
import About from "../../components/public/AboutSection.vue";
import Leadership from "../../components/public/Leadership.vue";
import Footer from "../../components/public/Footer.vue"
import router from "../../router/index.js";

</script>

<template>
  <NavBar :overlay-navbar="true"/>
  <Hero/>
  <About/>
  <Leadership/>
  <Footer/>
</template>
