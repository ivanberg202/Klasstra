<template>
  <div class="p-4 bg-white dark:bg-gray-800 rounded shadow flex justify-between items-center">
    <!-- Child Info -->
    <div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white">{{ firstName }} {{ lastName }}</h3>
      <p class="text-gray-700 dark:text-gray-300">Class: {{ className }}</p>
    </div>

    <!-- Delete Icon -->
    <button
      @click="confirmDelete"
      class="text-red-500 hover:text-red-700 focus:outline-none transition"
      aria-label="Delete child"
      title="Delete child"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>

    <!-- Confirmation Modal -->
    <div v-if="showConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white dark:bg-gray-800 p-6 rounded shadow max-w-sm w-full">
        <p class="text-gray-900 dark:text-gray-100">Are you sure you want to delete this child?</p>
        <div class="flex justify-end mt-4">
          <button
            @click="cancelDelete"
            class="py-2 px-4 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg focus:outline-none mr-2 text-gray-800 dark:text-gray-200"
          >
            Cancel
          </button>
          <button
            @click="deleteChild"
            class="py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg focus:outline-none"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
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
    studentId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      showConfirm: false, // Controls the visibility of the confirmation modal
    };
  },
  methods: {
    confirmDelete() {
      this.showConfirm = true; // Show the confirmation modal
    },
    cancelDelete() {
      this.showConfirm = false; // Hide the confirmation modal
    },
    deleteChild() {
      // Emit an event to notify the parent component about the deletion
      this.$emit("delete-child", this.studentId);
      this.showConfirm = false; // Hide the confirmation modal
    },
  },
};
</script>

<style scoped>
/* Additional styles if needed */
</style>
