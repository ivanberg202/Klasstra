<!-- TeacherDashboard.vue -->
<template>
  <div class="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
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

        <!-- Main Content -->
        <div v-else>
          <!-- Classes Section -->
          <section>
            <h2 class="text-xl font-semibold mb-4">Your Classes</h2>

            <!-- Existing Classes List -->
            <div v-if="classes && classes.length > 0" class="grid gap-4">
              <div
                v-for="classItem in classes"
                :key="classItem.id"
                class="p-4 bg-white dark:bg-gray-800 rounded shadow text-gray-900 dark:text-gray-100 flex justify-between items-center"
              >
                <div>
                  <h3 class="text-lg font-medium">{{ classItem.class_name }}</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    School: {{ classItem.school_name }}
                  </p>
                </div>
                <button
                  @click="removeClassAssignment(classItem.id)"
                  class="py-1 px-3 bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg focus:outline-none transition"
                >
                  Remove
                </button>
              </div>
            </div>

            <!-- No Classes Message -->
            <div v-else class="flex flex-col items-center justify-center py-10">
              <p class="text-gray-500 dark:text-gray-400 mb-4">
                No classes found. Please use the dropdown to select and add the classes you teach.
              </p>
            </div>
          </section>

          <!-- Classes Selection -->
          <div class="mt-6">
            <ClassSelector
              v-model:selectedClassId="selectedClassId"
              :classes="availableClasses"
              @class-assigned="handleClassSelected"
              :isLoading="isLoadingClasses"
            />

            <button
              v-if="selectedClassId"
              @click="navigateToSelectedClass"
              class="mt-4 py-2 px-4 bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg focus:outline-none transition"
            >
              Go to Class
            </button>
          </div>

          <!-- Announcements Section -->
          <section class="mt-10">
            <h2 class="text-xl font-semibold mb-4">Announcements</h2>

            <!-- Announcements List -->
            <AnnouncementList v-if="announcements && announcements.length > 0" :announcements="announcements" />

            <!-- No Announcements Message -->
            <div v-else class="flex flex-col items-center justify-center py-10">
              <p class="text-gray-500 dark:text-gray-400 mb-4">
                There are no announcements at the moment. Stay tuned for updates!
              </p>
              <button
                @click="goToCreateAnnouncement"
                class="py-2 px-4 bg-blue-200 dark:bg-blue-700 text-blue-700 dark:text-blue-300 font-medium rounded-lg hover:bg-blue-300 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Create Announcement
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';
import AnnouncementList from '../components/AnnouncementList.vue';
import ClassSelector from '../components/ClassSelector.vue';

export default {
  name: 'TeacherDashboard',
  components: {
    AnnouncementList,
    ClassSelector,
  },
  data() {
    return {
      teacherName: '',
      classes: [],
      availableClasses: [],
      announcements: [],
      isLoading: true,
      isLoadingClasses: true,
      errorMessage: '',
      selectedClassId: '',
    };
  },
  methods: {
    async fetchDashboardData() {
      try {
        // Fetch teacher dashboard data
        const response = await api.get('/dashboard/teacher');
        this.teacherName = response.data.name || 'Teacher';
        this.announcements = response.data.announcements || [];

        // Use assigned classes for cards
        this.classes = response.data.classes || [];

        // Fetch all available classes for dropdown
        const availableClassesResponse = await api.get('/classes/unrestricted');
        this.availableClasses = availableClassesResponse.data || [];
      } catch (error) {
        console.error(error);
        this.errorMessage = 'Failed to load dashboard data. Please try again later.';
      } finally {
        this.isLoading = false;
        this.isLoadingClasses = false;
      }
    },
    goToCreateAnnouncement() {
      this.$router.push('/create-announcement');
    },
    async handleClassSelected(classId) {
      console.log('Event received in TeacherDashboard with Class ID:', classId);
      try {
        // Find the selected class in `availableClasses`
        const newClass = this.availableClasses.find(c => c.id === parseInt(classId));
        console.log('New Class Found:', newClass);

        if (newClass) {
          // Add the new class to the `classes` array
          this.classes.push({
            id: newClass.id,
            class_name: newClass.class_name,
            school_name: newClass.school_name,
          });
          console.log('Updated classes array:', this.classes);

          // Remove the class from `availableClasses`
          this.availableClasses = this.availableClasses.filter(c => c.id !== parseInt(classId));
          console.log('Updated availableClasses array:', this.availableClasses);
        } else {
          console.error('Class not found in availableClasses');
        }

        // Show alert only once here
        alert('Class successfully assigned!');
      } catch (error) {
        console.error('Error handling class assignment:', error);
        alert('Failed to assign class. Please try again.');
      }
    },
    async removeClassAssignment(classId) {
      try {
        await api.delete(`/teacher-class-assignments/${classId}`);
        // Remove class from `classes`
        this.classes = this.classes.filter(c => c.id !== classId);
        console.log('Removed class with ID:', classId);

        // Optionally, add it back to availableClasses
        // Find the removed class details from the deleted class assignment
        // This assumes you have the class details; otherwise, you might need to fetch them
        // For simplicity, let's assume the backend returns the class details upon deletion

        // If not, you might need to refetch or have another way to get the class details
        // Here, we'll skip adding it back to `availableClasses` automatically

        alert('Class assignment removed successfully!');
      } catch (error) {
        console.error('Error removing class:', error);
        alert('Failed to remove class assignment. Please try again.');
      }
    },
    navigateToSelectedClass() {
      if (this.selectedClassId) {
        this.$router.push(`/classes/${this.selectedClassId}`);
      }
    },
  },
  created() {
    this.fetchDashboardData();
  },
};
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
