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
    this.socket = io('/', {
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
      this.reconnectAttempts = 0;
      this.joinRoom();
    });
    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.isConnected = false;
      if (reason === 'io server disconnect') {
        this.socket.connect();
      }
    });
    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.isConnected = false;
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.socket.connect();
        }, this.reconnectDelay * this.reconnectAttempts);
      }
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
    this.socket.on('question_generated', (data) => {
      eventBus.emit('questionGenerated', data);
    });
    this.socket.on('question_published', (data) => {
      eventBus.emit('questionPublished', data);
    });
    this.socket.on('question_ended', (data) => {
      eventBus.emit('questionEnded', data);
    });
    this.socket.on('answer_submitted', (data) => {
      eventBus.emit('answerSubmitted', data);
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
    if (this.socket) this.socket.disconnect();
    this.isConnected = false;
  }
}

const wsManager = new WebSocketManager();
export default wsManager; 