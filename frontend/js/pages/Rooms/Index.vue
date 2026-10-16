<script setup>
import { Link, router, usePage } from "@inertiajs/vue3";
import { computed } from "vue";

defineProps({ rooms: Array });
const page = usePage();
const isManager = computed(() => page.props.auth?.user?.is_manager ?? false);

function remove(room) {
  if (confirm(`Delete “${room.name}” and all of its bookings?`)) {
    router.delete(`/rooms/${room.id}/delete`);
  }
}
</script>

<template>
  <div class="flex items-center justify-between">
    <h1 class="text-2xl font-semibold">Rooms</h1>
    <Link
      v-if="isManager"
      href="/rooms/new"
      class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700"
    >
      New room
    </Link>
  </div>

  <p
    v-if="rooms.length === 0"
    class="rounded-md border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500"
  >
    No rooms yet.
    <template v-if="isManager">Create the first one.</template>
    <template v-else>Ask a room manager to add one, or switch role to add it yourself.</template>
  </p>

  <ul v-else class="divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
    <li v-for="room in rooms" :key="room.id" class="flex items-center justify-between gap-4 px-4 py-3">
      <div>
        <Link :href="`/rooms/${room.id}/`" class="font-medium text-indigo-700 hover:underline">{{ room.name }}</Link>
        <p v-if="room.description" class="text-sm text-slate-600">{{ room.description }}</p>
      </div>
      <div class="flex items-center gap-3 text-sm">
        <Link :href="`/rooms/${room.id}/`" class="text-slate-600 hover:underline">Schedule</Link>
        <template v-if="isManager">
          <Link :href="`/rooms/${room.id}/edit`" class="text-slate-600 hover:underline">Edit</Link>
          <button type="button" class="text-red-600 hover:underline" @click="remove(room)">Delete</button>
        </template>
      </div>
    </li>
  </ul>
</template>
