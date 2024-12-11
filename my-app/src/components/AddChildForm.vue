<template>
  <div class="mb-6 p-4 bg-white dark:bg-gray-800 rounded shadow">
    <h3 class="text-lg font-medium mb-2 text-gray-800 dark:text-gray-100">Add a New Child</h3>
    <form @submit.prevent="handleSubmit">
      <!-- First Name Field -->
      <div class="mb-4">
        <label class="block text-gray-700 dark:text-gray-200 mb-1">First Name</label>
        <input
          v-model="firstName"
          type="text"
          class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded focus:outline-none focus:ring bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200"
          required
        />
      </div>

      <!-- Last Name Field -->
      <div class="mb-4">
        <label class="block text-gray-700 dark:text-gray-200 mb-1">Last Name</label>
        <input
          v-model="lastName"
          type="text"
          class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded focus:outline-none focus:ring bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200"
          required
        />
      </div>

      <!-- Select Class Field -->
      <div class="mb-4">
        <label class="block text-gray-700 dark:text-gray-200 mb-1">Select Class</label>
        <select
          v-model="classId"
          class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded focus:outline-none focus:ring bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200"
          required
        >
          <option value="" disabled>Select a class</option>
          <option
            v-for="classItem in classesList"
            :key="classItem.id"
            :value="classItem.id"
          >
            {{ classItem.class_name }} ({{ classItem.school_name }})
          </option>
        </select>
      </div>

      <!-- Buttons Container -->
      <div class="mt-4 flex">
        <button
          type="submit"
          class="py-2 px-4 bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg focus:outline-none transition"
        >
          Save Child
        </button>
        <button
          type="button"
          @click="$emit('cancel')"
          class="ml-2 py-2 px-4 bg-gray-300 hover:bg-gray-400 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-900 dark:text-gray-200 font-medium rounded-lg focus:outline-none transition"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'AddChildForm',
  props: {
    classesList: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      firstName: '',
      lastName: '',
      classId: ''
    };
  },
  methods: {
    handleSubmit() {
      this.$emit('add-child', {
        first_name: this.firstName.trim(),
        last_name: this.lastName.trim(),
        class_id: this.classId
      });
    }
  }
};
</script>

<style scoped>
/* Additional scoped styles if needed */
</style>
