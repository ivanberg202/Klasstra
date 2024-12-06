<script setup>
</script>

<template>
  <!-- Main container -->
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Router View for Pages -->
    <router-view />
  </div>
</template>

<style>
/* Global reset to prevent layout issues */
html,
body,
[data-v-app] {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  box-sizing: border-box; /* Ensure padding/borders are included in width/height */
}
</style>
