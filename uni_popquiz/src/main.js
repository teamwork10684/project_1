import {
	createSSRApp
} from "vue";
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from "./App.vue";
export function createApp() {
	const app = createSSRApp(App);
	app.use(Antd)
	return {
		app,
	};
}
