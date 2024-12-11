<!-- src/components/UserProfileFields.vue -->
<template>
  <div class="mt-4">
    <h3 class="text-xl font-semibold mb-2 text-gray-800 dark:text-gray-100">Profile Information</h3>
    
    <div class="mb-2">
      <label class="block text-sm font-medium mb-1">First Name</label>
      <input
        v-model="localProfile.first_name"
        type="text"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
    </div>

    <div class="mb-2">
      <label class="block text-sm font-medium mb-1">Last Name</label>
      <input
        v-model="localProfile.last_name"
        type="text"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
    </div>

    <div class="mb-2">
      <label class="block text-sm font-medium mb-1">Phone Number</label>
      <input
        v-model="localProfile.phone_number"
        type="text"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
    </div>

    <div class="mb-2">
      <label class="block text-sm font-medium mb-1">Address</label>
      <input
        v-model="localProfile.address"
        type="text"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
    </div>

    <div class="mb-2">
      <label class="block text-sm font-medium mb-1">Hobbies</label>
      <input
        v-model="localProfile.hobbies"
        type="text"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
    </div>

    <div class="mb-2">
      <label class="block text-sm font-medium mb-1">Preferred Contact Method</label>
      <select
        v-model="localProfile.preferred_contact_method"
        class="w-full p-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      >
        <option disabled value="">Select a method</option>
        <option value="email">Email</option>
        <option value="phone">Phone</option>
        <option value="sms">SMS</option>
        <option value="none">None</option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserProfileFields',
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        first_name: '',
        last_name: '',
        phone_number: '',
        address: '',
        hobbies: '',
        preferred_contact_method: '',
      }),
    },
  },
  computed: {
    localProfile: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      },
    },
  },
};
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
