# vue_popquiz

PopQuiz 前端项目，基于 Vue 3 + Vite + Ant Design Vue，提供智能演讲互动平台的 Web 端界面。

## 技术栈 🛠️

- [Vue 3](https://vuejs.org/) + [Vite](https://vitejs.dev/)
- [Ant Design Vue](https://www.antdv.com/) 组件库
- [Vue Router](https://router.vuejs.org/)
- [Axios](https://axios-http.com/) 用于 API 请求
- [ECharts](https://echarts.apache.org/) 用于数据可视化
- [Socket.io-client](https://socket.io/) 实现实时通信

## 主要功能 ✨

- **用户认证**🔐：支持注册、登录、登出。
- **首页仪表盘**📊：展示用户统计信息、被邀请情况、我创建/参与/结束的演讲列表。
- **演讲房间管理**🏠：
  - 创建/加入/邀请他人加入演讲房间
  - 支持组织者、演讲者、听众多角色
  - 房间详情、邀请码管理
- **题目发布与答题**📝：演讲者/组织者可发布题目，听众可实时答题，支持答题统计与结果查看(等待后续完善)。
- **讨论区**💬：支持题目下的讨论与互动(等待后续完善)。
- **邀请管理**📨：查看、接受、拒绝他人邀请，支持多角色邀请。
- **实时互动**⚡：通过 WebSocket 实现房间内实时互动与状态同步(等待后续完善)。

## 页面结构 🗂️

- `/auth`：登录/注册页
- `/home`：用户首页（仪表盘、邀请、演讲列表）
- `/main`：主布局（含侧边栏导航）
- `/main/demo`：AI 题目生成 Demo
- `/main/room/:roomId`：普通房间页面
- `/main/speakerroom/:roomId`：演讲者房间页面

## 项目启动 🚀

```sh
npm install
npm run dev
```

## 构建生产环境 🏗️

```sh
npm run build
```

## 其他说明 ℹ️

- 默认后端 API 地址为 `http://localhost:5000/popquiz`，如需更改请在 `src/api/index.js` 中修改。
- 推荐使用 [VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) 进行开发。
