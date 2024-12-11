<template>
  <div class="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
    <!-- Removed Navbar to avoid duplication -->
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
            <ClassSelector
              :classes="classes"
              v-model:selectedClassId="selectedClassId"
            />
          </div>
          <!-- Action Buttons -->
          <div class="flex space-x-4">
            <button
              type="submit"
              class="py-3 px-6 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition"
            >
              Create Announcement
            </button>
            <button
              type="button"
              @click="cancel"
              class="py-3 px-6 bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500 dark:focus:ring-gray-400 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';
import ClassSelector from '../components/ClassSelector.vue';

export default {
  name: 'CreateAnnouncement',
  components: {
    ClassSelector,
  },
  data() {
    return {
      title: '',
      content: '',
      selectedClassId: '',
      classes: [],
    };
  },
  methods: {
    async fetchClasses() {
      try {
        const response = await api.get('/classes/unrestricted');
        this.classes = response.data || [];
        // If classes are returned, optionally set the first one as default
        if (this.classes.length > 0) {
          this.selectedClassId = this.classes[0].id;
        }
      } catch (error) {
        console.error('Error fetching classes:', error);
        alert('Failed to load classes.');
      }
    },
    async createAnnouncement() {
      try {
        const payload = {
          title: this.title,
          content_en: this.content,
          class_id: this.selectedClassId,
          target_audience: 'parents', // Adjust as needed
          original_language: 'en',
        };

        await api.post('/announcements/create', payload);
        alert('Announcement created successfully!');
        this.$router.push('/teacher-dashboard');
      } catch (error) {
        console.error(error);
        alert('Failed to create announcement.');
      }
    },
    cancel() {
      this.$router.push('/teacher-dashboard');
    }
  },
  created() {
    this.fetchClasses();
  },
};
</script>

<style scoped>
/* Additional styles if needed */
</style>
