<!-- src/components/UserBaseFields.vue -->
<template>
  <div>
    <div class="mb-2">
      <label class="block text-sm font-medium mb-1 text-gray-800 dark:text-gray-100">Username</label>
      <input
        v-model="localUsername"
        type="text"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
    </div>

    <div class="mb-2">
      <label class="block text-sm font-medium mb-1 text-gray-800 dark:text-gray-100">Email</label>
      <input
        v-model="localEmail"
        type="email"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
    </div>

    <div class="mb-2">
      <label class="block text-sm font-medium mb-1 text-gray-800 dark:text-gray-100">Password</label>
      <input
        v-model="localPassword"
        type="password"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
    </div>

    <div class="mb-2">
      <label class="block text-sm font-medium mb-1 text-gray-800 dark:text-gray-100">Role</label>
      <select
        v-model="localRole"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      >
        <option disabled value="">Select a role</option>
        <option value="admin">Admin</option>
        <option value="teacher">Teacher</option>
        <option value="parent">Parent</option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserBaseFields',
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        username: '',
        email: '',
        password: '',
        role: '',
      }),
    },
  },
  computed: {
    localUsername: {
      get() {
        return this.modelValue.username;
      },
      set(value) {
        console.log('Updating username:', value);
        this.$emit('update:modelValue', { ...this.modelValue, username: value });
      },
    },
    localEmail: {
      get() {
        return this.modelValue.email;
      },
      set(value) {
        console.log('Updating email:', value);
        this.$emit('update:modelValue', { ...this.modelValue, email: value });
      },
    },
    localPassword: {
      get() {
        return this.modelValue.password;
      },
      set(value) {
        console.log('Updating password:', value);
        this.$emit('update:modelValue', { ...this.modelValue, password: value });
      },
    },
    localRole: {
      get() {
        return this.modelValue.role;
      },
      set(value) {
        console.log('Updating role:', value);
        this.$emit('update:modelValue', { ...this.modelValue, role: value });
      },
    },
  },
};
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
