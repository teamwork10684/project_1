# PopQuiz API 文档

## 文档概览

本目录包含PopQuiz项目的完整API文档，包括HTTP API和WebSocket实时通信API。

## 文档列表

### 1. HTTP API文档

- **文件**: `popquiz_api.yml`
- **格式**: OpenAPI 3.0.3
- **内容**: 所有HTTP REST API接口定义
- **包含功能**:
  - 用户管理（注册、登录、登出）
  - 演讲室管理（创建、加入、邀请）
  - 题目管理（创建、发布、答题）
  - 讨论管理（发表、获取讨论）
  - 统计功能（答题统计、用户统计）

### 2. WebSocket API文档

- **文件**: `websocket_api.yml`
- **格式**: OpenAPI 3.0.3
- **内容**: WebSocket连接和事件定义
- **包含功能**:
  - WebSocket连接建立
  - 实时用户状态同步
  - 实时消息传递
  - 房间用户列表更新

### 3. WebSocket使用说明

- **文件**: `websocket_usage.md`
- **格式**: Markdown
- **内容**: 详细的WebSocket使用指南
- **包含内容**:
  - 连接建立方法
  - 事件定义和格式
  - 完整使用示例
  - Vue项目集成指南
  - 错误处理和故障排除

### 4. 数据库表结构

- **文件**: `tables.md`
- **格式**: Markdown
- **内容**: 数据库表结构说明
- **包含内容**:
  - 所有数据表的字段定义
  - 表关系说明
  - 索引和约束信息

## 快速开始

### 查看API文档

1. **在线查看**: 使用Swagger UI或其他OpenAPI查看器打开YAML文件
2. **本地查看**: 使用VS Code的OpenAPI插件或在线工具

### 测试API

1. **启动后端服务**:

   ```bash
   cd flask_popquiz
   python app.py
   ```
2. **使用API测试工具**:

   - Postman
   - curl
   - 浏览器开发者工具

### 集成WebSocket

1. **安装依赖**:

   ```bash
   cd vue_popquiz
   npm install socket.io-client
   ```
2. **参考使用说明**: 查看 `websocket_usage.md` 获取详细集成指南

## API认证

所有API都需要通过以下方式进行认证：

### HTTP API

- 使用 `session_token` 参数或 `Authorization` 头部
- Token通过登录接口获取

### WebSocket API

- 通过连接时的 `auth.token` 参数传递
- 使用相同的session token

## 开发环境

- **后端**: Flask + SQLAlchemy + SocketIO
- **前端**: Vue 3 + Socket.IO Client
- **数据库**: MySQL
- **实时通信**: WebSocket (Socket.IO)

## 注意事项

1. **CORS**: 后端已配置CORS支持跨域请求
2. **WebSocket**: 支持自动降级到Polling
3. **认证**: 所有接口都需要有效的session token
4. **错误处理**: 统一的错误响应格式
5. **数据格式**: 所有时间字段使用ISO 8601格式

## 更新日志

- **v1.0**: 初始版本，包含基础功能
- **v1.1**: 添加WebSocket实时通信功能
- **v1.2**: 完善API文档和使用说明
