<!-- src/views/ClassDetail.vue -->
<template>
    <div class="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-800 rounded shadow">
      <h1 class="text-2xl font-bold mb-4">Class Details</h1>
      
      <div v-if="isLoading" class="text-center text-gray-500 dark:text-gray-400">
        Loading class details...
      </div>
      
      <div v-else-if="errorMessage" class="text-center text-red-500 dark:text-red-400">
        {{ errorMessage }}
      </div>
      
      <div v-else>
        <p><strong>Name:</strong> {{ classData.class_name }}</p>
        <p><strong>School:</strong> {{ classData.school_name }}</p>
        <!-- Add more class details as needed -->
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    name: 'ClassDetail',
    props: {
      id: {
        type: [Number, String],
        required: true,
      },
    },
    data() {
      return {
        classData: {},
        isLoading: true,
        errorMessage: '',
      };
    },
    methods: {
      async fetchClassDetails() {
        try {
          const response = await api.get(`/classes/${this.id}`); // Ensure this endpoint exists
          this.classData = response.data;
        } catch (error) {
          console.error('Error fetching class details:', error);
          if (error.response && error.response.status === 404) {
            this.errorMessage = 'Class not found.';
          } else {
            this.errorMessage = 'Failed to load class details. Please try again later.';
          }
        } finally {
          this.isLoading = false;
        }
      },
    },
    created() {
      this.fetchClassDetails();
    },
  };
  </script>
  
  <style scoped>
  /* Optional: Add component-specific styles here */
  </style>
  