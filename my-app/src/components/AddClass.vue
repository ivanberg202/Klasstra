<!-- src/components/AddClass.vue -->
<template>
    <div class="max-w-md mx-auto bg-white dark:bg-gray-800 p-6 rounded shadow-md">
      <h2 class="text-xl font-semibold mb-4">Add New Class</h2>
  
      <!-- Error Message -->
      <div v-if="errorMessage" class="text-red-500 dark:text-red-400 mb-4">
        {{ errorMessage }}
      </div>
  
      <!-- Success Message -->
      <div v-if="successMessage" class="text-green-500 dark:text-green-400 mb-4">
        {{ successMessage }}
      </div>
  
      <form @submit.prevent="handleAddClass">
        <!-- Select School -->
        <div class="mb-4">
          <label class="block text-gray-700 dark:text-gray-200 mb-1" for="school-select">Select School</label>
          <select
            id="school-select"
            v-model="selectedSchoolId"
            class="w-full p-2 border rounded focus:outline-none focus:ring bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200"
            :disabled="isLoading"
            required
          >
            <option value="" disabled>Select a school</option>
            <option
              v-for="school in schools"
              :key="school.id"
              :value="school.id"
            >
              {{ school.name }}
            </option>
          </select>
        </div>
  
        <!-- Input Class Name -->
        <div class="mb-4">
          <label class="block text-gray-700 dark:text-gray-200 mb-1" for="class-name">Class Name</label>
          <input
            id="class-name"
            type="text"
            v-model="className"
            class="w-full p-2 border rounded focus:outline-none focus:ring bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200"
            placeholder="Enter class name"
            required
          />
        </div>
  
        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg focus:outline-none transition disabled:opacity-50"
        >
          {{ isSubmitting ? 'Adding...' : 'Add Class' }}
        </button>
      </form>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    name: 'AddClass',
    data() {
      return {
        schools: [],
        selectedSchoolId: '',
        className: '',
        isLoading: true,
        isSubmitting: false,
        errorMessage: '',
        successMessage: '',
      };
    },
    methods: {
      async fetchSchools() {
        try {
          const response = await api.get('/schools/all'); // Adjust endpoint as needed
          this.schools = response.data;
        } catch (error) {
          console.error('Error fetching schools:', error);
          this.errorMessage = 'Failed to load schools. Please try again later.';
        } finally {
          this.isLoading = false;
        }
      },
      async handleAddClass() {
        this.errorMessage = '';
        this.successMessage = '';
        this.isSubmitting = true;
  
        try {
          const payload = {
            name: this.className.trim(),
            school_id: this.selectedSchoolId,
          };
  
          const response = await api.post('/classes/create', payload);
          this.successMessage = `Class "${response.data.name}" has been successfully added.`;
          this.className = '';
          this.selectedSchoolId = '';
  
          // Emit an event to notify parent components to refresh class lists
          this.$emit('class-added', response.data);
        } catch (error) {
          console.error('Error adding class:', error);
          if (error.response && error.response.data && error.response.data.detail) {
            this.errorMessage = error.response.data.detail;
          } else {
            this.errorMessage = 'Failed to add class. Please try again.';
          }
        } finally {
          this.isSubmitting = false;
        }
      },
    },
    created() {
      this.fetchSchools();
    },
  };
  </script>
  
  <style scoped>
  /* Optional: Add any component-specific styles here */
  </style>
  