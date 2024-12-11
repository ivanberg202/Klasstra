<template>
    <!-- Fullscreen background container -->
    <div class="flex items-center justify-center h-screen w-screen bg-gray-50 dark:bg-gray-900">
      <!-- Dark Mode Toggle Button -->
      <button
        @click="toggleDarkMode"
        class="absolute top-4 right-4 p-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded shadow"
      >
        {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
      </button>
  
      <!-- Login Card -->
      <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md w-full max-w-sm">
        <h1 class="text-2xl font-bold text-gray-800 dark:text-gray-100 text-center mb-6">
          Login
        </h1>
        <form @submit.prevent="login">
          <!-- Username Input -->
          <div class="mb-4">
            <input
              v-model="username"
              type="text"
              placeholder="Username"
              class="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              required
            />
          </div>
          <!-- Password Input -->
          <div class="mb-6">
            <input
              v-model="password"
              type="password"
              placeholder="Password"
              class="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              required
            />
          </div>
          <!-- Login Button -->
          <button
            type="submit"
            class="w-full py-3 text-white font-medium bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition"
          >
            Login
          </button>
        </form>
        <!-- Register Redirect -->
        <p class="mt-4 text-center">
          Don't have an account?
          <router-link to="/register" class="text-blue-500 hover:underline">Register here</router-link>
        </p>
      </div>
    </div>
  </template>
  
  <script>
import { ref } from 'vue';
import { useAuth } from '../composables/useAuth';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const { autoLogin, redirectToDashboard } = useAuth();
    const router = useRouter();
    const username = ref('');
    const password = ref('');
    const isDarkMode = ref(false);

    const login = async () => {
  try {
    const { token, role } = await autoLogin(username.value, password.value);
    console.log('Token stored successfully:', token);

    // Wait a short delay to ensure the token is accessible globally
    await new Promise((resolve) => setTimeout(resolve, 100));

    redirectToDashboard(router, role);
  } catch (error) {
    console.error('Login failed:', error);
    alert('Invalid username or password. Please try again.');
  }
};



    const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value;
      const html = document.documentElement;
      if (isDarkMode.value) {
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      } else {
        html.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      }
    };

    // Initialize theme
    const savedTheme = localStorage.getItem('theme');
    isDarkMode.value =
      savedTheme === 'dark' ||
      (!savedTheme &&
        window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    return {
      username,
      password,
      isDarkMode,
      login,
      toggleDarkMode,
    };
  },
};
</script>

<style scoped>
/* Existing styles */
</style>
