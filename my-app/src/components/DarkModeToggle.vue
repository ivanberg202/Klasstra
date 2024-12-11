<template>
    <button
      @click="toggleDarkMode"
      class="absolute top-4 right-4 p-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded shadow"
    >
      {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
    </button>
  </template>
  
  <script>
  export default {
    name: 'DarkModeToggle',
    props: {
      isDarkMode: {
        type: Boolean,
        default: false,
      },
    },
    methods: {
      toggleDarkMode(event) {
        // Emit an event so the parent can handle the actual toggling
        this.$emit('toggle-dark-mode', event);
      },
    },
  };
  </script>
  