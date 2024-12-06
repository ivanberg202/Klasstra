<template>
    <div class="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
      <Navbar />
  
      <!-- Start of container matching Navbar -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Main content padding -->
        <div class="py-6">
          <!-- Error Message -->
          <div v-if="errorMessage" class="text-center text-red-500 dark:text-red-400 mb-4">
            {{ errorMessage }}
          </div>
  
          <!-- Loading Indicator -->
          <div v-if="isLoading" class="text-center text-gray-500 dark:text-gray-400">
            Loading dashboard data...
          </div>
  
          <!-- Announcements Section -->
          <section v-else>
            <h2 class="text-xl font-semibold mb-4">Announcements</h2>
            <div v-if="announcements.length" class="grid gap-4">
              <div
                v-for="announcement in announcements"
                :key="announcement.id"
                class="p-4 bg-white dark:bg-gray-800 rounded shadow text-gray-900 dark:text-gray-100"
              >
                <h3 class="text-lg font-medium">{{ announcement.title }}</h3>
                <p>{{ announcement.content_en }}</p>
              </div>
            </div>
            <p v-else class="text-gray-500 dark:text-gray-400">No announcements available.</p>
          </section>
  
          <!-- Children's Details Section -->
          <section class="mt-10">
            <h2 class="text-xl font-semibold mb-4">Your Children</h2>
            <div v-if="children.length" class="grid gap-4">
              <div
                v-for="child in children"
                :key="child.id"
                class="p-4 bg-white dark:bg-gray-800 rounded shadow text-gray-900 dark:text-gray-100"
              >
                <h3 class="text-lg font-medium">{{ child.first_name }} {{ child.last_name }}</h3>
                <p>Class: {{ child.class.name }}</p>
              </div>
            </div>
            <p v-else class="text-gray-500 dark:text-gray-400">No children information available.</p>
          </section>
        </div>
      </div>
      <!-- End of container -->
    </div>
  </template>
  
  <script>
  import api from '../api';
  import Navbar from '../components/Navbar.vue';
  
  export default {
    name: 'ParentDashboard',
    components: {
      Navbar,
    },
    data() {
      return {
        announcements: [],
        children: [],
        isLoading: true,
        errorMessage: '',
      };
    },
    methods: {
      async fetchDashboardData() {
        try {
          const response = await api.get('/dashboard/parent');
          this.announcements = response.data.announcements;
          this.children = response.data.students;
        } catch (error) {
          console.error(error);
          this.errorMessage = 'Failed to load dashboard data. Please try again later.';
        } finally {
          this.isLoading = false;
        }
      },
    },
    created() {
      this.fetchDashboardData();
    },
  };
  </script>
  
  <style scoped>
  /* Additional styles if needed */
  </style>
  