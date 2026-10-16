<script setup>
import { Link, useForm } from "@inertiajs/vue3";

const props = defineProps({
  room: { type: Object, default: null },
  errors: { type: Object, default: () => ({}) },
});
const form = useForm({ name: props.room?.name ?? "", description: props.room?.description ?? "" });
const action = props.room ? `/rooms/${props.room.id}/edit` : "/rooms/new";

function submit() {
  form.post(action);
}
</script>

<template>
  <div class="mx-auto max-w-lg">
    <h1 class="text-2xl font-semibold">{{ room ? "Edit room" : "New room" }}</h1>
    <form class="mt-6 space-y-4 rounded-lg border border-slate-200 bg-white p-6" @submit.prevent="submit">
      <div>
        <label for="name" class="block text-sm font-medium">Name</label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          required
          maxlength="80"
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <p v-if="form.errors.name" class="mt-1 text-sm text-red-600">{{ form.errors.name }}</p>
      </div>
      <div>
        <label for="description" class="block text-sm font-medium">
          Description <span class="text-slate-400">(optional)</span>
        </label>
        <input
          id="description"
          v-model="form.description"
          type="text"
          maxlength="200"
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <p v-if="form.errors.description" class="mt-1 text-sm text-red-600">{{ form.errors.description }}</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          type="submit"
          :disabled="form.processing"
          class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {{ room ? "Save changes" : "Create room" }}
        </button>
        <Link href="/rooms/" class="text-sm text-slate-600 hover:underline">Cancel</Link>
      </div>
    </form>
  </div>
</template>
