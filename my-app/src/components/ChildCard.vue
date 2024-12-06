<template>
    <div class="p-4 bg-white rounded shadow">
      <h3 class="text-lg font-medium">{{ firstName }} {{ lastName }}</h3>
      <p>Class: {{ className }}</p>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      firstName: {
        type: String,
        required: true,
      },
      lastName: {
        type: String,
        required: true,
      },
      className: {
        type: String,
        required: true,
      },
    },
  };
  </script>
  
  <style scoped>
  /* Styles specific to the child card */
  </style>
  