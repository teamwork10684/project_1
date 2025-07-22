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
        <a-card class="control-card" :bodyStyle="{padding: '0', height: '100%'}" :headStyle="{display: 'none'}">
            <DocumentPlayerPanel
              style="height:100%;width:100%"
              :roomId="Number(roomId)"
              :token="token"
              :roomStatus="roomInfo.status"
              :canUpload="roomInfo.status !== 2"
              :loading="loading"
              @start-speech="handleStartSpeech"
              @end-speech="handleEndSpeech"
              @page-change="handlePageChange"
            />
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
                :questionList="publishedQuestions"
                :discussionMessages="[]"
                :roomId="roomId"
                :token="token"
                @selectQuestion="handleStatsSelectQuestion"
                @back="handleStatsBack"
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
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  ArrowLeftOutlined,
} from '@ant-design/icons-vue';
import { speechRoomAPI, checkTokenExpired, getToken, questionAPI, discussionAPI } from '../../api';
import wsManager from '../../utils/websocket';
import eventBus from '../../utils/eventBus';
import OnlineChatPanel from '../../components/OnlineChatPanel.vue';
import QuestionPublishPanel from '../../components/QuestionPublishPanel.vue';
import QuestionStatsBar from '../../components/QuestionStatsBar.vue';
import DocumentPlayerPanel from '../../components/DocumentPlayerPanel.vue';

const route = useRoute();
const router = useRouter();

// 响应式数据
const roomId = computed(() => route.params.roomId);
const token = computed(() => getToken());
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
const initialTip = {
  user_id: 'system',
  username: '系统',
  message: '欢迎来到讨论区，开始您的讨论吧！',
  timestamp: new Date().toISOString(),
  is_system: true
};
const discussionMessages = ref([]);

// 获取房间讨论列表
const fetchRoomDiscussions = async () => {
  try {
    const token = getToken();
    if (!token) return;
    const res = await discussionAPI.getDiscussions(roomId.value, token);
    let msgs = (res.data.discussions || []).map(d => ({
      user_id: d.user_id,
      username: d.username,
      message: d.content,
      timestamp: d.created_at,
      is_system: d.is_system
    }));
    msgs.push(initialTip);
    discussionMessages.value = msgs;
  } catch (e) {
    discussionMessages.value = [initialTip];
  }
};

// 事件处理函数定义
function handleUserJoined(data) {
  if (!participants.value.some(p => p.user_id === data.user_id)) {
    participants.value.push({
      user_id: data.user_id,
      username: data.username,
      role: data.role
    });
    onlineCount.value = participants.value.length;
    // discussionMessages.value.push({
    //   user_id: 'system',
    //   username: '系统',
    //   message: `${data.username} 加入了房间`,
    //   timestamp: data.timestamp
    // });
  }
}
function handleUserLeft(data) {
  const index = participants.value.findIndex(p => p.user_id === data.user_id);
  if (index > -1) {
    participants.value.splice(index, 1);
    onlineCount.value = participants.value.length;
    // discussionMessages.value.push({
    //   user_id: 'system',
    //   username: '系统',
    //   message: `${data.username} 离开了房间`,
    //   timestamp: data.timestamp
    // });
  }
}
function handleRoomUsersUpdated(data) {
  // 去重赋值
  const uniqueUsers = [];
  const seen = new Set();
  for (const u of data.users) {
    if (!seen.has(u.user_id)) {
      uniqueUsers.push(u);
      seen.add(u.user_id);
    }
  }
  participants.value = uniqueUsers;
  onlineCount.value = data.total_online;
}
function handleNewMessage(data) {
  discussionMessages.value.push({
    user_id: data.user_id,
    username: data.username,
    message: data.message,
    timestamp: data.timestamp,
    is_system: data.is_system
  });
}

function setupWebSocketEvents() {
  eventBus.on('userJoined', handleUserJoined);
  eventBus.on('userLeft', handleUserLeft);
  eventBus.on('roomUsersUpdated', handleRoomUsersUpdated);
  eventBus.on('newMessage', handleNewMessage);
}

function cleanupWebSocketEvents() {
  eventBus.off('userJoined', handleUserJoined);
  eventBus.off('userLeft', handleUserLeft);
  eventBus.off('roomUsersUpdated', handleRoomUsersUpdated);
  eventBus.off('newMessage', handleNewMessage);
}

// 在线人员显示控制
const showOnlineUsers = ref(false);

// WebSocket连接状态
const wsConnected = ref(false);

// 题目数据
const questions = ref([]);
const publishedQuestions = ref([]);

// 预留操作方法
const handleAutoPublish = () => {
  // TODO: 自动发布实现
};
const handleSaveSettings = (settings) => {
  console.log('保存设置:', settings);
};

const handlePublishQuestion = async (question) => {
  if (roomInfo.value.status !== 1) {
    message.warning('只有在演讲进行中才能发布题目');
    return;
  }
  try {
    // 获取本地存储的答题限时
    const answerTimeLimit = parseInt(localStorage.getItem('answerTimeLimit')) || 60;
    const res = await questionAPI.publishQuestion(roomId.value, {
      token: token.value,
      question_id: question.id,
      time_limit: answerTimeLimit
    });
    message.success('题目发布成功');
    await fetchQuestions();
    await fetchPublishedQuestions(); // 新增：发布成功后刷新已发布题目列表
  } catch (e) {
    message.error(e?.response?.data?.message || '题目发布失败');
  }
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
    roomInfo.value = room_info;
    participantCount.value = room_info.total_participants;
    userInfo.value = user_info;
    userRole.value = user_info.role;
    await fetchQuestions();
    await fetchPublishedQuestions();
    console.log('房间信息:', room_info);
    console.log('用户信息:', user_info);
  } catch (error) {
    console.error('获取房间信息失败:', error);
    message.error(error.response?.data?.message || '获取房间信息失败');
  } finally {
    loading.value = false;
  }
};

const fetchQuestions = async () => {
  try {
    const res = await questionAPI.getCreatedQuestions(roomId.value, token.value);
    if (res.data && Array.isArray(res.data.questions)) {
      questions.value = res.data.questions;
    } else {
      questions.value = [];
    }
  } catch (e) {
    questions.value = [];
    message.error(e?.response?.data?.message || '获取题目列表失败');
  }
};

const fetchPublishedQuestions = async () => {
  try {
    const res = await questionAPI.getPublishedQuestions(roomId.value, token.value);
    if (res.data && Array.isArray(res.data.published_questions)) {
      publishedQuestions.value = res.data.published_questions;
    } else {
      publishedQuestions.value = [];
    }
  } catch (e) {
    publishedQuestions.value = [];
    message.error(e?.response?.data?.message || '获取已发布题目列表失败');
  }
};


// 发送讨论消息
const sendDiscussion = (msg) => {
  if (!msg || !msg.trim()) return;
  wsManager.sendMessage(msg.trim());
};


// WebSocket事件处理
// setupWebSocketEvents 和 cleanupWebSocketEvents 现在在 onMounted 和 onUnmounted 中调用

// 生命周期
onMounted(async () => {
  if (checkTokenExpired()) {
    return;
  }

  // 先获取房间信息
  await fetchRoomInfo();
  // 获取房间讨论列表
  await fetchRoomDiscussions();
  
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

  // 新增：监听题目生成事件，自动刷新题目列表
  eventBus.on('questionGenerated', (data) => {
    if (data && String(data.room_id) === String(roomId.value)) {
      console.log('收到题目生成事件，刷新题目列表', data);
      fetchQuestions();
    }
  });

  // 新增：监听题目自动结束事件，自动刷新统计
  eventBus.on('questionEnded', (data) => {
    if (data && String(data.room_id) === String(roomId.value)) {
      console.log('Speakerroom.vue 收到题目结束事件，刷新统计', data);
      fetchPublishedQuestions();
    }
  });
});

let pageTimer = null;
let lastPageInfo = { fileId: null, page: null };
let requestedPages = new Set();

const handlePageChange = ({ fileId, page }) => {
  // 只有进行中才允许自动生成题目
  if (roomInfo.value.status !== 1) return;
  // 清除上一个计时器
  if (pageTimer) clearTimeout(pageTimer);
  // 记录当前页
  lastPageInfo = { fileId, page };
  // 10秒后触发
  pageTimer = setTimeout(async () => {
    if (roomInfo.value.status !== 1) return;
    const key = `${fileId}_${page}`;
    if (!fileId || !page || requestedPages.has(key)) return;
    try {
      const resp = await questionAPI.generateQuestionByFilePage({
        token: token.value,
        file_id: fileId,
        page: page
      });
      requestedPages.add(key);
      console.log(`已请求生成第${page}页的题目`, resp);
    } catch (e) {
      console.error(e?.response?.data?.message || `请求生成第${page}页题目失败`, e);
    }
  }, 10000);
};

onUnmounted(() => {
  if (pageTimer) clearTimeout(pageTimer);
  wsManager.disconnect();
  wsConnected.value = false;
  cleanupWebSocketEvents();
});

const handleStartSpeech = async () => {
  try {
    await speechRoomAPI.startSpeech(roomId.value, token.value);
    message.success('演讲开始');
    await fetchRoomInfo();
  } catch (e) {
    message.error(e?.response?.data?.message || '开始演讲失败');
  }
};
const handleEndSpeech = async () => {
  try {
    await speechRoomAPI.endSpeech(roomId.value, token.value);
    message.success('演讲已结束');
    await fetchRoomInfo();
  } catch (e) {
    message.error(e?.response?.data?.message || '结束演讲失败');
  }
};

const handleStatsSelectQuestion = (item) => {
  // 现在QuestionStatsBar组件自己处理数据获取，这里只需要处理其他逻辑
  console.log('题目被选择:', item);
};

const handleStatsBack = () => {
  // 现在QuestionStatsBar组件自己处理返回逻辑，这里只需要处理其他逻辑
  console.log('返回题目列表');
};
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
  overflow: hidden;
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.reserved-card-2 {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
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
  min-height: 0;
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
  width: 100%;
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
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