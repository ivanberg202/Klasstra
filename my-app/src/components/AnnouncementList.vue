<!-- AnnouncementList.vue -->
<template>
  <div class="grid gap-4">
    <AnnouncementCard
      v-for="announcement in sortedAnnouncements"
      :key="announcement.id"
      :title="announcement.title"
      :content="announcement.content"
      :className="announcement.class_name"
      :dateSubmitted="announcement.date_submitted"
      :publisher="announcement.creator_name"
    ></AnnouncementCard>
  </div>
</template>

<script>
import AnnouncementCard from './AnnouncementCard.vue';

export default {
  name: 'AnnouncementList',
  components: {
    AnnouncementCard,
  },
  props: {
    announcements: {
      type: Array,
      default: () => [],
    },
  },
  computed: {
    sortedAnnouncements() {
      const sorted = [...this.announcements];
      const sortedByDate = sorted.sort((a, b) => {
        const dateA = new Date(a.date_submitted).getTime();
        const dateB = new Date(b.date_submitted).getTime();
        return dateB - dateA; // Newest first
      });
      console.log('Sorted announcements in AnnouncementList:', sortedByDate);
      return sortedByDate;
    },
  },
  created() {
    console.log('Announcements prop received in AnnouncementList:', this.announcements);
  },
};
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
