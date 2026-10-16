<script setup>
import { Link } from "@inertiajs/vue3";
</script>

<template>
  <div class="mx-auto max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    <h1 class="text-xl font-semibold">Check your inbox</h1>
    <p class="mt-2 text-sm text-slate-600">We sent you a sign-in link. It works once and expires in 15 minutes.</p>
    <p class="mt-4 rounded-md bg-amber-50 p-3 text-sm text-amber-800">
      Running locally? No email is sent. The link is printed in the terminal running
      <code class="font-mono">manage.py runserver</code>.
    </p>
    <Link href="/login" class="mt-4 inline-block text-sm text-indigo-600 hover:underline">Use a different email</Link>
  </div>
</template>
