# PopQuiz WebSocket API 使用说明

## 概述

PopQuiz使用WebSocket实现实时通信功能，包括用户在线状态、实时消息等。本文档详细说明了WebSocket的使用方法。

## 连接信息

- **WebSocket URL**: `ws://localhost:5000/socket.io/`
- **传输方式**: WebSocket + Polling (自动降级)
- **认证**: 通过auth参数传递token

## 连接建立

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000', {
  auth: {
    token: 'your-session-token'
  },
  transports: ['websocket', 'polling']
});
```

## 事件定义

### 连接事件

#### connect
- **触发时机**: WebSocket连接建立成功
- **数据格式**:
```javascript
{
  sid: "abc123def456" // Socket.IO会话ID
}
```

#### disconnect
- **触发时机**: WebSocket连接断开
- **数据格式**:
```javascript
{
  reason: "io client disconnect" // 断开原因
}
```

#### connect_error
- **触发时机**: WebSocket连接发生错误
- **数据格式**:
```javascript
{
  error: "Authentication failed" // 错误信息
}
```

### 客户端发送事件

#### join_room
- **用途**: 加入房间
- **数据格式**:
```javascript
{
  room_id: 1,        // 房间ID
  user_id: 1,        // 用户ID
  username: "张三",   // 用户名
  role: 2            // 用户角色（0-创建者，1-演讲者，2-听众）
}
```

#### leave_room
- **用途**: 离开房间
- **数据格式**:
```javascript
{
  room_id: 1,  // 房间ID
  user_id: 1   // 用户ID
}
```

#### send_message
- **用途**: 发送消息
- **数据格式**:
```javascript
{
  room_id: 1,                    // 房间ID
  user_id: 1,                    // 用户ID
  username: "张三",               // 用户名
  message: "大家好，我是今天的演讲者" // 消息内容
}
```

### 服务器发送事件

#### user_joined
- **触发时机**: 有新用户加入房间
- **数据格式**:
```javascript
{
  user_id: 1,      // 加入用户的ID
  username: "张三", // 加入用户的用户名
  role: 2,         // 用户角色
  timestamp: "2024-01-01T10:00:00Z" // 时间戳
}
```

#### user_left
- **触发时机**: 有用户离开房间
- **数据格式**:
```javascript
{
  user_id: 1,      // 离开用户的ID
  username: "张三", // 离开用户的用户名
  timestamp: "2024-01-01T10:00:00Z" // 时间戳
}
```

#### room_users
- **触发时机**: 房间内用户列表发生变化
- **数据格式**:
```javascript
{
  users: [
    {
      user_id: 1,
      username: "张三",
      role: 0
    },
    {
      user_id: 2,
      username: "李四",
      role: 2
    }
  ],
  total_online: 2, // 在线总人数
  timestamp: "2024-01-01T10:00:00Z" // 更新时间戳
}
```

#### new_message
- **触发时机**: 收到新消息
- **数据格式**:
```javascript
{
  user_id: 1,                    // 发送消息的用户ID
  username: "张三",               // 发送消息的用户名
  message: "大家好，我是今天的演讲者", // 消息内容
  timestamp: "2024-01-01T10:00:00Z" // 时间戳
}
```

## 完整使用示例

### 1. 连接和基础事件监听

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000', {
  auth: {
    token: 'your-session-token'
  },
  transports: ['websocket', 'polling']
});

// 连接成功
socket.on('connect', () => {
  console.log('Connected to server');
});

// 连接断开
socket.on('disconnect', (reason) => {
  console.log('Disconnected:', reason);
});

// 连接错误
socket.on('connect_error', (error) => {
  console.error('Connection error:', error);
});
```

### 2. 房间操作

```javascript
// 加入房间
socket.emit('join_room', {
  room_id: 1,
  user_id: 1,
  username: '张三',
  role: 2
});

// 监听用户加入
socket.on('user_joined', (data) => {
  console.log(`${data.username} 加入了房间`);
});

// 监听用户离开
socket.on('user_left', (data) => {
  console.log(`${data.username} 离开了房间`);
});

// 监听房间用户列表更新
socket.on('room_users', (data) => {
  console.log(`房间内共有 ${data.total_online} 人在线`);
  console.log('用户列表:', data.users);
});

// 发送消息
socket.emit('send_message', {
  room_id: 1,
  user_id: 1,
  username: '张三',
  message: '大家好！'
});

// 监听新消息
socket.on('new_message', (data) => {
  console.log(`${data.username}: ${data.message}`);
});

// 离开房间
socket.emit('leave_room', {
  room_id: 1,
  user_id: 1
});

// 断开连接
socket.disconnect();
```

### 3. 错误处理和重连

```javascript
// 自动重连
socket.on('disconnect', (reason) => {
  if (reason === 'io server disconnect') {
    // 服务器主动断开，尝试重连
    socket.connect();
  }
});

// 连接错误重试
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

socket.on('connect_error', (error) => {
  console.error('Connection error:', error);
  
  if (reconnectAttempts < maxReconnectAttempts) {
    setTimeout(() => {
      reconnectAttempts++;
      socket.connect();
    }, 1000 * reconnectAttempts);
  }
});

// 连接成功后重置重连计数
socket.on('connect', () => {
  reconnectAttempts = 0;
});
```

## 在Vue项目中的使用

### 1. 创建WebSocket管理器

```javascript
// utils/websocket.js
import { io } from 'socket.io-client';
import { getToken } from '../api';
import eventBus from './eventBus';

class WebSocketManager {
  constructor() {
    this.socket = null;
    this.roomId = null;
    this.userId = null;
    this.username = null;
    this.role = null;
    this.isConnected = false;
  }

  connect(roomId, userId, username, role) {
    this.roomId = roomId;
    this.userId = userId;
    this.username = username;
    this.role = role;

    const token = getToken();
    if (!token) {
      console.error('No token available for WebSocket connection');
      return;
    }

    this.socket = io('http://localhost:5000', {
      auth: { token },
      transports: ['websocket', 'polling']
    });

    this.setupEventListeners();
  }

  setupEventListeners() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.joinRoom();
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.isConnected = false;
    });

    this.socket.on('user_joined', (data) => {
      eventBus.emit('userJoined', data);
    });

    this.socket.on('user_left', (data) => {
      eventBus.emit('userLeft', data);
    });

    this.socket.on('room_users', (data) => {
      eventBus.emit('roomUsersUpdated', data);
    });

    this.socket.on('new_message', (data) => {
      eventBus.emit('newMessage', data);
    });
  }

  joinRoom() {
    if (!this.socket || !this.isConnected) return;

    this.socket.emit('join_room', {
      room_id: this.roomId,
      user_id: this.userId,
      username: this.username,
      role: this.role
    });
  }

  leaveRoom() {
    if (!this.socket || !this.isConnected) return;

    this.socket.emit('leave_room', {
      room_id: this.roomId,
      user_id: this.userId
    });
  }

  sendMessage(message) {
    if (!this.socket || !this.isConnected) return;

    this.socket.emit('send_message', {
      room_id: this.roomId,
      user_id: this.userId,
      username: this.username,
      message: message
    });
  }

  disconnect() {
    if (this.socket) {
      this.leaveRoom();
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }
}

const wsManager = new WebSocketManager();
export default wsManager;
```

### 2. 在Vue组件中使用

```javascript
// Speakerroom.vue
import wsManager from '../../utils/websocket';
import eventBus from '../../utils/eventBus';

export default {
  setup() {
    const participants = ref([]);
    const onlineCount = ref(0);
    const discussionMessages = ref([]);

    // 设置WebSocket事件监听
    const setupWebSocketEvents = () => {
      eventBus.on('userJoined', (data) => {
        // 处理用户加入
        participants.value.push({
          user_id: data.user_id,
          username: data.username,
          role: data.role
        });
        onlineCount.value = participants.value.length;
      });

      eventBus.on('userLeft', (data) => {
        // 处理用户离开
        const index = participants.value.findIndex(p => p.user_id === data.user_id);
        if (index > -1) {
          participants.value.splice(index, 1);
          onlineCount.value = participants.value.length;
        }
      });

      eventBus.on('roomUsersUpdated', (data) => {
        // 处理用户列表更新
        participants.value = data.users;
        onlineCount.value = data.total_online;
      });

      eventBus.on('newMessage', (data) => {
        // 处理新消息
        discussionMessages.value.push({
          user_id: data.user_id,
          username: data.username,
          message: data.message,
          timestamp: data.timestamp
        });
      });
    };

    // 发送消息
    const sendDiscussion = () => {
      if (!discussionInput.value.trim()) return;
      wsManager.sendMessage(discussionInput.value.trim());
      discussionInput.value = '';
    };

    onMounted(async () => {
      // 获取房间信息后连接WebSocket
      await fetchRoomInfo();
      
      setupWebSocketEvents();
      
      wsManager.connect(
        roomId.value,
        userInfo.value.user_id,
        userInfo.value.username,
        userInfo.value.role
      );
    });

    onUnmounted(() => {
      wsManager.disconnect();
    });

    return {
      participants,
      onlineCount,
      discussionMessages,
      sendDiscussion
    };
  }
};
```

## 注意事项

1. **认证**: 确保在连接时传递有效的session token
2. **重连**: 实现自动重连机制以处理网络中断
3. **错误处理**: 监听连接错误并适当处理
4. **资源清理**: 在组件卸载时断开WebSocket连接
5. **事件去重**: 避免重复监听同一事件
6. **状态同步**: 确保前端状态与服务器状态保持一致

## 故障排除

### 连接失败
- 检查token是否有效
- 确认服务器地址和端口正确
- 检查网络连接

### 消息不接收
- 确认已正确监听事件
- 检查事件名称是否正确
- 确认用户已加入房间

### 频繁断开连接
- 检查网络稳定性
- 实现指数退避重连策略
- 检查服务器负载 