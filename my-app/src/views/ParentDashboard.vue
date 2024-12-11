<!-- ParentDashboard.vue -->
<template>
  <div class="bg-gray-100 dark:bg-gray-900 min-h-screen text-gray-900 dark:text-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="py-6">
        <ErrorMessage :message="errorMessage" />
        <LoadingIndicator v-if="isLoading" />

        <template v-else>
          <!-- Children Section -->
          <section class="mt-10">
            <ChildrenList
              :children="children"
              :classesList="classesList"
              :addChildFormVisible="addChildFormVisible"
              :selectedClassId="childClassId"
              @update:selectedClassId="childClassId = $event"
              @show-add-form="addChildFormVisible = true"
              @hide-add-form="cancelAddChild"
              @add-child="handleAddChild"
              @delete-child="handleDeleteChild"
            />
          </section>

            <!-- Announcements Section -->
            <section class="mt-10">
              <h2 class="text-lg font-semibold mb-4">Announcements</h2>
              <template v-if="announcements.length > 0">
                <AnnouncementList :announcements="announcements" />
              </template>
              <template v-else>
                <p class="text-gray-500">No announcements available.</p>
                <p class="text-gray-500">Add a child to see the announcements of their class.</p>
              </template>
            </section>


        </template>
      </div>
    </div>
  </div>
</template>

<script>
import ChildrenList from '../components/ChildrenList.vue';
import AnnouncementList from '../components/AnnouncementList.vue';
import ErrorMessage from '../components/ErrorMessage.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import { useParentDashboard } from '../composables/useParentDashboard';
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

export default {
  name: 'ParentDashboard',
  components: {
    AnnouncementList,
    ChildrenList,
    ErrorMessage,
    LoadingIndicator,
  },
  setup() {
    const {
      announcements,
      children,
      classesList,
      isLoading,
      errorMessage,
      fetchDashboardData,
      fetchClassesForSelection,
      addChild,
    } = useParentDashboard();

    const addChildFormVisible = ref(false);
    const childClassId = ref('');
    const isProcessing = ref(false);
    const router = useRouter();

    function handleApiError(error, actionDescription) {
      console.error(`${actionDescription} failed:`, error);
      if (error.response) {
        if (error.response.status === 401) {
          alert('Unauthorized. Please log in again.');
          router.push('/login');
        } else if (error.response.status === 404) {
          alert('Resource not found.');
        } else {
          alert(`Error: ${error.response.data?.detail || 'Something went wrong. Please try again.'}`);
        }
      } else {
        alert('Network error. Please check your internet connection.');
      }
    }

    async function handleDeleteChild(studentId) {
      if (isProcessing.value) return;
      isProcessing.value = true;
      try {
        await api.delete(`/users/parent/delete_child/${studentId}`);
        children.value = children.value.filter((child) => child.id !== studentId);
        alert('Child deleted successfully.');
      } catch (error) {
        handleApiError(error, 'Deleting child');
      } finally {
        isProcessing.value = false;
      }
    }

    async function handleAddChild(payload) {
      if (isProcessing.value) return;
      isProcessing.value = true;
      try {
        await addChild(payload);
        addChildFormVisible.value = false;
      } catch (error) {
        handleApiError(error, 'Adding child');
      } finally {
        isProcessing.value = false;
      }
    }

    function cancelAddChild() {
      addChildFormVisible.value = false;
    }

    onMounted(async () => {
    console.log('ParentDashboard mounted, checking token...');
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No token found. Redirecting to login.');
      router.push('/login');
      return;
    }

    console.log('Token found, fetching dashboard data...');
    try {
      await fetchDashboardData();
      await fetchClassesForSelection();

      // Debugging the result of the fetch
      console.log('Classes list after fetching:', classesList.value);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      handleApiError(error, 'Fetching dashboard data');
    }
  });


    return {
      announcements,
      children,
      classesList,
      isLoading,
      errorMessage,
      addChildFormVisible,
      childClassId,
      handleAddChild,
      cancelAddChild,
      handleDeleteChild,
    };
  },
};
</script>
