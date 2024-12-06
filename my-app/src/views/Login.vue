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
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api'; // Axios instance for API calls
  
  export default {
    data() {
      return {
        username: '',
        password: '',
        isDarkMode: false,
      };
    },
    methods: {
        async login() {
            try {
                // Create form data for application/x-www-form-urlencoded
                const formData = new URLSearchParams();
                formData.append('username', this.username);
                formData.append('password', this.password);
                formData.append('grant_type', 'password');

                // Send form data to the backend
                const response = await api.post('/token', formData);

                const { access_token } = response.data;

                // Decode the token to get user details
                const payload = JSON.parse(atob(access_token.split('.')[1]));

                // Store the token, role, and first_name
                localStorage.setItem('token', access_token);
                localStorage.setItem('role', payload.role);
                localStorage.setItem('first_name', payload.first_name);

                // Redirect based on role
                this.redirectToDashboard(payload.role);
            } catch (error) {
                console.error('Login failed:', error);
                alert('Invalid username or password. Please try again.');
            }
            },
      redirectToDashboard(role) {
        const roleToDashboard = {
          parent: '/parent-dashboard',
          teacher: '/teacher-dashboard',
          admin: '/admin-dashboard',
        };
  
        if (roleToDashboard[role]) {
          this.$router.push(roleToDashboard[role]);
        } else {
          // Notify the user and clear the token if the role is unsupported
          alert(
            `Your role "${role}" is not supported in this application. Please contact support.`
          );
          localStorage.clear();
        }
      },
      toggleDarkMode() {
        this.isDarkMode = !this.isDarkMode;
        const html = document.documentElement;
        if (this.isDarkMode) {
          html.classList.add('dark');
          localStorage.setItem('theme', 'dark');
        } else {
          html.classList.remove('dark');
          localStorage.setItem('theme', 'light');
        }
      },
    },
    created() {
      // Initialize dark mode based on localStorage or system preference
      const savedTheme = localStorage.getItem('theme');
      this.isDarkMode =
        savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },
  };
  </script>
  
  <style scoped>
  /* Ensure no margins or extra space */
  html,
  body {
    margin: 0;
    padding: 0;
    height: 100%;
    width: 100%;
    overflow: hidden;
  }
  
  .flex {
    box-sizing: border-box; /* Ensure the element respects width/height */
  }
  
  .absolute {
    z-index: 10; /* Ensure the button is on top of all elements */
  }
  </style>
  