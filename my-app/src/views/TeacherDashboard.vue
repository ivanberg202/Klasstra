<template>
    <div class="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
      <Navbar />
      <!-- Container matching Navbar -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <!-- Top Section: Welcome and Create Announcement -->
          <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold">Welcome, {{ teacherName }}!</h1>
            <!-- Create Announcement Button -->
            <button
              @click="goToCreateAnnouncement"
              class="py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg focus:outline-none transition"
            >
              Create Announcement
            </button>
          </div>
  
          <!-- Error Message -->
          <div v-if="errorMessage" class="text-center text-red-500 dark:text-red-400 mb-4">
            {{ errorMessage }}
          </div>
  
          <!-- Loading Indicator -->
          <div v-if="isLoading" class="text-center text-gray-500 dark:text-gray-400">
            Loading dashboard data...
          </div>
  
          <!-- Classes Section -->
          <section v-else>
            <h2 class="text-xl font-semibold mb-4">Your Classes</h2>
            <div v-if="classes && classes.length > 0" class="grid gap-4">
              <div
                v-for="classItem in classes"
                :key="classItem.id"
                class="p-4 bg-white dark:bg-gray-800 rounded shadow text-gray-900 dark:text-gray-100"
              >
                <h3 class="text-lg font-medium">{{ classItem.name }}</h3>
              </div>
            </div>
            <p v-else class="text-gray-500 dark:text-gray-400">You are not assigned to any classes.</p>
          </section>
  
          <!-- Announcements Section -->
          <section class="mt-10">
            <h2 class="text-xl font-semibold mb-4">Announcements</h2>
            <div v-if="announcements && announcements.length > 0" class="grid gap-4">
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
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import Navbar from '../components/Navbar.vue';
  import api from '../api';
  
  export default {
    name: 'TeacherDashboard',
    components: {
      Navbar,
    },
    data() {
      return {
        teacherName: '',
        classes: [], // Initialize as an empty array
        announcements: [], // Initialize as an empty array
        isLoading: true,
        errorMessage: '',
      };
    },
    methods: {
      async fetchDashboardData() {
        try {
          const response = await api.get('/dashboard/teacher');
          this.teacherName = response.data.name;
          this.classes = response.data.classes || []; // Safeguard against undefined
          this.announcements = response.data.announcements || []; // Safeguard against undefined
        } catch (error) {
          console.error(error);
          this.errorMessage = 'Failed to load dashboard data. Please try again later.';
        } finally {
          this.isLoading = false;
        }
      },
      goToCreateAnnouncement() {
        this.$router.push('/create-announcement');
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
  