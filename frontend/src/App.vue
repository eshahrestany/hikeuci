<script setup>
import { Toaster } from "vue-sonner";
</script>

<template>
  <div id="app" class="overflow-x-hidden">
    <Toaster/>
    <router-view/>
  </div>
</template>
