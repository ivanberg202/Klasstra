import { createRouter, createWebHistory } from 'vue-router';

// Import your components or views
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import ParentDashboard from '../views/ParentDashboard.vue';
import TeacherDashboard from '../views/TeacherDashboard.vue';
import AdminDashboard from '../views/AdminDashboard.vue';
import CreateAnnouncement from '../views/CreateAnnouncement.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  {
    path: '/parent-dashboard',
    name: 'ParentDashboard',
    component: ParentDashboard,
    meta: { requiresAuth: true, role: 'parent' },
  },
  {
    path: '/teacher-dashboard',
    name: 'TeacherDashboard',
    component: TeacherDashboard,
    meta: { requiresAuth: true, role: 'teacher' },
  },
  {
    path: '/admin-dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/:pathMatch(.*)*', // Catch-all route for 404
    name: 'NotFound',
    component: () => import('../components/NotFound.vue'), // Lazy-load NotFound view
  },
  {
    path: '/create-announcement',
    name: 'CreateAnnouncement',
    component: CreateAnnouncement,
    meta: { requiresAuth: true, role: 'teacher' },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard to protect routes
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');

  if (to.meta.requiresAuth) {
    if (!token) {
      // Redirect to login if the user is not authenticated
      return next('/login');
    }
    if (to.meta.role && to.meta.role !== userRole) {
      // Redirect to the correct dashboard if the role doesn't match
      if (userRole === 'parent') {
        return next('/parent-dashboard');
      }
      if (userRole === 'teacher') {
        return next('/teacher-dashboard');
      }
      if (userRole === 'admin') {
        return next('/admin-dashboard');
      }
      return next('/'); // Default fallback
    }
  }

  // Allow access if no restrictions
  next();
});

export default router;
