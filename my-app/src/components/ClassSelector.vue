<!-- ClassSelector.vue -->
<template>
  <div>
    <label class="block text-sm font-medium mb-1">Select Class</label>
    <select
      v-model="localSelectedClassId"
      class="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      @change="assignClassToTeacher"
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
  name: 'ClassSelector',
  props: {
    classes: {
      type: Array,
      required: true,
    },
    selectedClassId: {
      type: [String, Number],
      default: '',
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
    teacherId: {
      // Pass the logged-in teacher's ID or leave it blank for the backend to infer
      type: [String, Number],
      required: false,
    },
  },
  data() {
    return {
      localSelectedClassId: this.selectedClassId,
    };
  },
  watch: {
    selectedClassId(newVal) {
      this.localSelectedClassId = newVal;
    },
  },
  methods: {
    async assignClassToTeacher() {
      const classId = this.localSelectedClassId;

      // Validate the selected class ID
      if (!classId) {
        console.error('Class ID is empty or invalid.');
        alert('Please select a valid class.');
        return;
      }

      // Prepare the payload
      const payload = {
        class_id: parseInt(classId), // Ensure the class ID is an integer
      };

      try {
        // Log the payload being sent
        console.log('Payload being sent to API:', payload);

        // Make the API call
        const response = await api.post('/teacher-class-assignments', payload);

        // Log the API response
        console.log('API Response:', response);

        // Emit the success event with the selected class ID
        this.$emit('class-assigned', classId);

        // Removed the alert from here
      } catch (error) {
        // Log the error response or message
        if (error.response) {
          console.error('Error response:', error.response);
        } else {
          console.error('Error message:', error.message);
        }

        // Notify the user
        alert('Failed to assign class. Please try again.');
      }
    },
    cancelSelection() {
      this.localSelectedClassId = '';
      this.$emit('update:selectedClassId', '');
      this.$emit('class-assigned', null); // Emit null to indicate cancellation
    },
  },
};
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
