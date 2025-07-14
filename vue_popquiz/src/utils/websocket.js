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
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  // 连接到WebSocket服务器
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

    // 创建Socket.IO连接
    this.socket = io('http://localhost:5000', {
      auth: {
        token: token
      },
      transports: ['websocket', 'polling']
    });

    this.setupEventListeners();
  }

  // 设置事件监听器
  setupEventListeners() {
    if (!this.socket) return;

    // 连接成功
    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      
      // 加入房间
      this.joinRoom();
    });

    // 连接断开
    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.isConnected = false;
      
      if (reason === 'io server disconnect') {
        // 服务器主动断开，尝试重连
        this.socket.connect();
      }
    });

    // 连接错误
    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.isConnected = false;
      
      // 自动重连
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.socket.connect();
        }, this.reconnectDelay * this.reconnectAttempts);
      }
    });

    // 用户加入房间
    this.socket.on('user_joined', (data) => {
      console.log('User joined:', data);
      this.emit('userJoined', data);
    });

    // 用户离开房间
    this.socket.on('user_left', (data) => {
      console.log('User left:', data);
      this.emit('userLeft', data);
    });

    // 房间用户列表更新
    this.socket.on('room_users', (data) => {
      console.log('Room users updated:', data);
      this.emit('roomUsersUpdated', data);
    });

    // 新消息
    this.socket.on('new_message', (data) => {
      console.log('New message:', data);
      this.emit('newMessage', data);
    });
  }

  // 加入房间
  joinRoom() {
    if (!this.socket || !this.isConnected) return;

    this.socket.emit('join_room', {
      room_id: this.roomId,
      user_id: this.userId,
      username: this.username,
      role: this.role
    });
  }

  // 离开房间
  leaveRoom() {
    if (!this.socket || !this.isConnected) return;

    this.socket.emit('leave_room', {
      room_id: this.roomId,
      user_id: this.userId
    });
  }

  // 发送消息
  sendMessage(message) {
    if (!this.socket || !this.isConnected) return;

    this.socket.emit('send_message', {
      room_id: this.roomId,
      user_id: this.userId,
      username: this.username,
      message: message
    });
  }

  // 断开连接
  disconnect() {
    if (this.socket) {
      this.leaveRoom();
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  // 事件发射器
  emit(event, data) {
    // 使用事件总线发送事件
    eventBus.emit(event, data);
  }

  // 获取连接状态
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      roomId: this.roomId,
      userId: this.userId
    };
  }
}

// 创建全局实例
const wsManager = new WebSocketManager();

export default wsManager; 