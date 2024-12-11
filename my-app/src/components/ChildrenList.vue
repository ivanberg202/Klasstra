<template>
  <div>
    <!-- Header and Add Child Button -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Your Children</h2>
      <button
        @click="$emit('show-add-form')"
        class="py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg focus:outline-none transition"
      >
        Add Child
      </button>
    </div>

    <!-- Add Child Form Using AddChildForm Component -->
    <!-- Pass the classesList prop down to the AddChildForm component -->
    <AddChildForm
      v-if="addChildFormVisible"
      :classesList="classesList"
      @add-child="addChild"
      @cancel="hideAddChildForm"
    />

    <!-- Children List -->
    <div v-if="children.length" class="grid gap-4">
      <ChildCard
        v-for="child in children"
        :key="child.id"
        :firstName="child.first_name"
        :lastName="child.last_name"
        :className="child.class.name"
        :studentId="child.id"
        @delete-child="handleDeleteChild"
      />
    </div>
    <p v-else class="text-gray-500 dark:text-gray-500">No children information available.</p>
  </div>
</template>

<script>
import ClassSelector from './ClassSelector.vue';
import ChildCard from './ChildCard.vue';
import AddChildForm from './AddChildForm.vue';

export default {
  name: 'ChildrenList',
  components: { 
    ClassSelector,
    ChildCard,
    AddChildForm,
  },
  props: {
    children: {
      type: Array,
      default: () => [],
    },
    classesList: {
      type: Array,
      default: () => [],
    },
    addChildFormVisible: {
      type: Boolean,
      default: false,
    },
    selectedClassId: {
      type: [Number, String],
      default: '',
    },
  },
  methods: {
    addChild(payload) {
      // Forward the 'add-child' event and payload to the parent component (ParentDashboard)
      this.$emit('add-child', payload);
    },
    hideAddChildForm() {
      // Notify parent to hide the add-child form
      this.$emit('hide-add-form');
    },
    handleDeleteChild(studentId) {
      // Forward the 'delete-child' event to the parent
      this.$emit('delete-child', studentId);
    },
  },
};
</script>

<style scoped>
/* Add any local styles if needed */
</style>
