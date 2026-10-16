const DAY_FORMAT = new Intl.DateTimeFormat("en-IE", { weekday: "short", day: "numeric", month: "short" });
const LONG_FORMAT = new Intl.DateTimeFormat("en-IE", {
  weekday: "long",
  day: "numeric",
  month: "long",
  year: "numeric",
});

// ISO date strings are parsed as local dates so the weekday never shifts by timezone.
export function toDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function formatDay(iso) {
  return DAY_FORMAT.format(toDate(iso));
}

export function formatLongDay(iso) {
  return LONG_FORMAT.format(toDate(iso));
}

export function formatHour(hour) {
  return `${String(hour).padStart(2, "0")}:00`;
}

export function formatRange(start, end) {
  return `${formatHour(start)}–${formatHour(end)}`;
}
