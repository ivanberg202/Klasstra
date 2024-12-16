<template>
  <div class="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="py-6">
        <ErrorMessage :message="errorMessage" />
        <LoadingIndicator v-if="isLoading" />
        <template v-else>
          <!-- Top Section: Welcome and Create Announcement -->
          <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold">Welcome, {{ teacherName }}!</h1>
            <button
              @click="goToCreateAnnouncement"
              class="py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg focus:outline-none transition"
            >
              Create Announcement
            </button>
          </div>

          <!-- Classes Section -->
          <section>
            <h2 class="text-xl font-semibold mb-4">Your Classes</h2>
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
            <div v-else class="flex flex-col items-center justify-center py-10">
              <p class="text-gray-500 dark:text-gray-400 mb-4">
                No classes found. Please use the dropdown to select and add the classes you teach.
              </p>
            </div>
          </section>

          <!-- Class Selector -->
          <div class="mt-6">
            <ClassSelector
              v-model:selectedClassId="selectedClassId"
              :classes="availableClasses"
              @class-assigned="handleClassSelected"
              :isLoading="false"
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
            <AnnouncementList v-if="announcements && announcements.length > 0" :announcements="announcements" />
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
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTeacherDashboard } from '../composables/useTeacherDashboard'
import AnnouncementList from '../components/AnnouncementList.vue'
import ClassSelector from '../components/ClassSelector.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import LoadingIndicator from '../components/LoadingIndicator.vue'
import api from '../api'

export default {
  name: 'TeacherDashboard',
  components: {
    AnnouncementList,
    ClassSelector,
    ErrorMessage,
    LoadingIndicator,
  },
  setup() {
    const {
      teacherName,
      classes,
      availableClasses,
      announcements,
      isLoading,
      errorMessage,
      fetchDashboardData,
      fetchAnnouncements,
    } = useTeacherDashboard()

    const selectedClassId = ref('')
    const router = useRouter()
    const isProcessing = ref(false)

    function handleApiError(error, actionDescription) {
      console.error(`${actionDescription} failed:`, error)
      if (error.response) {
        if (error.response.status === 401) {
          alert('Unauthorized. Please log in again.')
          router.push('/login')
        } else if (error.response.status === 404) {
          alert('Resource not found.')
        } else {
          alert(`Error: ${error.response.data?.detail || 'Something went wrong. Please try again.'}`)
        }
      } else {
        alert('Network error. Please check your internet connection.')
      }
    }

    async function handleClassSelected(classId) {
      if (isProcessing.value) return
      isProcessing.value = true
      try {
        const newClass = availableClasses.value.find(c => c.id === parseInt(classId))
        if (!newClass) {
          alert('Class not found in available classes.')
          return
        }

        // Assign the class to the teacher via API
        await api.post('/teacher-class-assignments', { class_id: parseInt(classId) })

        // Update local state
        classes.value.push(newClass)
        availableClasses.value = availableClasses.value.filter(c => c.id !== parseInt(classId))

        // Fetch announcements again since the class list changed
        await fetchAnnouncements()
        alert('Class successfully assigned!')
      } catch (error) {
        handleApiError(error, 'Assigning class')
      } finally {
        isProcessing.value = false
      }
    }

    async function removeClassAssignment(classId) {
      if (isProcessing.value) return
      isProcessing.value = true
      try {
        await api.delete(`/teacher-class-assignments/${classId}`)
        const removedClass = classes.value.find(c => c.id === classId)
        classes.value = classes.value.filter(c => c.id !== classId)

        if (removedClass) {
          availableClasses.value.push(removedClass)
        }

        await fetchAnnouncements()
        alert('Class assignment removed successfully!')
      } catch (error) {
        handleApiError(error, 'Removing class assignment')
      } finally {
        isProcessing.value = false
      }
    }

    function navigateToSelectedClass() {
      if (selectedClassId.value) {
        router.push(`/classes/${selectedClassId.value}`)
        selectedClassId.value = ''
      }
    }

    function goToCreateAnnouncement() {
      router.push('/create-announcement')
    }

    onMounted(async () => {
      console.log('TeacherDashboard mounted, checking token...')
      const token = localStorage.getItem('access_token')
      if (!token) {
        console.error('No token found. Redirecting to login.')
        router.push('/login')
        return
      }

      console.log('Token found, fetching teacher dashboard data...')
      try {
        await fetchDashboardData()
        await fetchAnnouncements()
      } catch (error) {
        handleApiError(error, 'Fetching teacher dashboard data')
      }
    })

    return {
      teacherName,
      classes,
      availableClasses,
      announcements,
      isLoading,
      errorMessage,
      selectedClassId,
      handleClassSelected,
      removeClassAssignment,
      navigateToSelectedClass,
      goToCreateAnnouncement,
    }
  },
}
</script>
