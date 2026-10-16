<script setup>
import { usePage } from "@inertiajs/vue3";
import { computed } from "vue";

const page = usePage();
const messages = computed(() => page.props.messages ?? []);
const classes = {
  success: "border-green-200 bg-green-50 text-green-800",
  error: "border-red-200 bg-red-50 text-red-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  info: "border-sky-200 bg-sky-50 text-sky-800",
};
</script>

<template>
  <div v-if="messages.length" class="space-y-2">
    <div
      v-for="(m, i) in messages"
      :key="i"
      class="rounded-md border px-4 py-3 text-sm"
      :class="classes[m.level_tag] ?? classes.info"
    >
      {{ m.message }}
    </div>
  </div>
</template>
