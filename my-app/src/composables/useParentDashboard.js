// useParentDashboard.js

import { ref } from 'vue';
import api from '../api';

export function useParentDashboard() {
  const announcements = ref([]);
  const children = ref([]);
  const classesList = ref([]);
  const isLoading = ref(true);
  const errorMessage = ref('');

  async function fetchDashboardData() {
    const token = localStorage.getItem('access_token');
    console.log('useParentDashboard.js: Retrieved token before fetching dashboard:', token);
  
    if (!token) {
      console.error('useParentDashboard.js: Cannot fetch dashboard data: Token is missing.');
      errorMessage.value = 'Authentication token is missing. Please log in again.';
      isLoading.value = false;
      return;
    }
  
    console.log('useParentDashboard.js: Fetching dashboard data with token:', token);
    try {
      const response = await api.get('/dashboard/parent');
      console.log('useParentDashboard.js: Dashboard data received:', response.data);
      
      // Map announcements to ensure 'content' is defined
      if (Array.isArray(response.data.announcements)) {
        announcements.value = response.data.announcements.map((announcement) => ({
          ...announcement,
          content: announcement.content || announcement.content_en || announcement.content_de || announcement.content_fr || 'No content available.',
        }));
        console.log('Mapped announcements with content:', announcements.value);
      } else {
        console.warn('useParentDashboard.js: Announcements data is not an array.');
        announcements.value = [];
      }

      children.value = response.data.students || [];
      console.log('Children updated:', children.value);
    } catch (error) {
      console.error('useParentDashboard.js: Error fetching dashboard data:', error);
      if (error.response) {
        console.error('useParentDashboard.js: Response status:', error.response.status);
        console.error('useParentDashboard.js: Response data:', error.response.data);
      } else {
        console.error('useParentDashboard.js: Network or unknown error:', error.message);
      }
      errorMessage.value = 'Failed to load dashboard data. Please try again later.';
    } finally {
      isLoading.value = false;
    }
  }
  
  async function fetchClassesForSelection() {
    try {
      const response = await api.get('/classes/unrestricted'); // Use the new endpoint
      classesList.value = response.data;
      console.log('Fetched unrestricted classes:', classesList.value);
    } catch (error) {
      console.error('Error fetching unrestricted classes:', error);
      throw error;
    }
  }

  async function addChild({ first_name, last_name, class_id }) {
    const payload = { first_name, last_name, class_id: parseInt(class_id, 10) };
    await api.post('/users/parent/add_child', payload);
    // After adding, refresh children
    await fetchDashboardData();
  }

  return {
    announcements,
    children,
    classesList,
    isLoading,
    errorMessage,
    fetchDashboardData,
    fetchClassesForSelection,
    addChild
  };
}
