<script setup>
import { Link, useForm } from "@inertiajs/vue3";
import { computed } from "vue";
import { formatHour } from "@/lib/dates";

const props = defineProps({
  room: Object,
  initial: Object,
  hours: Array,
  errors: { type: Object, default: () => ({}) },
});
const form = useForm({
  date: props.initial.date,
  start_hour: Number(props.initial.start_hour),
  end_hour: Number(props.initial.end_hour),
  title: props.initial.title ?? "",
});
const endOptions = computed(() => props.hours.map((h) => h + 1).filter((h) => h > form.start_hour));

function onStartChange() {
  if (form.end_hour <= form.start_hour) form.end_hour = form.start_hour + 1;
}
function submit() {
  form.post(`/rooms/${props.room.id}/book`);
}
</script>

<template>
  <div class="mx-auto max-w-lg">
    <Link :href="`/rooms/${room.id}/?week=${form.date}`" class="text-sm text-slate-500 hover:underline">
      ← {{ room.name }} schedule
    </Link>
    <h1 class="text-2xl font-semibold">Book {{ room.name }}</h1>
    <form class="mt-6 space-y-4 rounded-lg border border-slate-200 bg-white p-6" @submit.prevent="submit">
      <div>
        <label for="date" class="block text-sm font-medium">Date</label>
        <input
          id="date"
          v-model="form.date"
          type="date"
          required
          class="mt-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <p v-if="form.errors.date" class="mt-1 text-sm text-red-600">{{ form.errors.date }}</p>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="start" class="block text-sm font-medium">From</label>
          <select
            id="start"
            v-model.number="form.start_hour"
            class="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
            @change="onStartChange"
          >
            <option v-for="h in hours" :key="h" :value="h">{{ formatHour(h) }}</option>
          </select>
          <p v-if="form.errors.start_hour" class="mt-1 text-sm text-red-600">{{ form.errors.start_hour }}</p>
        </div>
        <div>
          <label for="end" class="block text-sm font-medium">Until</label>
          <select
            id="end"
            v-model.number="form.end_hour"
            class="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option v-for="h in endOptions" :key="h" :value="h">{{ formatHour(h) }}</option>
          </select>
          <p v-if="form.errors.end_hour" class="mt-1 text-sm text-red-600">{{ form.errors.end_hour }}</p>
        </div>
      </div>
      <div>
        <label for="title" class="block text-sm font-medium">
          Title <span class="text-slate-400">(optional)</span>
        </label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          maxlength="120"
          placeholder="e.g. Sprint planning"
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <p v-if="form.errors.title" class="mt-1 text-sm text-red-600">{{ form.errors.title }}</p>
      </div>
      <p v-if="form.errors.__all__" class="text-sm text-red-600">{{ form.errors.__all__ }}</p>
      <div class="flex items-center gap-3">
        <button
          type="submit"
          :disabled="form.processing"
          class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          Book room
        </button>
        <Link :href="`/rooms/${room.id}/`" class="text-sm text-slate-600 hover:underline">Cancel</Link>
      </div>
    </form>
  </div>
</template>
