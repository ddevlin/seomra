<script setup>
import { Link, router } from "@inertiajs/vue3";
import { computed } from "vue";
import BookingCell from "@/components/BookingCell.vue";
import { formatDay, formatHour, formatLongDay, formatRange } from "@/lib/dates";

const props = defineProps({
  date: String,
  today: String,
  rooms: Array,
  hours: Array,
  bookings: Array,
  my_bookings: Array,
  prev_day: String,
  next_day: String,
});

// "roomId:hour" -> booking for the selected day.
const slots = computed(() => {
  const map = new Map();
  for (const b of props.bookings) {
    for (let h = b.start_hour; h < b.end_hour; h++) map.set(`${b.room_id}:${h}`, b);
  }
  return map;
});
const bookingAt = (roomId, hour) => slots.value.get(`${roomId}:${hour}`) ?? null;
const navClass = "rounded-md border border-slate-300 bg-white px-3 py-1.5 hover:bg-slate-50";

function goTo(date) {
  if (date) router.get("/bookings/", { date }, { preserveState: true, preserveScroll: true });
}
function cancel(booking) {
  const when = `${formatDay(booking.date)}, ${formatRange(booking.start_hour, booking.end_hour)}`;
  if (confirm(`Cancel ${booking.room_name} on ${when}?`)) {
    router.delete(`/bookings/${booking.id}/cancel`, { preserveScroll: true });
  }
}
</script>

<template>
  <div class="flex flex-wrap items-end justify-between gap-4">
    <div>
      <h1 class="text-2xl font-semibold">Bookings</h1>
      <p class="text-sm text-slate-600">{{ formatLongDay(date) }}</p>
    </div>
    <div class="flex flex-wrap items-center gap-2 text-sm">
      <button type="button" :class="navClass" @click="goTo(prev_day)">← Previous day</button>
      <button type="button" :class="navClass" @click="goTo(today)">Today</button>
      <button type="button" :class="navClass" @click="goTo(next_day)">Next day →</button>
      <input
        type="date"
        :value="date"
        class="rounded-md border border-slate-300 bg-white px-2 py-1.5"
        @change="goTo($event.target.value)"
      />
    </div>
  </div>

  <p
    v-if="rooms.length === 0"
    class="rounded-md border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500"
  >
    No rooms yet. <Link href="/rooms/" class="text-indigo-600 hover:underline">Go to rooms</Link>.
  </p>
  <div v-else class="overflow-x-auto rounded-lg border border-slate-200 bg-white">
    <table class="w-full min-w-[720px] table-fixed border-collapse text-sm">
      <thead>
        <tr>
          <th class="w-40 border border-slate-200 bg-slate-50 p-2 text-left font-medium text-slate-500">Room</th>
          <th
            v-for="hour in hours"
            :key="hour"
            class="border border-slate-200 bg-slate-50 p-2 text-left font-medium text-slate-700"
          >
            {{ formatHour(hour) }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="room in rooms" :key="room.id">
          <th class="border border-slate-200 bg-slate-50 p-2 text-left font-medium">
            <Link :href="`/rooms/${room.id}/?week=${date}`" class="text-indigo-700 hover:underline">
              {{ room.name }}
            </Link>
          </th>
          <BookingCell
            v-for="hour in hours"
            :key="room.id + ':' + hour"
            :booking="bookingAt(room.id, hour)"
            :is-start="bookingAt(room.id, hour)?.start_hour === hour"
            :book-href="`/rooms/${room.id}/book?date=${date}&hour=${hour}`"
          />
        </tr>
      </tbody>
    </table>
  </div>

  <section>
    <h2 class="text-lg font-semibold">My upcoming bookings</h2>
    <p v-if="my_bookings.length === 0" class="mt-2 text-sm text-slate-500">You have no upcoming bookings.</p>
    <ul v-else class="mt-2 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
      <li
        v-for="b in my_bookings"
        :key="b.id"
        class="flex items-center justify-between gap-4 px-4 py-3 text-sm"
      >
        <div>
          <Link :href="`/rooms/${b.room_id}/?week=${b.date}`" class="font-medium text-indigo-700 hover:underline">
            {{ b.room_name }}
          </Link>
          <span class="text-slate-600"> · {{ formatDay(b.date) }}, {{ formatRange(b.start_hour, b.end_hour) }}</span>
          <span v-if="b.title" class="text-slate-500"> · {{ b.title }}</span>
        </div>
        <button type="button" class="text-red-600 hover:underline" @click="cancel(b)">Cancel</button>
      </li>
    </ul>
  </section>
</template>
