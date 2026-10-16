<script setup>
import { useForm } from "@inertiajs/vue3";

const form = useForm({ email: "" });
function submit() {
  form.post("/login");
}
</script>

<template>
  <div class="mx-auto max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    <h1 class="text-xl font-semibold">Sign in</h1>
    <p class="mt-1 text-sm text-slate-600">Enter your email and we'll send you a sign-in link.</p>
    <form class="mt-6 space-y-4" @submit.prevent="submit">
      <div>
        <label for="email" class="block text-sm font-medium">Email</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          autocomplete="email"
          required
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        />
        <p v-if="form.errors.email" class="mt-1 text-sm text-red-600">{{ form.errors.email }}</p>
      </div>
      <button
        type="submit"
        :disabled="form.processing"
        class="w-full rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        Send me a link
      </button>
    </form>
  </div>
</template>
