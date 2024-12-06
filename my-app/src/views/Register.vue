<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-100">
      <form @submit.prevent="register" class="bg-white p-6 rounded shadow-md w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4 text-center">Register</h2>
  
        <!-- Username -->
        <div class="mb-4">
          <label class="block text-gray-700 mb-1">Username</label>
          <input
            v-model="username"
            type="text"
            class="w-full p-2 border rounded focus:outline-none focus:ring"
            required
          />
        </div>
  
        <!-- Email -->
        <div class="mb-4">
          <label class="block text-gray-700 mb-1">Email</label>
          <input
            v-model="email"
            type="email"
            class="w-full p-2 border rounded focus:outline-none focus:ring"
            required
          />
        </div>
  
        <!-- Password -->
        <div class="mb-4">
          <label class="block text-gray-700 mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            class="w-full p-2 border rounded focus:outline-none focus:ring"
            required
          />
        </div>
  
        <!-- Role -->
        <div class="mb-6">
          <label class="block text-gray-700 mb-1">Role</label>
          <select
            v-model="role"
            class="w-full p-2 border rounded focus:outline-none focus:ring"
            required
          >
            <option value="" disabled>Select your role</option>
            <option value="parent">Parent</option>
            <option value="teacher">Teacher</option>
            <option value="class_representative">Class Representative</option>
          </select>
        </div>
  
        <!-- Submit Button -->
        <button
          type="submit"
          class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 transition"
        >
          Register
        </button>
  
        <!-- Login Redirect -->
        <p class="mt-4 text-center">
          Already have an account?
          <router-link to="/login" class="text-blue-500 hover:underline">Login here</router-link>
        </p>
      </form>
    </div>
  </template>
  
  <script>
  import api from '../api'; // Axios instance for backend calls
  
  export default {
    name: 'Register',
    data() {
      return {
        username: '',
        email: '',
        password: '',
        role: '',
      };
    },
    methods: {
      async register() {
        try {
          const userData = {
            username: this.username,
            email: this.email,
            password: this.password,
            role: this.role,
          };
  
          // Make API call to register the user
          await api.post('/auth/register', userData);
  
          alert('Registration successful! Please log in.');
          this.$router.push('/login');
        } catch (error) {
          console.error(error);
          alert('Registration failed. Please try again.');
        }
      },
    },
  };
  </script>
  
  <style scoped>
  /* Component-specific styles */
  </style>
  