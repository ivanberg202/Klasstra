// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';

// Import your components or views
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import ParentDashboard from '../views/ParentDashboard.vue';
import TeacherDashboard from '../views/TeacherDashboard.vue';
import AdminDashboard from '../views/AdminDashboard.vue';
import CreateAnnouncement from '../views/CreateAnnouncement.vue';
import ClassDetail from '../components/ClassDetail.vue'; // Ensure this file exists
import NotFound from '../components/NotFound.vue'; // Ensure this component exists

const routes = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { hideNavbar: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { hideNavbar: true },
  },
  {
    path: '/parent-dashboard',
    name: 'ParentDashboard',
    component: ParentDashboard,
    meta: { requiresAuth: true, roles: ['parent'] },
  },
  {
    path: '/teacher-dashboard',
    name: 'TeacherDashboard',
    component: TeacherDashboard,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/admin-dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/create-announcement',
    name: 'CreateAnnouncement',
    component: CreateAnnouncement,
    meta: { requiresAuth: true, roles: ['teacher', 'admin'] }, // Assuming admins can also create announcements
  },
  {
    path: '/classes/:id',
    name: 'ClassDetail',
    component: ClassDetail,
    meta: { requiresAuth: true, roles: ['admin', 'teacher'] },
    props: true, // Allows route params to be passed as props to the component
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { hideNavbar: false },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation Guard
router.beforeEach((to, from, next) => {
  
  const token = localStorage.getItem('access_token'); // Check for token

  const userRole = localStorage.getItem('role'); // Check for role

  if (to.meta.requiresAuth) {
    if (!token) {
      console.warn('router/index.js: No token found. Redirecting to login.');
      return next({ name: 'Login' });
    }

    if (to.meta.roles) {
      const allowedRoles = Array.isArray(to.meta.roles) ? to.meta.roles : [to.meta.roles];

      if (!allowedRoles.includes(userRole)) {
        console.warn(`router/index.js: Role "${userRole}" not allowed. Redirecting based on role.`);
        switch (userRole) {
          case 'parent':
            return next({ name: 'ParentDashboard' });
          case 'teacher':
            return next({ name: 'TeacherDashboard' });
          case 'admin':
            return next({ name: 'AdminDashboard' });
          default:
            console.error('router/index.js: Unknown role encountered. Redirecting to login.');
            return next({ name: 'Login' });
        }
      }
    }
  }

  next();
});

export default router;
