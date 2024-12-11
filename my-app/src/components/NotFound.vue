<!-- src/components/NotFound.vue -->
<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
    <h1 class="text-4xl font-bold text-gray-800 dark:text-gray-200 mb-4">404 - Page Not Found</h1>
    <p class="text-gray-600 dark:text-gray-400 mb-6">Oops! The page you're looking for doesn't exist.</p>
    <router-link to="/" class="py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg">
      Go to Home
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
};
</script>

<style scoped>
/* Add component-specific styles here */
</style>
