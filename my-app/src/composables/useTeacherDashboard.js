// useTeacherDashboard.js
import { ref } from 'vue'
import api from '../api'

export function useTeacherDashboard() {
  const teacherName = ref('')
  const classes = ref([])
  const availableClasses = ref([])
  const announcements = ref([])
  const isLoading = ref(false)
  const errorMessage = ref('')

  async function fetchDashboardData() {
    isLoading.value = true
    try {
      const response = await api.get('/dashboard/teacher')
      teacherName.value = response.data.name || 'Teacher'
      classes.value = response.data.classes || []
      availableClasses.value = response.data.available_classes || []
    } catch (error) {
      console.error('Error fetching teacher dashboard data:', error)
      errorMessage.value = 'Failed to load dashboard data. Please try again later.'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAnnouncements() {
    try {
      const classIds = classes.value.map(c => c.id)
      if (classIds.length === 0) {
        announcements.value = []
        return
      }

      const params = new URLSearchParams()
      classIds.forEach(id => params.append('class_ids', id))

      const response = await api.get(`/announcements?${params.toString()}`)
      announcements.value = response.data || []
    } catch (error) {
      console.error('Error fetching announcements:', error)
      errorMessage.value = 'Failed to load announcements. Please try again later.'
    }
  }

  return {
    teacherName,
    classes,
    availableClasses,
    announcements,
    isLoading,
    errorMessage,
    fetchDashboardData,
    fetchAnnouncements,
  }
}
