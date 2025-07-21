import { http, HttpResponse } from 'msw'; // 从 msw 中导入 http 和 HttpResponse


// 假设你的后端接口前缀是 /api，如果不是，请根据实际情况调整
const API_BASE_URL = 'http://localhost:5000/popquiz';

export const handlers = [
  // --- 1. 模拟 GET 请求：获取用户列表 ---
  // http.get(url, resolver)
  // url: 要拦截的 URL 路径
  // resolver: 一个异步函数，用于处理请求并返回响应
  http.post(`${API_BASE_URL}/login`, async({request}) => {
    const { username, password } = await request.json(); 
    console.log(`尝试登录 - 用户名: ${username}, 密码: ${password}`);

    // 根据用户名和密码进行条件判断
    if (username === 'user' && password === '123456') { 
        return HttpResponse.json({
          "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", // 模拟的 token
          "message": "登录成功"
        }, { status: 200 }); 
      } else { 
        return HttpResponse.json({
          "message": "登录失败",
        }, { status: 401 }); // 模拟一些延迟
      }
    }),

 http.post(`${API_BASE_URL}/register`, async({request}) => {
    const { username, password } = await request.json(); 
    console.log(`尝试注册 - 用户名: ${username}, 密码: ${password}`);

    // 根据用户名和密码进行条件判断
    if (username === 'user' && password === '123456') { 
        return HttpResponse.json({
          "id": "001", // 模拟的 token
          "message": "注册成功"
        }, { status: 200 }); 
      } else { 
        return HttpResponse.json({
          "message": "用户名已存在",
        }, { status: 401 }); // 模拟一些延迟
      }
    }),
];


//localStorage.removeItem('token');
//localStorage.removeItem('username');