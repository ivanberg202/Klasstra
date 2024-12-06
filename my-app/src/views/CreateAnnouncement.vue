<template>
    <div class="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
      <Navbar />
      <!-- Container matching Navbar -->
      <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <h1 class="text-2xl font-bold mb-6">Create New Announcement</h1>
          <form @submit.prevent="createAnnouncement">
            <!-- Title Input -->
            <div class="mb-4">
              <label class="block text-sm font-medium mb-1">Title</label>
              <input
                v-model="title"
                type="text"
                class="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                required
              />
            </div>
            <!-- Content Input -->
            <div class="mb-4">
              <label class="block text-sm font-medium mb-1">Content</label>
              <textarea
                v-model="content"
                rows="5"
                class="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                required
              ></textarea>
            </div>
            <!-- Class Selection -->
            <div class="mb-6">
              <label class="block text-sm font-medium mb-1">Select Class</label>
              <select
                v-model="selectedClass"
                class="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200"
                required
              >
                <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
                  {{ classItem.name }}
                </option>
              </select>
            </div>
            <!-- Submit Button -->
            <button
              type="submit"
              class="py-3 px-6 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition"
            >
              Create Announcement
            </button>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import Navbar from '../components/Navbar.vue';
  import api from '../api';
  
  export default {
    name: 'CreateAnnouncement',
    components: {
      Navbar,
    },
    data() {
      return {
        title: '',
        content: '',
        selectedClass: null,
        classes: [],
      };
    },
    methods: {
      async fetchClasses() {
        try {
            console.log('Fetching classes...');
            const response = await api.get('/classes/my-classes');
            console.log('API response:', response);

            this.classes = response.data || [];
            console.log('Classes array:', this.classes);

            if (this.classes.length > 0) {
            this.selectedClass = this.classes[0].id;
            console.log('Default selected class ID:', this.selectedClass);
            } else {
            console.warn('No classes returned for the current user.');
            }
        } catch (error) {
            console.error('Error fetching classes:', error);
            alert('Failed to load classes.');
        }
        },
      async createAnnouncement() {
        try {
          // Prepare the payload according to AnnouncementCreate schema
          const payload = {
            title: this.title,
            content_en: this.content,
            class_id: this.selectedClass,
            target_audience: 'parents', // Adjust based on your use case
            original_language: 'en', // Default to English
            // Optional fields:
            // content_de: null,
            // content_fr: null,
            // recipients: [], // Add specific recipients if needed
          };
  
          await api.post('/announcements/create', payload);
          alert('Announcement created successfully!');
          this.$router.push('/teacher-dashboard');
        } catch (error) {
          console.error(error);
          alert('Failed to create announcement.');
        }
      },
    },
    created() {
      this.fetchClasses();
    },
  };
  </script>
  
  <style scoped>
  /* Additional styles if needed */
  </style>
  