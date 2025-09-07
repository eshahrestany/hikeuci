<script setup>
import TrailsTable from "@/components/admin/TrailsTable.vue";
const props = defineProps({
  trailsData: {
    type: Array,
    required: true
  }
});
</script>

<template>
 <TrailsTable :trails-data="props.trailsData"/>
</template>
