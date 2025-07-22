import { http, HttpResponse } from 'msw'; // 从 msw 中导入 http 和 HttpResponse


// 假设你的后端接口前缀是 /api，如果不是，请根据实际情况调整
const API_BASE_URL = 'http://localhost:5000/popquiz';

export const handlers = [
  // --- 1. 模拟 GET 请求：获取用户列表 ---
  // http.get(url, resolver)
  // url: 要拦截的 URL 路径
  // resolver: 一个异步函数，用于处理请求并返回响应
  http.post(`${API_BASE_URL}/login`, async ({ request }) => {//测试登录功能
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

  http.post(`${API_BASE_URL}/register`, async ({ request }) => {//测试注册功能
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

  http.get(`${API_BASE_URL}/user/speech-rooms`, async ({ request }) => { // 测试获取用户参与的演讲室列表
    console.log('尝试获取用户参与/创建的所有演讲室列表');

    // 1. 从 URLSearchParams 中获取 token 参数
    const url = new URL(request.url); // 创建 URL 对象来解析 URL
    const token = url.searchParams.get('token'); // 获取 'token' query 参数

    console.log(`从 query 参数接收到的 Token: ${token}`);

    // 2. 验证 token 是否有效
    let isAuthenticated = false;
    let userId = null;


    if (token === "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") {
      isAuthenticated = true;
      userId = "001"; // 假设这个token对应用户ID 001
    } else {
      return HttpResponse.json({ "message": "token无效或已过期" }, { status: 401 });
    }


    if (!isAuthenticated) {
      console.log(`Token 无效或缺失: ${token}`);
      return HttpResponse.json({ "message": "参数错误" }, { status: 400 });
    }

    // 3. 如果 token 有效，则返回 rooms 数据
    console.log(`Token 验证成功，用户 ${userId} 请求演讲室列表`);
    const roomsData = {
      "rooms": [
        {
          "id": 1,
          "name": "Python基础教程",
          "description": "介绍Python编程语言的基础知识",
          "creator_id": 1,
          "speaker_id": 2,
          "role": 0,
          "invite_code": "aB3cD7eF9gH2jk5m",
          "speaker_invite_code": "XY8ZN4pQ6rS1tUVw",
          "status": 0,
          "created_at": "2024-01-01T10:00:00Z"
        },
        {
          "id": 2,
          "name": "javaScript基础教程",
          "description": "介绍JS编程语言的基础知识",
          "creator_id": 1,
          "speaker_id": 2,
          "role": 1,
          "invite_code": "kkkkkkkkkkkkkkkk",
          "speaker_invite_code": "XY8ZN4pQ6rS1tUVw",
          "status": 1,
          "created_at": "2024-02-01T08:00:00Z"
        },


      ]
    };
    return HttpResponse.json(roomsData, { status: 200 });
  }),

  http.get(`${API_BASE_URL}/user/created-rooms`, async ({ request }) => { // 测试获取用户创建的演讲室列表
    console.log('尝试获取用户参与/创建的所有演讲室列表');

    // 1. 从 URLSearchParams 中获取 token 参数
    const url = new URL(request.url); // 创建 URL 对象来解析 URL
    const token = url.searchParams.get('token'); // 获取 'token' query 参数

    console.log(`从 query 参数接收到的 Token: ${token}`);

    // 2. 验证 token 是否有效
    let isAuthenticated = false;
    let userId = null;


    if (token === "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") {
      isAuthenticated = true;
      userId = "001"; // 假设这个token对应用户ID 001
    } else {
      return HttpResponse.json({ "message": "token无效或已过期" }, { status: 401 });
    }


    if (!isAuthenticated) {
      console.log(`Token 无效或缺失: ${token}`);
      return HttpResponse.json({ "message": "参数错误" }, { status: 400 });
    }

    // 3. 如果 token 有效，则返回 rooms 数据
    console.log(`Token 验证成功，用户 ${userId} 请求演讲室列表`);
    const roomsData = {
      "rooms": [
        {
          "id": 1,
          "name": "Python基础教程",
          "description": "介绍Python编程语言的基础知识",
          "creator_id": 1,
          "speaker_id": 2,
          "role": 0,
          "invite_code": "aB3cD7eF9gH2jk5m",
          "speaker_invite_code": "XY8ZN4pQ6rS1tUVw",
          "status": 0,
          "created_at": "2024-01-01T10:00:00Z"
        },
        {
          "id": 2,
          "name": "javaScript基础教程",
          "description": "介绍JS编程语言的基础知识",
          "creator_id": 1,
          "speaker_id": 2,
          "role": 1,
          "invite_code": "kkkkkkkkkkkkkkkk",
          "speaker_invite_code": "XY8ZN4pQ6rS1tUVw",
          "status": 1,
          "created_at": "2024-02-01T08:00:00Z"
        },

        {
          "id": 3,
          "name": "音乐鉴赏",
          "description": "艺术审美补完计划",
          "creator_id": 1,
          "speaker_id": 2,
          "role": 100,
          "invite_code": "music-123",
          "speaker_invite_code": "music-123",
          "status": 2,
          "created_at": "2024-03-01T18:00:00Z"
        },

      ]
    };
    return HttpResponse.json(roomsData, { status: 200 });
  }),

  http.post(`${API_BASE_URL}/invitations`, async ({ request }) => {//测试邀请功能
    const { token, invitee_username } = await request.json();

    // 判断邀请用户
    if (invitee_username == "friend") {
      return HttpResponse.json({
        "id": "1", // 模拟的 token
        "message": "邀请成功"
      }, { status: 200 });
    } else {
      return HttpResponse.json({
        "message": "用户不存在",
      }, { status: 400 });
    }
  }),

  http.get(`${API_BASE_URL}/user/invitations`, async ({ request }) => {//测试被邀请情况功能
    const url = new URL(request.url); // 创建 URL 对象来解析 URL
    const token = url.searchParams.get('token'); // 获取 'token' query 参数
    // 判断邀请用户
    if (token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") {

      const invitationsData = {
        "invitations": [
          {
            "id": 1,
            "room_id": 1,
            "room_name": "Python基础教程",
            "description": "介绍Python编程语言的基础知识",
            "created_at": "2024-01-01T10:00:00Z",
            "creator_name": "张三",
            "speaker_name": "李四",
            "total_participants": 15,
            "role": 1,
            "status": 0,
            "room_status": 0,
            "invited_time": "2024-01-01T09:30:00Z"
          },
          {
            "id": 2,
            "room_id": 2,
            "room_name": "Web开发实战",
            "description": "从零开始学习Web开发",
            "created_at": "2024-01-02T14:30:00Z",
            "creator_name": "王五",
            "speaker_name": null,
            "total_participants": 8,
            "role": 0,
            "status": 1,
            "room_status": 1,
            "invited_time": "2024-01-02T13:00:00Z"
          },

        ]
      };

      return HttpResponse.json(invitationsData, { status: 200 });
    } else {
      return HttpResponse.json({
        "message": "参数错误",
      }, { status: 400 });
    }
  }),

  http.post(`${API_BASE_URL}/invitations/accept`, async ({ request }) => {//测试接受邀请功能
    const { token} = await request.json();

    // 判断邀请用户
    if (token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") {
      return HttpResponse.json({
        "id": "1", // 模拟的 token
        "message": "接受邀请成功"
      }, { status: 200 });
    } else {
      return HttpResponse.json({
        "message": "邀请不存在",
      }, { status: 400 });
    }
  }),

  http.post(`${API_BASE_URL}/invitations/reject`, async ({ request }) => {//测试拒绝邀请功能
    const { token} = await request.json();

    // 判断邀请用户
    if (token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") {
      return HttpResponse.json({
        "id": "1", // 模拟的 token
        "message": "拒绝邀请成功"
      }, { status: 200 });
    } else {
      return HttpResponse.json({
        "message": "邀请不存在",
      }, { status: 400 });
    }
  }),

  http.post(`${API_BASE_URL}/join-room`, async ({ request }) => {//测试加入演讲室功能
    const { token, invite_code} = await request.json();

    // 判断邀请用户
    if (token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"&&invite_code=="666666") {
      return HttpResponse.json({
        "id": "1", // 模拟的 token
        "message": "加入成功"
      }, { status: 200 });
    } else {
      return HttpResponse.json({
        "message": "邀请无效或者过期",
      }, { status: 400 });
    }
  }),

];


//localStorage.removeItem('token');
//localStorage.removeItem('username');