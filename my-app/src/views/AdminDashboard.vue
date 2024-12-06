<!-- src/views/AdminDashboard.vue -->
<template>
    <div class="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
      <Navbar />
      <div class="p-6">
        <h1 class="text-2xl font-bold mb-6">Admin Dashboard</h1>
        <!-- Add admin-specific content here -->
      </div>
    </div>
  </template>
  
  <script>
  import Navbar from '../components/Navbar.vue';
  
  export default {
    name: 'AdminDashboard',
    components: {
      Navbar,
    },
    // ... rest of your script
  };
  </script>
  
  <style scoped>
  /* Additional styles if needed */
  </style>
  