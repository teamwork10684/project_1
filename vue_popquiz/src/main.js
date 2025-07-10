import { createApp } from 'vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000/popquiz',
  timeout: 10000
})

const app = createApp(App)
app.config.globalProperties.$axios = axiosInstance
app.use(Antd)
app.use(router)
app.mount('#app')
