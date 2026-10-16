import "vite/modulepreload-polyfill";
import axios from "axios";

import { createInertiaApp } from "@inertiajs/vue3";
import { createApp, h } from "vue";
import Layout from "./components/Layout.vue";


import "../css/main.css";


const pages = import.meta.glob("./pages/**/*.vue");


document.addEventListener("DOMContentLoaded", () => {
	axios.defaults.xsrfCookieName = "csrftoken";
	axios.defaults.xsrfHeaderName = "X-CSRFToken";
	
	createInertiaApp({
		resolve: async (name) => {
			const page = (await pages[`./pages/${name}.vue`]()).default;
			page.layout = page.layout || Layout;
			return page;
		},
		setup({ el, App, props, plugin }) {
			createApp({ render: () => h(App, props) })
				.use(plugin)
				.mount(el);
		},
	});
	
});
