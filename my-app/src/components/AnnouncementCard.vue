<!-- AnnouncementCard.vue -->
<template>
  <div class="p-4 bg-white dark:bg-gray-800 rounded shadow text-gray-900 dark:text-gray-100">
    <!-- Title -->
    <h3 class="text-lg font-medium mb-2">{{ title }}</h3>

    <!-- Top Section: Class, Publisher, and Published Date -->
    <div class="flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-300 mb-3">
      <!-- Class Name -->
      <p v-if="className" class="mr-4">
        <span class="font-semibold">Class:</span> {{ className }}
      </p>

      <!-- Publisher -->
      <p v-if="publisher" class="mr-4">
        <span class="font-semibold">Published by:</span> {{ publisher }}
      </p>

      <!-- Published Date -->
      <p v-if="formattedDateTime">
        <span class="font-semibold">Published:</span> {{ formattedDateTime }}
      </p>
    </div>

    <!-- Content -->
    <p v-html="formattedContent" class="mt-2"></p>
  </div>
</template>

<script>
export default {
  name: 'AnnouncementCard',
  props: {
    title: { type: String, required: true },
    content: { type: String, required: true },
    className: { type: String, default: '' },
    dateSubmitted: { type: String, default: '' },
    publisher: { type: String, default: '' }, // New publisher prop
  },
  computed: {
    formattedContent() {
      // Replace newlines in content with <br> tags to preserve line breaks
      return this.content.replace(/\n/g, '<br>');
    },
    formattedDateTime() {
      const date = new Date(this.dateSubmitted);
      if (isNaN(date.getTime())) return '';
      return new Intl.DateTimeFormat(navigator.language, {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: navigator.language.includes('en-US'),
      }).format(date);
    },
  },
};
</script>
