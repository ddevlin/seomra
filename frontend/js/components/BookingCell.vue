<script setup>
import { Link } from "@inertiajs/vue3";

// One hour-slot cell in a schedule grid: shows the booking that covers it,
// or a "Book" link when the slot is free.
defineProps({
  booking: { type: Object, default: null },
  bookHref: { type: String, default: null },
  isStart: { type: Boolean, default: false },
});
</script>

<template>
  <td class="h-12 border border-slate-200 p-0 align-top">
    <div
      v-if="booking"
      class="h-full px-2 py-1 text-xs leading-tight"
      :class="booking.is_mine ? 'bg-indigo-100 text-indigo-900' : 'bg-slate-200 text-slate-700'"
      :title="`${booking.user_email}${booking.title ? ' · ' + booking.title : ''}`"
    >
      <template v-if="isStart">
        <div class="truncate font-medium">{{ booking.title || "Booked" }}</div>
        <div class="truncate">{{ booking.user_email }}</div>
      </template>
    </div>
    <Link
      v-else-if="bookHref"
      :href="bookHref"
      class="flex h-full w-full items-center justify-center text-xs text-transparent hover:bg-emerald-50 hover:text-emerald-700"
    >
      Book
    </Link>
  </td>
</template>
