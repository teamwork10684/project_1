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
        <a-card title="演讲控制" class="control-card">
          <div class="control-content">
            <p class="control-placeholder">演讲控制功能已移除</p>
          </div>
        </a-card>
      </div>

      <!-- 右侧：参与者面板 -->
      <div class="side-panel">
        <div class="side-panel-container">
          <!-- 预留卡片1 -->
          <a-card class="reserved-card-1">
            <div class="reserved-content-1">
              <QuestionPublishPanel
                :questions="questions"
                @autoPublish="handleAutoPublish"
                @publishQuestion="handlePublishQuestion"
                @saveSettings="handleSaveSettings"
              />
            </div>
          </a-card>

          <!-- 预留卡片2 -->
          <a-card class="reserved-card-2">
            <div class="reserved-content-2">
              <QuestionStatsBar
                :question="'太阳从哪边升起？'"
                :options="[
                  { label: 'A', text: '长文本选项长文本选项长文本选项长文本选项长文本选项长文本选项长文本选项长文本选项长文本选项长文本选项长文本选项', count: 20 },
                  { label: 'B', text: '西边', count: 2 },
                  { label: 'C', text: '南边', count: 1 },
                  { label: 'D', text: '北边', count: 20 }
                ]"
                :unselectedCount="3"
                :accuracy="0.75"
                :correctLabel="'A'"
                :endTime="'2025-07-14T18:53:00'"
              />
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
  ArrowLeftOutlined,
} from '@ant-design/icons-vue';
import { speechRoomAPI, checkTokenExpired, getToken } from '../../api';
import wsManager from '../../utils/websocket';
import eventBus from '../../utils/eventBus';
import OnlineChatPanel from '../../components/OnlineChatPanel.vue';
import QuestionPublishPanel from '../../components/QuestionPublishPanel.vue';
import QuestionStatsBar from '../../components/QuestionStatsBar.vue';

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

// 题目数据
const questions = ref([
  {
    id: 1,
    raw_text: "太阳从哪边升起？",
    prompt: "请根据以下内容出一道选择题",
    question: "太阳从哪边升起？",
    option_a: "东边",
    option_b: "西边", 
    option_c: "南边",
    option_d: "北边",
    answer: "A",
    created: true,
    published: false,
    created_at: "2024-01-01T10:00:00Z"
  },
  {
    id: 2,
    raw_text: "Python是一种什么类型的编程语言？",
    prompt: "请根据以下内容出一道选择题",
    question: "Python是一种什么类型的编程语言？",
    option_a: "编译型语言",
    option_b: "解释型语言",
    option_c: "汇编语言",
    option_d: "机器语言",
    answer: "B",
    created: true,
    published: true,
    created_at: "2024-01-01T11:00:00Z"
  },
  {
    id: 3,
    raw_text: "Vue.js的核心特性是什么？",
    prompt: "请根据以下内容出一道选择题",
    question: "Vue.js的核心特性是什么？",
    option_a: "响应式数据绑定",
    option_b: "组件化开发",
    option_c: "虚拟DOM",
    option_d: "以上都是",
    answer: "D",
    created: true,
    published: false,
    created_at: "2024-01-01T12:00:00Z"
  }
]);

// 预留操作方法
const handleAutoPublish = () => {
  // TODO: 自动发布实现
};
const handleSaveSettings = (settings) => {
  console.log('保存设置:', settings);
  // TODO: 保存设置实现
};

const handlePublishQuestion = (question) => {
  // TODO: 发布题目实现
};

// 方法
const goBack = () => {
  router.push('/home');
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
  flex: 0 0 calc(30% - 16px);
  min-height: 120px;
}

.reserved-card-2 {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.reserved-card-2 :deep(.ant-card-body) {
  flex: 1;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 0 !important;
}

.reserved-content-2 {
  flex: 1;
  display: flex;
  flex-direction: column;
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

.reserved-card-1 :deep(.ant-card-body) {
  padding: 6px !important;
  height: 100%;
}

.reserved-content-1 {
  position: relative;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 0 0 0 0;
  min-height: 220px;
  background: transparent;
}

/* 按钮区域样式 */
.button-area {
  position: absolute;
  top: 16px;
  right: 24px;
  display: flex;
  gap: 12px;
  z-index: 2;
}

.auto-publish-btn {
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  border: none;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.2);
}

.auto-publish-btn:hover {
  background: linear-gradient(90deg, #0958d9 0%, #1677ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
}

.publish-settings-btn {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  background: #fff;
  color: #666;
}

.publish-settings-btn:hover {
  border-color: #1677ff;
  color: #1677ff;
  transform: translateY(-1px);
}

/* 题目列表容器 */
.question-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  margin: 0 16px;
  padding: 48px 0 0 0;
  min-height: 220px;
}

.question-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px 8px 24px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.question-list-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.question-count {
  font-size: 14px;
  color: #666;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
}

/* 题目列表 */
.question-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 24px 8px 24px;
}

.question-item {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;
}

.question-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.question-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.question-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  line-height: 1.4;
  margin-right: 12px;
}

.question-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.question-status.status-0 {
  background: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.question-status.status-1 {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.question-status.status-2 {
  background: #f9f0ff;
  color: #722ed1;
  border: 1px solid #d3adf7;
}

.question-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.question-actions .ant-btn {
  font-size: 12px;
  height: 24px;
  padding: 0 8px;
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