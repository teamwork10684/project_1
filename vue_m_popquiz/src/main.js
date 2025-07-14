import { createApp } from 'vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import router from './router'
//主要功能逻辑

const app = createApp(App)
app.use(Antd)
app.use(router)
app.mount('#app')
