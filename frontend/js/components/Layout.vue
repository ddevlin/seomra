<script setup>
import { Link, router, usePage } from "@inertiajs/vue3";
import { computed } from "vue";
import FlashMessages from "./FlashMessages.vue";

const page = usePage();
const user = computed(() => page.props.auth?.user ?? null);
const switchLabel = computed(() =>
  user.value?.is_manager ? "Switch to user" : "Switch to room manager",
);

function switchRole() {
  router.post("/role/switch", {}, { preserveScroll: true });
}
function logout() {
  router.post("/logout");
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="border-b border-slate-200 bg-white">
      <nav class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <div class="flex items-center gap-6">
          <Link href="/" class="text-lg font-semibold tracking-tight">Seomra</Link>
          <template v-if="user">
            <Link href="/rooms/" class="text-sm text-slate-600 hover:text-slate-900">Rooms</Link>
            <Link href="/bookings/" class="text-sm text-slate-600 hover:text-slate-900">Bookings</Link>
          </template>
        </div>
        <div v-if="user" class="flex flex-wrap items-center gap-3 text-sm">
          <span class="text-slate-600">{{ user.email }}</span>
          <span
            class="rounded-full px-2 py-0.5 text-xs font-medium"
            :class="user.is_manager ? 'bg-indigo-100 text-indigo-800' : 'bg-slate-100 text-slate-700'"
          >
            {{ user.is_manager ? "Room manager" : "User" }}
          </span>
          <button type="button" class="text-indigo-600 hover:underline" @click="switchRole">
            {{ switchLabel }}
          </button>
          <button type="button" class="text-slate-500 hover:underline" @click="logout">Log out</button>
        </div>
      </nav>
    </header>
    <main class="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <FlashMessages />
      <slot />
    </main>
  </div>
</template>
