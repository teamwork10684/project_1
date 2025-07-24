import { createApp } from 'vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(Antd)
app.use(router)

// if (process.env.NODE_ENV === 'development') {
//     console.log('当前处于开发环境，启动 MSW Worker...');
//     // 动态导入 MSW worker，确保只有在开发环境才加载
//     import('./mocks/browser')
//       .then(({ worker }) => {
//         // worker.start() 方法可以接受一些选项
//         worker.start({
//           // onUnhandledRequest: 'bypass' (默认) - 未匹配的请求直接通过，不拦截
//           // onUnhandledRequest: 'warn' - 未匹配的请求在控制台发出警告
//           // onUnhandledRequest: 'error' - 未匹配的请求在控制台抛出错误
//           onUnhandledRequest: 'warn', // 推荐在开发中设置为 warn
//         });
//         console.log('MSW Worker 已启动！');
//       })
//       .catch(error => {
//         console.error('启动 MSW Worker 失败:', error);
//       });
//   }

app.mount('#app')
