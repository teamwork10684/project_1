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
      <!-- 左侧：答题板 -->
      <div class="control-panel">
        <AnswerBoard
          v-if="answerBoardState !== 'no-question' && answerBoardQuestion"
          v-bind="answerBoardQuestion"
          @submit="handleSubmitAnswer"
        />
        <div
          v-else
          class="answer-board-placeholder"
        >
          当前未选择题目
        </div>
      </div>

      <!-- 右侧：参与者面板 -->
      <div class="side-panel">
        <div class="side-panel-container">
          <!-- 题目列表卡片 -->
          <a-card class="reserved-card-1" :body-style="{height: '100%', minHeight: '0', padding: '2px'}" :title="null">
            <QuestionListPanel :questions="questionList" @select="handleQuestionSelect" />
          </a-card>

          <!-- 统计信息卡片 -->
          <a-card class="reserved-card-2" :body-style="{height: '100%', minHeight: '0', padding: '2px'}" :title="null">
            <StatsPanel :stats="statsData" />
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
import { speechRoomAPI, checkTokenExpired, getToken, questionAPI, answerAPI, discussionAPI } from '../../api';
import wsManager from '../../utils/websocket';
import eventBus from '../../utils/eventBus';
import OnlineChatPanel from '../../components/OnlineChatPanel.vue';
import AnswerBoard from '../../components/AnswerBoard.vue';
import QuestionListPanel from '../../components/QuestionListPanel.vue';
import StatsPanel from '../../components/StatsPanel.vue';

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
const initialTip = {
  user_id: 'system',
  username: '系统',
  message: '欢迎来到讨论区，开始您的讨论吧！',
  timestamp: new Date().toISOString(),
  is_system: true
};
const discussionMessages = ref([]);

// 题目讨论信号处理
function handleQuestionDiscussion(data) {
  console.log('handleQuestionDiscussion', data);
  // 仅当当前答题板有题目且id匹配时追加
  if (!answerBoardQuestion.value || !data.question_id) return;
  if (data.question_id !== answerBoardQuestion.value.id) return;
  answerBoardQuestion.value.discussions.push(data);
}

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

// 展示数据提升到Room.vue
const answerBoardQuestion = ref(null); // 结构见下
const answerBoardState = ref('no-question'); // 'no-question' | 'in-progress' | 'ended'
const questionList = ref([]);
const statsData = ref({
  score: 0,
  accuracy: 0,
  correct: 0,
  wrong: 0,
  skip: 0,
});

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


// 获取当前进行中题目及其统计
const fetchCurrentQuestionAndStats = async () => {
  const token = getToken();
  // 获取所有被发布题目
  const res = await questionAPI.getPublishedQuestions(roomId.value, token);
  const publishedQuestions = res.data.published_questions || [];
  // 先找进行中的题目
  let current = publishedQuestions.find(q => q.status === 0);
  let status = 0;
  // 如果没有进行中的题目，找最新已结束的题目
  if (!current && publishedQuestions.length > 0) {
    // 假设题目有end_time字段，否则用id最大
    current = publishedQuestions
      .filter(q => q.status === 1)
      .sort((a, b) => {
        if (a.end_time && b.end_time) {
          return new Date(b.end_time) - new Date(a.end_time);
        }
        return b.id - a.id;
      })[0];
    status = 1;
  }
  if (!current) {
    answerBoardState.value = 'no-question';
    answerBoardQuestion.value = null;
    return;
  }
  // 获取统计信息
  const statsRes = await questionAPI.getQuestionStatisticsForAudience(current.id, token);
  const data = statsRes.data;
  // 组装答题板数据
  const qinfo = data.question_info;
  const stat = data.statistics;
  // 以接口返回的status为准
  status = data.time_info?.status ?? status;
  answerBoardState.value = status === 1 ? 'ended' : 'in-progress';
  answerBoardQuestion.value = {
    id: qinfo.id,
    question: qinfo.question,
    options: [
      { value: 'A', text: qinfo.option_a, count: stat.option_a_count },
      { value: 'B', text: qinfo.option_b, count: stat.option_b_count },
      { value: 'C', text: qinfo.option_c, count: stat.option_c_count },
      { value: 'D', text: qinfo.option_d, count: stat.option_d_count },
    ],
    statistics: stat,
    status,
    myAnswer: data.my_answer,
    correctValue: qinfo.answer,
    showCorrect: status === 1,
    showMyAnswer: !!data.my_answer,
    accuracy: stat.accuracy_rate,
    countdown: data.time_info.time_limit,
    start_time: data.time_info.start_time,
    end_time: data.time_info.end_time,
    discussions: []
  };
};

// 获取用户在房间内的答题统计
const fetchUserRoomStats = async () => {
  try {
    const token = getToken();
    if (!token) return;
    const res = await answerAPI.getUserRoomStatistics({ token, room_id: roomId.value });
    const data = res.data;
    statsData.value = {
      score: data.score || 0,
      accuracy: data.accuracy || 0,
      correct: data.correct_count || 0,
      wrong: data.wrong_count || 0,
      skip: data.skipped_count || 0,
    };
  } catch (err) {
    statsData.value = { score: 0, accuracy: 0, correct: 0, wrong: 0, skip: 0 };
  }
};

// 获取对特定题目讨论消息的API方法
async function fetchDiscussionMessages(questionId) {
  try {
    // Room.vue中token通过getToken()获取
    const token = getToken();
    const res = await discussionAPI.getQuestionDiscussions(questionId, token);
    answerBoardQuestion.value.discussions = res.data?.discussions || [];
    console.log('answerBoardQuestion.value.discussions', answerBoardQuestion.value.discussions);
  } catch (e) {
    console.log('fetchDiscussionMessages error', e);
    answerBoardQuestion.value.discussions = [];
  }
}

// 生命周期
onMounted(async () => {
  if (checkTokenExpired()) {
    return;
  }

  // 先获取房间信息
  await fetchRoomInfo();
  // 获取房间讨论列表
  await fetchRoomDiscussions();
  // 获取用户房间统计
  await fetchUserRoomStats();
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
  // 获取房间所有被发布题目
  try {
    const token = getToken();
    const res = await questionAPI.getPublishedQuestions(roomId.value, token);
    questionList.value = (res.data.published_questions || []).map(q => ({
      id: q.id, // 修复：加上id字段
      question: q.question,
      status: q.status // 0进行中 1已结束
    }));
  } catch (err) {
    message.error('获取题目列表失败');
  }
  // 获取当前进行中题目及其统计
  try {
    await fetchCurrentQuestionAndStats();
    // 新增：如果有当前题目，自动获取其讨论列表
    if (answerBoardQuestion.value && answerBoardQuestion.value.id) {
      await fetchDiscussionMessages(answerBoardQuestion.value.id);
    }
  } catch (err) {
    answerBoardState.value = 'no-question';
    answerBoardQuestion.value = null;
  }

  // 新增：监听题目生成事件，自动刷新题目列表
  eventBus.on('questionGenerated', async (data) => {
    if (data && String(data.room_id) === String(roomId.value)) {
      console.log('Room.vue 收到题目生成事件，刷新题目列表', data);
      try {
        const token = getToken();
        const res = await questionAPI.getPublishedQuestions(roomId.value, token);
        questionList.value = (res.data.published_questions || []).map(q => ({
          id: q.id,
          question: q.question,
          status: q.status
        }));
      } catch (err) {
        message.error('获取题目列表失败');
      }
    }
  });
  // 新增：监听题目发布事件，自动刷新题目列表
  eventBus.on('questionPublished', async (data) => {
    if (data && String(data.room_id) === String(roomId.value)) {
      console.log('Room.vue 收到题目发布事件，刷新题目列表', data);
      try {
        const token = getToken();
        const res = await questionAPI.getPublishedQuestions(roomId.value, token);
        questionList.value = (res.data.published_questions || []).map(q => ({
          id: q.id,
          question: q.question,
          status: q.status
        }));
        try {
          await fetchCurrentQuestionAndStats();
        } catch (err) {
          answerBoardState.value = 'no-question';
          answerBoardQuestion.value = null;
        }
      } catch (err) {
        message.error('获取题目列表失败');
      }
    }
  });
  // 新增：监听题目自动结束事件，自动刷新题目列表
  eventBus.on('questionEnded', async (data) => {
    if (data && String(data.room_id) === String(roomId.value)) {
      console.log('Room.vue 收到题目结束事件，刷新题目列表', data);
      try {
        const token = getToken();
        const res = await questionAPI.getPublishedQuestions(roomId.value, token);
        questionList.value = (res.data.published_questions || []).map(q => ({
          id: q.id,
          question: q.question,
          status: q.status
        }));
        // 新增：刷新答题板
        await fetchCurrentQuestionAndStats();
      } catch (err) {
        message.error('获取题目列表失败');
        // 即使失败也要尝试刷新答题板
        try {
          await fetchCurrentQuestionAndStats();
        } catch {}
      }
    }
    await fetchUserRoomStats();
  });
  // 新增：监听答题事件，自动刷新答题板
  eventBus.on('answerSubmitted', async (data) => {
    // 判断当前答题板的题目id和事件中的published_question_id是否一致
    if (
      answerBoardQuestion.value &&
      data.published_question_id === (questionList.value.find(q => q.status === 0)?.id)
    ) {
      await fetchCurrentQuestionAndStats();
    }
  });
  // 监听题目讨论信号
  eventBus.on('questionDiscussion', handleQuestionDiscussion);
});

onUnmounted(() => {
  // 断开WebSocket连接
  wsManager.disconnect();
  wsConnected.value = false;
  cleanupWebSocketEvents();
  eventBus.off('answerSubmitted');
  eventBus.off('questionDiscussion', handleQuestionDiscussion);
});

const handleQuestionSelect = async (item) => {
  try {
    const token = getToken();
    // item.id为published_question_id
    const statsRes = await questionAPI.getQuestionStatisticsForAudience(item.id, token);
    const data = statsRes.data;
    const qinfo = data.question_info;
    const stat = data.statistics;
    const status = data.time_info.status; // 0进行中 1已结束
    answerBoardState.value = status === 1 ? 'ended' : 'in-progress';
    answerBoardQuestion.value = {
      id: qinfo.id, // 新增
      question: qinfo.question,
      options: [
        { value: 'A', text: qinfo.option_a, count: stat.option_a_count },
        { value: 'B', text: qinfo.option_b, count: stat.option_b_count },
        { value: 'C', text: qinfo.option_c, count: stat.option_c_count },
        { value: 'D', text: qinfo.option_d, count: stat.option_d_count },
      ],
      statistics: stat,
      status,
      myAnswer: data.my_answer,
      correctValue: qinfo.answer,
      showCorrect: status === 1,
      showMyAnswer: !!data.my_answer,
      accuracy: stat.accuracy_rate,
      countdown: data.time_info.time_limit,
      start_time: data.time_info.start_time, // 新增
      end_time: data.time_info.end_time, // 新增
      discussions: []
    };
    // 获取该题目的讨论列表
    await fetchDiscussionMessages(qinfo.id);
  } catch (err) {
    answerBoardState.value = 'no-question';
    answerBoardQuestion.value = null;
  }
};

const handleSubmitAnswer = async (selected) => {
  try {
    const token = getToken();
    // 需要roomId, question_id, answer
    // question_id 需从answerBoardQuestion中获取
    // published_question_id 只用于统计，提交答案用原始question_id
    // 需保证answerBoardQuestion有question_id字段
    // 但当前answerBoardQuestion结构没有id，需在handleQuestionSelect和fetchCurrentQuestionAndStats中补充
    const questionId = answerBoardQuestion.value?.id || answerBoardQuestion.value?.question_id;
    if (!questionId) {
      message.error('题目信息缺失，无法提交');
      return;
    }
    await answerAPI.answerQuestion(roomId.value, {
      token,
      question_id: questionId,
      answer: selected
    });
    message.success('提交成功');
    // 提交后刷新答题板和统计
    await fetchCurrentQuestionAndStats();
    //await fetchUserRoomStats();
  } catch (err) {
    message.error(err?.response?.data?.message || '提交失败');
  }
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
  height: 100%;
  min-height: 0;
  flex: 1 1 0%;
  overflow: hidden;
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

.answer-board-placeholder {
  width: 100%;
  height: 100%;
  min-height: 240px;
  background: #fff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b3b3b3;
  font-size: 24px;
  font-weight: 500;
  box-shadow: 0 1px 4px rgba(22, 119, 255, 0.04);
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