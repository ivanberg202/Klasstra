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
import api from '../api'; // Ensure this points to your Axios instance
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
  created() {
    console.log('TeacherDashboard component created.');
    this.initializeDashboard();
  },
  methods: {
    async initializeDashboard() {
      try {
        console.log('Initializing dashboard...');
        await this.fetchDashboardData();
        await this.fetchAnnouncements();
        console.log('Dashboard initialized successfully.');
      } catch (error) {
        console.error('Error initializing dashboard:', error);
        this.errorMessage = 'Failed to initialize dashboard. Please try again later.';
      }
    },
    async fetchDashboardData() {
      try {
        console.log('Fetching teacher dashboard data...');
        const response = await api.get('/dashboard/teacher');
        console.log('Dashboard data fetched:', response.data);

        this.teacherName = response.data.name || 'Teacher';
        this.classes = response.data.classes || [];
        console.log('Classes updated:', this.classes);
        this.availableClasses = response.data.available_classes || [];
        console.log('Available classes updated:', this.availableClasses);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        this.errorMessage = 'Failed to load dashboard data. Please try again later.';
      } finally {
        this.isLoading = false;
        this.isLoadingClasses = false;
      }
    },
    async fetchAnnouncements() {
      try {
        const classIds = Array.isArray(this.classes) ? this.classes.map(c => c.id) : [];
        console.log('Class IDs for fetching announcements:', classIds);

        if (classIds.length === 0) {
          this.announcements = [];
          console.log('No classes found, skipping announcement fetch.');
          return;
        }

        const params = new URLSearchParams();
        classIds.forEach(id => params.append('class_ids', id));

        console.log('Fetching announcements for classes:', classIds);
        const response = await api.get(`/announcements?${params.toString()}`);
        console.log('Raw response data:', response.data);

        // Assign the list directly since the backend returns a list
        this.announcements = response.data || [];
        console.log('Announcements received and set:', this.announcements);
      } catch (error) {
        console.error('Error fetching announcements:', error);
        this.errorMessage = 'Failed to load announcements. Please try again later.';
      }
    },
    goToCreateAnnouncement() {
      this.$router.push('/create-announcement');
    },
    async handleClassSelected(classId) {
      console.log('Class selected:', classId);
      try {
        const newClass = this.availableClasses.find(c => c.id === parseInt(classId));
        console.log('New Class Found:', newClass);

        if (newClass) {
          this.classes.push({
            id: newClass.id,
            class_name: newClass.class_name,
            school_name: newClass.school_name,
          });
          console.log('Updated classes array:', this.classes);

          this.availableClasses = this.availableClasses.filter(c => c.id !== parseInt(classId));
          console.log('Updated availableClasses array:', this.availableClasses);
        } else {
          console.error('Class not found in availableClasses');
          return;
        }

        await this.fetchAnnouncements();
        alert('Class successfully assigned!');
      } catch (error) {
        console.error('Error handling class assignment:', error);
        alert('Failed to assign class. Please try again.');
      }
    },
    async removeClassAssignment(classId) {
      try {
        console.log(`Removing class assignment for Class ID: ${classId}`);
        await api.delete(`/teacher-class-assignments/${classId}`);
        console.log(`Deleted class assignment for Class ID: ${classId}`);

        const removedClass = this.classes.find(c => c.id === classId);
        this.classes = this.classes.filter(c => c.id !== classId);
        console.log('Updated classes array after removal:', this.classes);

        if (removedClass) {
          this.availableClasses.push({
            id: removedClass.id,
            class_name: removedClass.class_name,
            school_name: removedClass.school_name,
          });
          console.log('Added class back to availableClasses:', removedClass);
        }

        await this.fetchAnnouncements();
        alert('Class assignment removed successfully!');
      } catch (error) {
        console.error('Error removing class assignment:', error);
        alert('Failed to remove class assignment. Please try again.');
      }
    },
    navigateToSelectedClass() {
      if (this.selectedClassId) {
        this.$router.push(`/classes/${this.selectedClassId}`);
        this.selectedClassId = '';
        console.log('Navigated to class:', this.selectedClassId);
      }
    },
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
