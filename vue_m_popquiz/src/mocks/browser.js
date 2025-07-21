import { setupWorker } from 'msw/browser'; // 导入 setupWorker
import { handlers } from './handlers';      // 导入我们定义的 Mock 规则

// 创建 Service Worker
export const worker = setupWorker(...handlers);

// 可选：在 worker 启动前添加一些监听器，用于调试
worker.events.on('request:start', ({ request }) => {
  console.log('MSW 请求开始:', request.method, request.url);
});

worker.events.on('request:match', ({ request }) => {
  console.log('MSW 请求匹配:', request.method, request.url);
});

worker.events.on('request:unhandled', ({ request }) => {
  console.warn('MSW 未处理的请求:', request.method, request.url);
});

worker.events.on('response:mocked', ({ request, response }) => {
  console.log('MSW 模拟响应:', request.method, request.url, response.status);
});