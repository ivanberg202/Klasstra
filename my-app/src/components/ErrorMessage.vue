<template>
    <div v-if="message" class="text-center text-red-500 dark:text-red-400 mb-4">
      {{ message }}
    </div>
  </template>
  
  <script>
  export default {
    name: 'ErrorMessage',
    props: {
      message: {
        type: String,
        required: false,
      },
    },
  };
  </script>
  