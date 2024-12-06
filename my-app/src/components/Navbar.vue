<template>
    <nav class="bg-white dark:bg-gray-800 shadow w-full">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Left Side -->
          <div class="text-2xl font-bold text-gray-800 dark:text-gray-100">
            <router-link to="/" class="hover:underline">
              Class App
            </router-link>
          </div>
  
          <!-- Right Side -->
          <div class="flex items-center space-x-4">
            <!-- User's Name Display -->
            <div class="text-gray-800 dark:text-gray-100">
              Hello, {{ userName }}!
            </div>
  
            <!-- Dark Mode Toggle Button -->
            <button
              @click="toggleDarkMode"
              class="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none"
            >
              <span v-if="isDarkMode">
                <!-- Sun Icon -->
                <svg class="h-6 w-6 text-gray-800 dark:text-gray-100" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    d="M10 2a1 1 0 011 1v2a1 1 0 11-2 0V3a1 1 0 011-1zM4.22 4.22a1 1 0 011.42 0l1.42 1.42a1 1 0 11-1.42 1.42L4.22 5.64a1 1 0 010-1.42zM2 10a1 1 0 011-1h2a1 1 0 110 2H3a1 1 0 01-1-1zm9 7a1 1 0 11-2 0v-2a1 1 0 112 0v2zm4.78-1.78a1 1 0 10-1.42-1.42l-1.42 1.42a1 1 0 001.42 1.42l1.42-1.42zM17 10a1 1 0 100-2h-2a1 1 0 100 2h2zm-5-7a1 1 0 00-1 1v2a1 1 0 102 0V4a1 1 0 00-1-1zm3.78 3.78a1 1 0 10-1.42-1.42l-1.42 1.42a1 1 0 001.42 1.42l1.42-1.42zM5.64 14.36a1 1 0 00-1.42 1.42l1.42 1.42a1 1 0 001.42-1.42l-1.42-1.42z"
                  />
                </svg>
              </span>
              <span v-else>
                <!-- Moon Icon -->
                <svg class="h-6 w-6 text-gray-800 dark:text-gray-100" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    d="M10 2a8 8 0 016.32 12.9A8 8 0 117.1 3.68 7.93 7.93 0 0110 2z"
                  />
                </svg>
              </span>
            </button>
  
            <!-- Logout Button -->
            <button
              @click="logout"
              class="py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded focus:outline-none transition"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  </template>
  
  <script>
  export default {
    name: 'Navbar',
    data() {
      return {
        isDarkMode: false,
      };
    },
    computed: {
      userName() {
        // Retrieve first_name from localStorage
        return localStorage.getItem('first_name') || 'User';
      },
    },
    methods: {
      toggleDarkMode(event) {
        this.isDarkMode = !this.isDarkMode;
        document.documentElement.classList.toggle('dark', this.isDarkMode);
        localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
  
        // Remove focus immediately after clicking
        event.target.blur();
      },
      logout() {
        localStorage.clear();
        this.$router.push('/login');
      },
    },
    created() {
      const savedTheme = localStorage.getItem('theme');
      this.isDarkMode =
        savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
      document.documentElement.classList.toggle('dark', this.isDarkMode);
    },
  };
  </script>
  
  <style scoped>
  nav {
    width: 100%;
  }
  </style>
  