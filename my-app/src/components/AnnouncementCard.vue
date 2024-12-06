<template>
    <div class="p-4 bg-white rounded shadow">
      <h3 class="text-lg font-medium">{{ title }}</h3>
      <p>{{ content }}</p>
    </div>
  </template>
  
  <script>
  export default {
    props: ['title', 'content'],
  };
  </script>
  