<!-- src/views/Register.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 relative">
    <DarkModeToggle :isDarkMode="isDarkMode" @toggle-dark-mode="toggleDarkMode" />

    <form @submit.prevent="handleRegister" class="bg-white dark:bg-gray-800 p-6 rounded shadow-md w-full max-w-md">
      <h2 class="text-2xl font-bold mb-4 text-center text-gray-800 dark:text-gray-100">Register</h2>

      <!-- User Base Fields (required) -->
      <UserBaseFields v-model="userBase" />

      <!-- Debugging: Display userBase -->
      <!-- <pre class="bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded p-2 mt-2">{{ JSON.stringify(userBase, null, 2) }}</pre> -->

      <!-- Error Message -->
      <div v-if="errorMessage" class="text-center text-red-500 dark:text-red-400 mb-4">
        {{ errorMessage }}
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ isSubmitting ? 'Registering...' : 'Register' }}
      </button>

      <!-- Login Redirect -->
      <p class="mt-4 text-center text-gray-700 dark:text-gray-200">
        Already have an account?
        <router-link to="/login" class="text-blue-500 hover:underline">Login here</router-link>
      </p>
    </form>
  </div>
</template>

<script>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';
import { useDarkMode } from '../composables/useDarkMode'; 
import DarkModeToggle from '../components/DarkModeToggle.vue';
import UserBaseFields from '../components/UserBaseFields.vue';

export default {
  name: 'Register',
  components: {
    DarkModeToggle,
    UserBaseFields,
  },
  setup() {
    const { registerUser, autoLogin, redirectToDashboard } = useAuth();
    const { isDarkMode, toggleDarkMode } = useDarkMode();
    const router = useRouter();

    // State for core user data
    const userBase = ref({
      username: '',
      email: '',
      password: '',
      role: '', // admin, teacher, parent
    });

    const isSubmitting = ref(false);
    const errorMessage = ref('');

    watch(userBase, (newVal) => {
      console.log('userBase updated:', newVal);
    }, { deep: true });

    async function handleRegister() {
      // Basic Validation
      if (!userBase.value.username || !userBase.value.email || !userBase.value.password || !userBase.value.role) {
        errorMessage.value = 'Please fill in all required fields.';
        return;
      }

      isSubmitting.value = true;
      errorMessage.value = '';

      try {
        // Prepare user data payload
        const userData = {
          username: userBase.value.username,
          email: userBase.value.email,
          password: userBase.value.password,
          role: userBase.value.role,
        };

        // Register user with minimal data
        await registerUser(userData);

        // Auto-login after successful registration
        await autoLogin(userBase.value.username, userBase.value.password);

        // Redirect to the appropriate dashboard
        redirectToDashboard(router, userBase.value.role);

        // Note: Parents will add children or Teachers will add classes
        // after this step on their own dashboards or a separate route.
      } catch (error) {
        console.error(error);
        if (error.response && error.response.data && error.response.data.detail) {
          errorMessage.value = error.response.data.detail;
        } else {
          errorMessage.value = 'Registration failed. Please try again.';
        }
      } finally {
        isSubmitting.value = false;
      }
    }

    return {
      userBase,
      isDarkMode,
      toggleDarkMode,
      handleRegister,
      isSubmitting,
      errorMessage,
    };
  },
};
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
