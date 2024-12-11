<!-- src/components/StudentFields.vue -->
<template>
    <div>
      <div
        v-for="(student, index) in localStudents"
        :key="index"
        class="mb-4 p-4 border border-gray-300 dark:border-gray-700 rounded"
      >
        <h4 class="text-lg font-semibold mb-2">Child {{ index + 1 }}</h4>
  
        <div class="mb-2">
          <label class="block text-sm font-medium mb-1 text-gray-800 dark:text-gray-100">First Name</label>
          <input
            v-model="student.first_name"
            type="text"
            class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            required
          />
        </div>
  
        <div class="mb-2">
          <label class="block text-sm font-medium mb-1 text-gray-800 dark:text-gray-100">Last Name</label>
          <input
            v-model="student.last_name"
            type="text"
            class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            required
          />
        </div>
  
        <div class="mb-2">
          <label class="block text-sm font-medium mb-1 text-gray-800 dark:text-gray-100">Class</label>
          <select
            v-model="student.class_id"
            class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            required
          >
            <option disabled value="">Please select a class</option>
            <option v-for="cls in classes" :key="cls.id" :value="cls.id">
              {{ cls.name }}
            </option>
          </select>
        </div>
  
        <button
          type="button"
          @click="removeStudent(index)"
          class="mt-2 text-red-500 hover:text-red-700"
        >
          Remove Child
        </button>
      </div>
  
      <button
        type="button"
        @click="addStudent"
        class="w-full bg-green-500 text-white p-2 rounded hover:bg-green-600 transition"
      >
        Add Another Child
      </button>
    </div>
  </template>
  
  <script>
  import api from '../api'; // Adjust the path as necessary
  
  export default {
    name: 'StudentFields',
    props: {
      modelValue: {
        type: Array,
        default: () => [],
      },
    },
    data() {
      return {
        localStudents: [...this.modelValue],
        classes: [],
      };
    },
    watch: {
      localStudents: {
        handler(newVal) {
          console.log('students updated:', newVal);
          this.$emit('update:modelValue', newVal);
        },
        deep: true,
      },
      modelValue: {
        handler(newVal) {
          this.localStudents = [...newVal];
        },
        deep: true,
      },
    },
    methods: {
      async fetchClasses() {
        try {
          const response = await api.get('/classes/unrestricted');
          this.classes = response.data;
          console.log('Fetched classes:', this.classes);
        } catch (error) {
          console.error('Error fetching classes:', error);
          alert('Failed to load classes.');
        }
      },
      addStudent() {
        this.localStudents.push({
          first_name: '',
          last_name: '',
          class_id: '',
        });
        console.log('Added a new student:', this.localStudents[this.localStudents.length - 1]);
      },
      removeStudent(index) {
        const removed = this.localStudents.splice(index, 1);
        console.log('Removed student:', removed[0]);
      },
    },
    created() {
      this.fetchClasses();
    },
  };
  </script>
  
  <style scoped>
  /* Add any component-specific styles here */
  </style>
  