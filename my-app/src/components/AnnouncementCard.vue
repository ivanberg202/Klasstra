<!-- AnnouncementCard.vue -->
<template>
  <div class="p-4 bg-white dark:bg-gray-800 rounded shadow">
    <h3 class="text-lg font-medium">{{ title }}</h3>
    <p class="text-sm text-gray-600 dark:text-gray-400">{{ content }}</p>
    <div class="text-xs text-gray-500 dark:text-gray-500 mt-2">
      Class: {{ className }} | Published by: {{ publisher }} | Submitted on: {{ formattedDate }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'AnnouncementCard',
  props: {
    title: {
      type: String,
      required: true,
    },
    content: {
      type: String,
      default: 'No content available.', // Provide a default fallback
    },
    className: {
      type: String,
      required: true,
    },
    dateSubmitted: {
      type: String, // Assuming ISO string
      required: true,
    },
    publisher: { // Ensure this matches the serialized field
      type: String,
      required: true,
    },
  },
  computed: {
    formattedDate() {
      return new Date(this.dateSubmitted).toLocaleDateString();
    },
  },
  created() {
    console.log('AnnouncementCard props:', {
      title: this.title,
      content: this.content,
      className: this.className,
      dateSubmitted: this.dateSubmitted,
      publisher: this.publisher,
    });
  },
};
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
