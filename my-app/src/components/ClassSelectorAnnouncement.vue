<!-- ClassSelectorAnnouncement.vue -->
<template>
    <div>
      <label class="block text-sm font-medium mb-1">Select Class</label>
      <select
        v-model="selectedClassIdLocal"
        class="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
        @change="emitSelection"
      >
        <option disabled value="">Please select one</option>
        <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
          {{ classItem.class_name }}
        </option>
      </select>
      <div class="mt-2 flex justify-end">
        <button
          v-if="isLoading"
          disabled
          class="py-1 px-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg"
        >
          Loading...
        </button>
        <button
          @click="cancelSelection"
          class="ml-2 py-1 px-3 bg-gray-300 hover:bg-gray-400 text-gray-800 dark:bg-gray-600 dark:hover:bg-gray-700 rounded-lg"
        >
          Cancel
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    name: 'ClassSelectorAnnouncement',
    props: {
      selectedClassId: {
        type: [String, Number],
        default: '',
      },
      isLoading: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        classes: [], // Stores fetched classes
        selectedClassIdLocal: this.selectedClassId, // Local state for v-model
      };
    },
    watch: {
      selectedClassId(newVal) {
        this.selectedClassIdLocal = newVal; // Sync local state with prop
      },
    },
    methods: {
      async fetchAssignedClasses() {
        try {
          const response = await api.get('/teacher-classes'); // Fetch assigned classes
          this.classes = response.data;
        } catch (error) {
          console.error('Error fetching assigned classes:', error);
          alert('Failed to load your assigned classes.');
        }
      },
      emitSelection() {
        this.$emit('update:selectedClassId', this.selectedClassIdLocal); // Emit updated value
        this.$emit('class-selected', this.selectedClassIdLocal); // Additional event for custom handling
      },
      cancelSelection() {
        this.selectedClassIdLocal = ''; // Reset local state
        this.$emit('update:selectedClassId', ''); // Notify parent of reset
        this.$emit('class-selected', null); // Emit null for cancellation
      },
    },
    mounted() {
      this.fetchAssignedClasses(); // Load classes on mount
    },
  };
  </script>
  
  <style scoped>
  /* Add any component-specific styles here */
  </style>
  