<script setup>
import { Link } from "@inertiajs/vue3";
import { computed } from "vue";
import BookingCell from "@/components/BookingCell.vue";
import { formatDay, formatHour } from "@/lib/dates";

const props = defineProps({
  room: Object,
  days: Array,
  hours: Array,
  bookings: Array,
  today: String,
  prev_week: String,
  next_week: String,
});

// "YYYY-MM-DD:hour" -> booking, so each cell is a constant-time lookup.
const slots = computed(() => {
  const map = new Map();
  for (const b of props.bookings) {
    for (let h = b.start_hour; h < b.end_hour; h++) map.set(`${b.date}:${h}`, b);
  }
  return map;
});
const bookingAt = (day, hour) => slots.value.get(`${day}:${hour}`) ?? null;
const bookHref = (day, hour) => `/rooms/${props.room.id}/book?date=${day}&hour=${hour}`;
const navClass = "rounded-md border border-slate-300 bg-white px-3 py-1.5 hover:bg-slate-50";
</script>

<template>
  <div class="flex flex-wrap items-end justify-between gap-4">
    <div>
      <Link href="/rooms/" class="text-sm text-slate-500 hover:underline">← Rooms</Link>
      <h1 class="text-2xl font-semibold">{{ room.name }}</h1>
      <p v-if="room.description" class="text-sm text-slate-600">{{ room.description }}</p>
    </div>
    <div class="flex items-center gap-2 text-sm">
      <Link :href="`/rooms/${room.id}/?week=${prev_week}`" :class="navClass">← Previous week</Link>
      <Link :href="`/rooms/${room.id}/?week=${today}`" :class="navClass">This week</Link>
      <Link :href="`/rooms/${room.id}/?week=${next_week}`" :class="navClass">Next week →</Link>
    </div>
  </div>

  <div class="overflow-x-auto rounded-lg border border-slate-200 bg-white">
    <table class="w-full min-w-[720px] table-fixed border-collapse text-sm">
      <thead>
        <tr>
          <th class="w-20 border border-slate-200 bg-slate-50 p-2 text-left font-medium text-slate-500">Time</th>
          <th
            v-for="day in days"
            :key="day"
            class="border border-slate-200 bg-slate-50 p-2 text-left font-medium"
            :class="day === today ? 'text-indigo-700' : 'text-slate-700'"
          >
            {{ formatDay(day) }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="hour in hours" :key="hour">
          <th class="border border-slate-200 bg-slate-50 p-2 text-left font-normal text-slate-500">
            {{ formatHour(hour) }}
          </th>
          <BookingCell
            v-for="day in days"
            :key="day + hour"
            :booking="bookingAt(day, hour)"
            :is-start="bookingAt(day, hour)?.start_hour === hour"
            :book-href="bookHref(day, hour)"
          />
        </tr>
      </tbody>
    </table>
  </div>
  <p class="text-xs text-slate-500">Hover a free slot and click “Book”. Your own bookings are highlighted.</p>
</template>
