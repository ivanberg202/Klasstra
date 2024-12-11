// src/composables/useAuth.js
import { ref } from 'vue';
import api from '../api';
import { base64UrlDecode } from '../utils/base64UrlDecode'; // Import the decoding function

export function useAuth() {
  const token = ref(null);
  const role = ref(null);
  const firstName = ref(null);

  async function registerUser(userData) {
    // Attempt registration
    await api.post('/auth/register', userData);
  }

  async function autoLogin(username, password) {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      formData.append('grant_type', 'password');
  
      const response = await api.post('/token', formData);
      const { access_token } = response.data;
  
      console.log('Storing token in localStorage...');
      localStorage.setItem('access_token', access_token); // Use "access_token" as the key
      console.log('Token stored in localStorage:', localStorage.getItem('access_token')); // Verify storage
  
      // Decode the token to extract role and other details
      console.log('Decoding token...');
      const payload = JSON.parse(base64UrlDecode(access_token.split('.')[1]));
      console.log('Decoded payload:', payload);
  
      const userRole = payload.role;
      const firstNameFromToken = payload.first_name || 'User';
  
      // Store additional details in localStorage
      localStorage.setItem('role', userRole);
      localStorage.setItem('firstName', firstNameFromToken);
  
      console.log('Role and first name stored in localStorage:', { userRole, firstNameFromToken });
  
      return { token: access_token, role: userRole };
    } catch (error) {
      console.error('Auto-login failed:', error);
      throw error;
    }
  }
  
  
  
  
  
  function redirectToDashboard(router, role) {
    const roleToDashboard = {
      parent: '/parent-dashboard',
      teacher: '/teacher-dashboard',
      admin: '/admin-dashboard',
    };
  
    if (roleToDashboard[role]) {
      router.push(roleToDashboard[role]);
    } else {
      alert(`Your role "${role}" is not supported in this application. Please contact support.`);
      localStorage.clear();
    }
  }
  

  return { registerUser, autoLogin, redirectToDashboard };
}
