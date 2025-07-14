<template>
  <div class="speakerroom-container">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="header-left">
        <a-button type="link" @click="goBack">
          <ArrowLeftOutlined />
          返回首页
        </a-button>
      </div>
      <div class="header-center">
        <h1 class="room-title">{{ roomInfo.name }}</h1>
      </div>
      <div class="header-right">
        <div class="user-info">
          <a-avatar :size="32" style="background-color: #1677ff">
            {{ userInfo.username?.charAt(0) || 'U' }}
          </a-avatar>
          <span class="username">{{ userInfo.username }}</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：演讲控制面板 -->
      <div class="control-panel">
        <a-card title="放映区" class="control-card">
          <div class="control-content">
            <p class="control-placeholder">放映区</p>
          </div>
        </a-card>
      </div>

      <!-- 右侧：参与者面板 -->
      <div class="side-panel">
        <div class="side-panel-container">
          <!-- 预留卡片1 -->
          <a-card title="预留区域1" class="reserved-card-1">
            <div class="reserved-content">
              <p>此区域预留用于未来功能扩展</p>
            </div>
          </a-card>

          <!-- 预留卡片2 -->
          <a-card title="预留区域2" class="reserved-card-2">
            <div class="reserved-content">
              <p>此区域预留用于未来功能扩展</p>
            </div>
          </a-card>

          <!-- 固定高度父容器包裹OnlineChatPanel -->
          <div class="chat-panel-wrapper" style="height: 100%; min-height: 300px;">
            <OnlineChatPanel
              :users="participants"
              :onlineCount="onlineCount"
              :messages="discussionMessages"
              @send="sendDiscussion"
              style="height: 100%;"
            />
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  ArrowLeftOutlined
} from '@ant-design/icons-vue';
import { speechRoomAPI, checkTokenExpired, getToken } from '../../api';
import wsManager from '../../utils/websocket';
import eventBus from '../../utils/eventBus';
import OnlineChatPanel from '../../components/OnlineChatPanel.vue';

const route = useRoute();
const router = useRouter();

// 响应式数据
const roomId = computed(() => route.params.roomId);
const roomInfo = ref({
  id: null,
  name: '加载中...',
  description: '',
  creator_id: null,
  creator_name: '',
  speaker_id: null,
  speaker_name: '',
  status: 0,
  total_participants: 0,
  created_at: null
});
const userInfo = ref({
  user_id: null,
  username: localStorage.getItem('username') || '用户',
  role: 0
});
const userRole = ref(0); // 0-创建者，1-演讲者，2-听众
const participantCount = ref(0);
const loading = ref(true);

// 参与者相关
const participants = ref([]);
const onlineCount = ref(0);

// 讨论相关
const discussionInput = ref('');
const discussionMessages = ref([
  {
    user_id: 'system',
    username: '系统',
    message: '欢迎来到讨论区，开始您的讨论吧！',
    timestamp: new Date().toISOString()
  }
]);

// 在线人员显示控制
const showOnlineUsers = ref(false);

// WebSocket连接状态
const wsConnected = ref(false);

// 方法
const goBack = () => {
  router.push('/home');
};

const getStatusText = (status) => {
  const statusMap = {
    0: '等待开始',
    1: '进行中',
    2: '已结束'
  };
  return statusMap[status] || '未知';
};

const getStatusColor = (status) => {
  const colorMap = {
    0: 'orange',
    1: 'green',
    2: 'purple'
  };
  return colorMap[status] || 'default';
};

const getRoleText = (role) => {
  const roleMap = {
    0: '创建者',
    1: '演讲者',
    2: '听众'
  };
  return roleMap[role] || '未知';
};

const getRoleColor = (role) => {
  const colorMap = {
    0: 'blue',
    1: 'green',
    2: 'orange'
  };
  return colorMap[role] || 'default';
};



// 获取房间信息
const fetchRoomInfo = async () => {
  try {
    loading.value = true;
    const token = getToken();
    if (!token) {
      checkTokenExpired();
      return;
    }

    const response = await speechRoomAPI.enterRoom(roomId.value, token);
    const { room_info, user_info } = response.data;
    
    // 更新房间信息
    roomInfo.value = room_info;
    participantCount.value = room_info.total_participants;
    
    // 更新用户信息
    userInfo.value = user_info;
    userRole.value = user_info.role;
    
    console.log('房间信息:', room_info);
    console.log('用户信息:', user_info);
  } catch (error) {
    console.error('获取房间信息失败:', error);
    message.error(error.response?.data?.message || '获取房间信息失败');
  } finally {
    loading.value = false;
  }
};



// 发送讨论消息
const sendDiscussion = (msg) => {
  if (!msg || !msg.trim()) return;
  wsManager.sendMessage(msg.trim());
};


// WebSocket事件处理
const setupWebSocketEvents = () => {
  // 用户加入房间
  eventBus.on('userJoined', (data) => {
    console.log('用户加入:', data);
    // 添加新用户到参与者列表
    const newParticipant = {
      user_id: data.user_id,
      username: data.username,
      role: data.role
    };
    participants.value.push(newParticipant);
    onlineCount.value = participants.value.length;
    
    // 添加系统消息
    discussionMessages.value.push({
      user_id: 'system',
      username: '系统',
      message: `${data.username} 加入了房间`,
      timestamp: data.timestamp
    });
  });

  // 用户离开房间
  eventBus.on('userLeft', (data) => {
    console.log('用户离开:', data);
    // 从参与者列表中移除用户
    const index = participants.value.findIndex(p => p.user_id === data.user_id);
    if (index > -1) {
      participants.value.splice(index, 1);
      onlineCount.value = participants.value.length;
    }
    
    // 添加系统消息
    discussionMessages.value.push({
      user_id: 'system',
      username: '系统',
      message: `${data.username} 离开了房间`,
      timestamp: data.timestamp
    });
  });

  // 房间用户列表更新
  eventBus.on('roomUsersUpdated', (data) => {
    console.log('房间用户更新:', data);
    participants.value = data.users;
    onlineCount.value = data.total_online;
  });

  // 新消息
  eventBus.on('newMessage', (data) => {
    console.log('新消息:', data);
    discussionMessages.value.push({
      user_id: data.user_id,
      username: data.username,
      message: data.message,
      timestamp: data.timestamp
    });
  });
};

// 生命周期
onMounted(async () => {
  if (checkTokenExpired()) {
    return;
  }

  // 先获取房间信息
  await fetchRoomInfo();
  
  // 设置WebSocket事件监听
  setupWebSocketEvents();
  
  // 连接WebSocket
  wsManager.connect(
    roomId.value,
    userInfo.value.user_id,
    userInfo.value.username,
    userInfo.value.role
  );
  
  wsConnected.value = true;
});

onUnmounted(() => {
  // 断开WebSocket连接
  wsManager.disconnect();
  wsConnected.value = false;
});
</script>

<style scoped>
.speakerroom-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  max-width: 100vw;
  overflow-x: hidden;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px 30px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.header-center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 2;
}

.room-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1677ff;
  margin: 0;
  text-align: center;
}

.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 1;
}

.participant-count {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  color: #666;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-weight: 500;
  color: #333;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  height: calc(100vh - 140px);
  max-width: 100%;
  min-height: 0;
}

.control-panel {
  display: flex;
  flex-direction: column;
}

.control-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.3);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.control-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-placeholder {
  color: #999;
  font-style: italic;
  text-align: center;
  margin: 0;
}



.side-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.side-panel-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
  min-height: 0;
}

.participants-card,
.reserved-card-1,
.reserved-card-2 {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.reserved-card-1 {
  flex: 0 0 calc(20% - 16px);
  min-height: 120px;
}

.reserved-card-2 {
  flex: 0 0 calc(30% - 16px);
  min-height: 150px;
}

.participants-card {
  flex: 0 0 calc(50% - 16px);
  min-height: 300px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.participants-card :deep(.ant-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 12px;
  height: 0;
  min-height: 0;
}

/* 参与者卡片标题样式 */
.participants-card :deep(.ant-card-head) {
  min-height: 32px;
  padding: 8px 16px;
}

.participants-card :deep(.ant-card-head-title) {
  text-align: center;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.2;
  padding: 0;
}

/* 参与者容器样式 */
.participants-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  flex: 1;
  position: relative;
  min-height: 0;
}

/* 区域通用样式 */
.section {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

/* 在线人员覆盖层 */
.online-users-overlay {
  position: absolute;
  top: -12px;
  left: -12px;
  right: -12px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  height: 110px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}

.online-users-overlay.expanded {
  height: 260px;
}

.online-users-content {
  flex: 1;
  padding: 8px;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.online-users-content::-webkit-scrollbar {
  display: none;
}

.toggle-button-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2px 0;
  background: rgba(255, 255, 255, 0.9);
}

.custom-toggle-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 12px;
  color: #666;
  font-size: 10px;
  transition: all 0.2s ease;
  min-width: 40px;
}

.custom-toggle-button:hover {
  background-color: #f0f0f0;
  color: #333;
}

/* 讨论区包装器 */
.discussion-wrapper {
  flex: 0 0 80%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.discussion-spacer {
  height: 90px;
  flex-shrink: 0;
}

/* 第一部分：讨论区 */
.discussion-section {
  flex: 1;
  min-height: 200px;
  padding: 8px 0;
  position: relative;
  min-height: 0;
}

.discussion-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  background-color: #fafafa;
  border-radius: 4px;
  position: relative;
  z-index: 2;
  margin: 0 -4px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.discussion-content::-webkit-scrollbar {
  display: none;
}

.discussion-messages {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-item {
  display: flex;
  gap: 8px;
  font-size: 0.8rem;
}

.message-author {
  font-weight: 600;
  color: #1677ff;
  min-width: 40px;
}

.message-author.system {
  color: #999;
  font-style: italic;
}

.message-text {
  color: #333;
  flex: 1;
  word-break: break-word;
}

/* 第二部分：编辑讨论 */
.edit-section {
  flex: 0 0 20%;
  min-height: 80px;
  padding: 8px 0;
}

.edit-content {
  position: relative;
  padding: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: 0 -12px;
}

.edit-content :deep(.ant-input) {
  flex: 1;
  resize: none;
  margin-bottom: 8px;
  min-height: 60px;
  overflow: hidden;
}

.send-button {
  align-self: flex-end;
  margin-top: auto;
}

.reserved-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-style: italic;
}



.participant-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.participant-name {
  flex: 1;
  font-weight: 500;
  color: #333;
}

.chat-panel-wrapper {
  flex: 1 1 0%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}


/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 16px;
    height: auto;
  }

  .control-panel {
    order: -1;
  }

  .control-card {
    height: auto;
  }

  .side-panel {
    height: auto;
  }

  .reserved-card-1 {
    flex: 0 0 calc(20% - 16px);
    min-height: 100px;
  }

  .reserved-card-2 {
    flex: 0 0 calc(30% - 16px);
    min-height: 120px;
  }

  .participants-card {
    flex: 0 0 calc(50% - 16px);
    min-height: 250px;
  }
}

@media (max-width: 768px) {
  .speakerroom-container {
    padding: 16px;
  }

  .header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .header-left {
    flex-direction: column;
    gap: 8px;
    flex: none;
  }

  .header-center {
    flex: none;
  }

  .header-right {
    flex-direction: column;
    gap: 12px;
    flex: none;
  }
}
</style>