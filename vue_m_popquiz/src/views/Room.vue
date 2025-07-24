<template>
  <div class="room-bg">
    <div class="room-topbar">
      <span class="back-arrow" @click="goBack">&#8592; {{ roomName || '房间' }}</span>
      <div class="topbar-right">
        <button class="topbar-btn" @click="showHistory">历史</button>
        <span class="topbar-timer">{{ countdown || '--:--' }}</span>
      </div>
    </div>
    <div class="main-vertical">
      <div class="question-card tight-card">
        <div class="question-title">
          <template v-if="currentQuestion && currentQuestion.question && options.length && options.some(opt => opt.text)">
            <span class="main-question-text">{{ currentQuestion.question }}</span>
            <div class="question-options vertical-options">
              <div v-for="opt in options" :key="opt.value" v-if="opt.text" class="option-row">
                <span class="option-label">{{ opt.value }}.</span>
                <span class="option-text">{{ opt.text }}</span>
              </div>
            </div>
          </template>
          <template v-else>
            暂无进行中的题目
          </template>
        </div>
        <button v-if="questionStatus === 0 && !myAnswer" class="publish-btn" :disabled="!selectedOption" @click="submitAnswer">提交</button>
      </div>
      <div class="stats-card tight-card">
        <div class="stats-title">正确率统计</div>
        <img src="https://img2.baidu.com/it/u=1813931372,1843083532&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=375" alt="统计图" class="stats-img" />
      </div>
      <div class="chat-card tight-card">
        <div class="chat-header">
          <span class="online-dot"></span> <span class="online-count">{{ onlineCount }}人在线</span>
        </div>
        <div class="chat-list">
          <div v-for="msg in chatList" :key="msg.id">
            <template v-if="msg.is_system || msg.username === '系统' || msg.username === '未知用户'">
              <div class="chat-msg-system">系统提示：{{ msg.content }}</div>
            </template>
            <template v-else>
              <div class="chat-msg">
                <span class="chat-username">{{ msg.username }}:</span>
                <span class="chat-content">{{ msg.content }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input-row">
      <input v-model="chatInput" placeholder="同学们可以说一下理由哦" />
      <button @click="sendChat">发送</button>
    </div>
    <!-- 历史题目弹窗 -->
    <div v-if="historyVisible" class="history-modal-bg">
      <div class="history-modal">
        <div class="history-title">历史题目</div>
        <div class="history-list-scroll">
          <div v-if="publishedQuestions.length === 0" class="history-empty">暂无历史题目</div>
          <div v-else>
            <div v-for="q in publishedQuestions" :key="q.id" class="history-question-item">
              <div class="history-q-content-main-row">
                <span class="history-q-content-main">{{ q.question }}</span>
                <button class="expand-btn" :aria-expanded="expandedQuestionId === q.id" @click="toggleExpandQuestion(q)">
                  <span :class="['expand-icon', expandedQuestionId === q.id ? 'expanded' : '']"></span>
                </button>
              </div>
              <div class="history-q-meta-row">
                <span class="history-q-status">{{ q.status === 0 ? '进行中' : '已结束' }}</span>
                <span class="history-q-time">{{ q.publish_time || q.created_at }}</span>
              </div>
              <div v-if="expandedQuestionId === q.id" class="history-q-expand">
                <div v-if="expandedQuestionStats.loading">加载中...</div>
                <div v-else-if="expandedQuestionStats.error" style="color:#f00;">{{ expandedQuestionStats.error }}</div>
                <template v-else>
                  <div class="expand-q-options">
                    <div v-for="opt in ['A','B','C','D']" :key="opt" :class="['expand-q-option', expandedQuestionStats.question_info.answer === opt ? 'expand-q-option-correct' : '']">
                      {{ opt }}) {{ expandedQuestionStats.question_info['option_' + opt.toLowerCase()] }}
                      <span v-if="expandedQuestionStats.question_info.answer === opt" class="expand-q-correct">✔</span>
                      <span class="expand-q-count">（{{ expandedQuestionStats.statistics['option_' + opt.toLowerCase() + '_count'] || 0 }}人）</span>
                    </div>
                  </div>
                  <div class="expand-q-stats-row">
                    总答题人数：{{ expandedQuestionStats.statistics.total_participants }}，
                    正确：{{ expandedQuestionStats.statistics.correct_count }}，
                    错误：{{ expandedQuestionStats.statistics.wrong_count }}，
                    正确率：{{ expandedQuestionStats.statistics.accuracy_rate }}%
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
        <!-- 用户统计 -->
        <div v-if="userStats" class="history-stats">
          <div class="history-stats-title">我的答题统计</div>
          <div>分数：{{ userStats.score }}</div>
          <div>正确率：{{ userStats.accuracy }}%</div>
          <div>正确题数：{{ userStats.correct_count }}</div>
          <div>错误题数：{{ userStats.wrong_count }}</div>
          <div>跳过题数：{{ userStats.skipped_count }}</div>
        </div>
        <button class="history-close-btn" @click="historyVisible = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { questionAPI, getToken, discussionAPI } from '@/api'
import axios from 'axios'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
import { io } from 'socket.io-client'
import wsManager from '@/utils/websocket'
import eventBus from '@/utils/eventBus'
let socket = null
dayjs.extend(duration)
const router = useRouter()
const route = useRoute()
const chatInput = ref('')
const roomName = ref(route.query.roomName || '')

// 新增：题目信息
const currentQuestion = ref(null)
const questionPublishTime = ref(null)
const questionLimitSeconds = ref(0)
const countdown = ref('')
let countdownTimer = null

// 新增：历史题目弹窗及数据
const historyVisible = ref(false)
const publishedQuestions = ref([])
const userStats = ref(null)
const expandedQuestionId = ref(null)
const expandedQuestionStats = ref({})

// 新增：聊天板相关
const chatList = ref([])
const onlineCount = ref(0)

// 新增：答题相关状态
const selectedOption = ref('')
const myAnswer = ref('')
const correctAnswer = ref('')
const options = ref([])
const questionStatus = ref(0) // 0进行中 1已结束
const showCorrect = ref(false)
const showMyAnswer = ref(false)

// 拉取历史消息时统一格式
async function fetchHistoryChats(roomId, token) {
  try {
    const res = await discussionAPI.getDiscussions(roomId, token)
    if (res.data && Array.isArray(res.data.discussions)) {
      chatList.value = res.data.discussions.map(d => ({
        id: d.id,
        username: d.username,
        content: d.content, // 统一用 content
        is_system: d.is_system
      }))
      onlineCount.value = res.data.discussions.length
    } else {
      chatList.value = []
      onlineCount.value = 0
    }
  } catch (e) {
    chatList.value = []
    onlineCount.value = 0
    window.$message?.error?.(e.response?.data?.message || '获取聊天记录失败')
  }
}

function handleNewMessage(data) {
  chatList.value.push({
    id: Date.now() + Math.random(),
    username: data.username,
    content: data.message, // 统一用 content
    is_system: data.is_system
  })
}

// 用户信息，优先从 localStorage 获取
const userInfo = ref({
  user_id: localStorage.getItem('user_id') || '',
  username: localStorage.getItem('username') || '用户',
  role: Number(localStorage.getItem('role')) || 2
})

async function toggleExpandQuestion(q) {
  if (expandedQuestionId.value === q.id) {
    expandedQuestionId.value = null
    expandedQuestionStats.value = {}
    return
  }
  expandedQuestionId.value = q.id
  expandedQuestionStats.value = { loading: true }
  const token = getToken()
  try {
    const res = await axios.get(`/popquiz/published-questions/${q.id}/statistics-for-audience`, { params: { token } })
    if (res.data && res.data.question_info && res.data.statistics) {
      expandedQuestionStats.value = res.data
    } else {
      expandedQuestionStats.value = { error: '暂无统计信息' }
    }
  } catch (e) {
    expandedQuestionStats.value = { error: '获取统计失败' }
  }
}

// 倒计时刷新函数
function updateCountdown() {
  if (!questionPublishTime.value || !questionLimitSeconds.value) {
    countdown.value = ''
    return
  }
  const now = dayjs()
  const end = dayjs(questionPublishTime.value).add(questionLimitSeconds.value, 'second')
  const diff = end.diff(now, 'second')
  if (diff <= 0) {
    countdown.value = '00:00'
    clearInterval(countdownTimer)
    countdownTimer = null
    return
  }
  const d = dayjs.duration(diff * 1000)
  const mm = String(Math.floor(diff / 60)).padStart(2, '0')
  const ss = String(diff % 60).padStart(2, '0')
  countdown.value = `${mm}:${ss}`
}

// 修改 fetchCurrentQuestionAndStats，获取题目和统计
async function fetchCurrentQuestionAndStats() {
  const roomId = route.params.id
  const token = getToken()
  if (!roomId || !token) return
  try {
    const res = await questionAPI.getCurrentQuestionForAudience(roomId, token)
    if (res.data && res.data.published_question && res.data.published_question.question) {
      const q = res.data.published_question
      // 兼容题干和选项结构
      let questionText = ''
      let optionA = '', optionB = '', optionC = '', optionD = ''
      if (q.question && typeof q.question === 'object') {
        questionText = q.question.question
        optionA = q.question.option_a
        optionB = q.question.option_b
        optionC = q.question.option_c
        optionD = q.question.option_d
      } else {
        questionText = q.question
        optionA = q.option_a
        optionB = q.option_b
        optionC = q.option_c
        optionD = q.option_d
      }
      currentQuestion.value = { ...q, question: questionText }
      questionPublishTime.value = q.publish_time || q.created_at
      questionLimitSeconds.value = q.time_limit || 0
      questionStatus.value = q.status || 0
      correctAnswer.value = q.answer || ''
      myAnswer.value = q.my_answer || ''
      showCorrect.value = questionStatus.value === 1
      showMyAnswer.value = !!myAnswer.value
      options.value = [
        { value: 'A', text: optionA, count: q.option_a_count },
        { value: 'B', text: optionB, count: q.option_b_count },
        { value: 'C', text: optionC, count: q.option_c_count },
        { value: 'D', text: optionD, count: q.option_d_count }
      ]
      if (questionPublishTime.value && questionLimitSeconds.value) {
        updateCountdown()
        if (countdownTimer) clearInterval(countdownTimer)
        countdownTimer = setInterval(updateCountdown, 1000)
      }
    } else {
      currentQuestion.value = null
      questionPublishTime.value = null
      questionLimitSeconds.value = 0
      countdown.value = ''
      questionStatus.value = 0
      correctAnswer.value = ''
      myAnswer.value = ''
      showCorrect.value = false
      showMyAnswer.value = false
      options.value = []
      if (countdownTimer) clearInterval(countdownTimer)
      countdownTimer = null
    }
  } catch (e) {
    currentQuestion.value = null
    questionPublishTime.value = null
    questionLimitSeconds.value = 0
    countdown.value = ''
    questionStatus.value = 0
    correctAnswer.value = ''
    myAnswer.value = ''
    showCorrect.value = false
    showMyAnswer.value = false
    options.value = []
    if (countdownTimer) clearInterval(countdownTimer)
    countdownTimer = null
  }
}

// 新增：答题提交
async function submitAnswer() {
  if (!selectedOption.value) return
  const roomId = route.params.id
  const token = getToken()
  try {
    await axios.post(`/popquiz/speech-rooms/${roomId}/answer-question`, {
      token,
      question_id: currentQuestion.value?.id,
      answer: selectedOption.value
    })
    myAnswer.value = selectedOption.value
    showMyAnswer.value = true
    selectedOption.value = ''
    await fetchCurrentQuestionAndStats()
  } catch (e) {
    // 可加错误提示
  }
}

// 获取所有已发布题目
async function fetchPublishedQuestions() {
  const roomId = route.params.id
  const token = getToken()
  if (!roomId || !token) return
  try {
    const res = await questionAPI.getPublishedQuestions(roomId, token)
    if (res.data && Array.isArray(res.data.published_questions)) {
      publishedQuestions.value = res.data.published_questions
    } else {
      publishedQuestions.value = []
    }
  } catch {
    publishedQuestions.value = []
  }
}

// 进入房间后自动获取最新题目和讨论列表
onMounted(async () => {
  const roomId = route.params.id
  const token = getToken()
  if (!roomId || !token) return
  try {
    // 获取题目
    await fetchCurrentQuestionAndStats()
    // 获取讨论列表（历史消息）
    await fetchHistoryChats(roomId, token)
    await fetchPublishedQuestions()
  } catch (e) {
    currentQuestion.value = null
    questionPublishTime.value = null
    questionLimitSeconds.value = 0
    countdown.value = ''
    questionStatus.value = 0
    correctAnswer.value = ''
    myAnswer.value = ''
    showCorrect.value = false
    showMyAnswer.value = false
    options.value = []
    if (countdownTimer) clearInterval(countdownTimer)
    countdownTimer = null
    chatList.value = []
    onlineCount.value = 0
  }

  // WebSocket 连接（只用 wsManager）
  const userId = localStorage.getItem('user_id') || localStorage.getItem('userid') || localStorage.getItem('username')
  const username = localStorage.getItem('username') || '用户'
  const role = Number(localStorage.getItem('role')) || 2
  if (!token || !roomId || !userId) {
    console.log('ws connect skipped: missing token/userId/roomId', token, userId, roomId)
    return
  }
  wsManager.connect(roomId, userId, username, role)
  eventBus.on('newMessage', handleNewMessage)
  eventBus.on('answerSubmitted', fetchCurrentQuestionAndStats)
  eventBus.on('questionPublished', async (data) => {
    // 新题目推送，刷新题目栏和历史题目
    await fetchPublishedQuestions()
    await fetchCurrentQuestionAndStats()
  })
})

onUnmounted(() => {
  wsManager.disconnect()
  eventBus.off('newMessage', handleNewMessage)
  eventBus.off('answerSubmitted', fetchCurrentQuestionAndStats)
  eventBus.off('questionPublished')
})

// 历史按钮点击事件
async function showHistory() {
  const roomId = route.params.id
  const token = getToken()
  if (!roomId || !token) return
  try {
    // 1. 获取历史题目
    await fetchPublishedQuestions()
    // 2. 获取用户统计
    const statsRes = await axios.post('/popquiz/user-room-statistics', {
      token,
      room_id: roomId
    })
    if (statsRes.data) {
      userStats.value = statsRes.data
    } else {
      userStats.value = null
    }
    historyVisible.value = true
  } catch (e) {
    publishedQuestions.value = []
    userStats.value = null
    historyVisible.value = true
  }
}

async function sendChat() {
  const content = chatInput.value.trim()
  if (!content) return
  wsManager.sendMessage(content)
  chatInput.value = ''
}
function goBack() {
  router.push('/')
}
</script>

<style scoped>
.room-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5faff 0%, #e3e8f0 100%);
  padding: 0;
}
.room-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  padding: 0 20px;
  height: 54px;
  border-radius: 0 0 18px 18px;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(22,119,255,0.06);
}
.back-arrow {
  font-size: 22px;
  color: #1677ff;
  cursor: pointer;
  user-select: none;
  font-weight: 700;
  transition: color 0.2s;
}
.back-arrow:hover {
  color: #0d5ad7;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.topbar-btn {
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 6px 22px;
  font-size: 16px;
  font-weight: 700;
  margin-right: 8px;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
  transition: background 0.2s;
}
.topbar-btn:hover {
  background: linear-gradient(90deg, #0d5ad7 0%, #1677ff 100%);
}
.topbar-timer {
  background: #fff;
  color: #1677ff;
  border-radius: 10px;
  padding: 6px 18px;
  font-size: 16px;
  font-weight: 700;
  border: 1.5px solid #1677ff;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
}
.main-vertical {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 54px - 70px);
  margin: 0;
  gap: 18px;
  padding: 18px 0 0 0;
}
.tight-card {
  margin: 0 18px 0 18px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(22,119,255,0.06);
}
.question-card, .stats-card, .chat-card {
  background: #fff;
  padding: 18px 20px 14px 20px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.question-card { height: 36%; }
.stats-card { height: 20%; border-top: 1px solid #e0e0e0; margin-top: 10px; }
.chat-card { height: 44%; border-top: 1px solid #e0e0e0; margin-top: 10px; }
.question-title {
  font-size: 22px;
  font-weight: bold;
  color: #1677ff;
  margin-bottom: 18px;
  letter-spacing: 0.5px;
  text-align: center;
}
.main-question-text {
  font-size: 1.35em;
  font-weight: 700;
  color: #222;
  display: block;
  margin-bottom: 0;
  line-height: 1.7;
  word-break: break-word;
}
.vertical-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 10px;
  align-items: stretch;
}
.option-block {
  width: 100%;
  display: flex;
  align-items: center;
  background: #fff;
  border: 2px solid #e6e6e6;
  border-radius: 10px;
  padding: 16px 18px;
  font-size: 1.1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(22,119,255,0.03);
  margin: 0;
}
.option-block:hover {
  border-color: #1677ff;
  background: #f0f7ff;
}
.option-block.my-selected {
  background: #1677ff;
  color: #fff;
  border-color: #1677ff;
}
.option-block.correct {
  background: #eaffea;
  color: #52c41a;
  border-color: #52c41a;
}
.option-block.wrong {
  background: #fffbe6;
  color: #ff9800;
  border-color: #ff9800;
}
.option-label {
  font-weight: 700;
  margin-right: 16px;
  font-size: 1.1em;
}
.option-text {
  flex: 1;
  text-align: left;
  font-size: 1.1em;
  font-weight: 600;
}
.option-count {
  color: #888;
  font-size: 0.98em;
  margin-left: 12px;
}
.question-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 28px;
  margin-bottom: 10px;
  align-items: center;
}
.option {
  font-size: 16px;
  color: #1677ff;
  padding: 4px 16px;
  border-radius: 8px;
  background: #f0f7ff;
  font-weight: 600;
  transition: background 0.2s, color 0.2s;
  cursor: pointer;
}
.option.correct {
  color: #1ca01c;
  font-weight: bold;
  background: #eafbe7;
}
.option.my-selected {
  background: #e6f7ff;
  border: 1px solid #1677ff;
  color: #1677ff;
  font-weight: bold;
}
.option.wrong {
  background: #fffbe6;
  border: 1px solid #ff9800;
  color: #ff9800;
  font-weight: bold;
}
.publish-btn {
  margin-left: auto;
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 6px 28px;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
  transition: background 0.2s;
}
.publish-btn:hover {
  background: linear-gradient(90deg, #0d5ad7 0%, #1677ff 100%);
}
.publish-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  color: #888;
}
.correct-badge, .my-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 6px;
  margin-left: 8px;
  font-weight: bold;
}
.correct-badge {
  background: #eafbe7;
  color: #1ca01c;
}
.my-badge {
  background: #e6f7ff;
  color: #1677ff;
}
.stats-title {
  font-size: 16px;
  font-weight: 700;
  color: #1677ff;
  margin-bottom: 10px;
}
.stats-img {
  width: 100%;
  border-radius: 10px;
  margin-top: 6px;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
}
.chat-header {
  font-size: 16px;
  font-weight: 700;
  color: #1677ff;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
}
.online-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  background: #52c41a;
  border-radius: 50%;
  margin-right: 2px;
}
.online-count {
  color: #52c41a;
  font-size: 15px;
  font-weight: 600;
}
.chat-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  font-size: 15px;
  color: #333;
  padding-left: 2px;
}
.chat-msg {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  line-height: 1.6;
}
.chat-username {
  font-weight: 600;
  color: #1677ff;
  margin-right: 2px;
}
.chat-system {
  color: #888;
  font-style: italic;
}
.chat-content {
  word-break: break-all;
}
.chat-input-row {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 0 0 18px 18px;
  margin: 0;
  padding: 14px 18px;
  box-shadow: 0 2px 12px rgba(22,119,255,0.06);
  border-top: 1.5px solid #e0e0e0;
}
.chat-input-row input {
  flex: 1;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px;
  margin-right: 10px;
  font-size: 16px;
  background: #f5faff;
  transition: border 0.2s;
}
.chat-input-row input:focus {
  border: 1.5px solid #1677ff;
}
.chat-input-row button {
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 22px;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
  transition: background 0.2s;
}
.chat-input-row button:hover {
  background: linear-gradient(90deg, #0d5ad7 0%, #1677ff 100%);
}
.history-modal-bg {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.history-modal {
  background: #fff;
  border-radius: 32px;
  padding: 36px 36px 24px 36px;
  min-width: 480px;
  max-width: 98vw;
  box-shadow: 0 12px 48px 0 rgba(22,119,255,0.13), 0 2px 12px 0 rgba(22,119,255,0.08);
  height: 640px;
  display: flex;
  flex-direction: column;
  position: relative;
}
.history-list-scroll {
  flex: 1 1 auto;
  overflow-y: auto;
  max-height: 340px;
  margin-bottom: 14px;
  padding-bottom: 12px;
}
.history-title {
  font-size: 25px;
  font-weight: bold;
  color: #1677ff;
  margin-bottom: 26px;
  text-align: center;
  letter-spacing: 1px;
}
.history-empty {
  color: #888;
  text-align: center;
  padding: 48px 0;
  font-size: 18px;
}
.history-question-item {
  background: #f5faff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(22,119,255,0.08);
  border: 2px solid #e6f0ff;
  margin-bottom: 22px;
  padding: 22px 20px 14px 20px;
  transition: box-shadow 0.2s;
}
.history-question-item:last-child {
  margin-bottom: 0;
}
.history-q-content-main-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.history-q-content-main {
  font-size: 21px;
  font-weight: bold;
  color: #222;
  margin-bottom: 0;
  line-height: 1.8;
  flex: 1;
  transition: background 0.2s;
  word-break: break-all;
}
.expand-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #e6f0ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 1.5px 6px rgba(22,119,255,0.08);
  margin-left: 8px;
  outline: none;
  position: relative;
}
.expand-btn:active, .expand-btn:focus {
  background: #d0e6ff;
}
.expand-icon {
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  position: relative;
  transition: transform 0.25s cubic-bezier(.4,2,.6,1), background 0.2s;
}
.expand-icon::before {
  content: '';
  display: block;
  position: absolute;
  left: 4px;
  top: 8px;
  width: 10px;
  height: 2.5px;
  background: #1677ff;
  border-radius: 2px;
  transition: background 0.2s;
}
.expand-icon::after {
  content: '';
  display: block;
  position: absolute;
  left: 8px;
  top: 4px;
  width: 2.5px;
  height: 10px;
  background: #1677ff;
  border-radius: 2px;
  transition: background 0.2s, opacity 0.2s;
}
.expand-icon.expanded {
  transform: rotate(180deg);
}
.expand-icon.expanded::after {
  opacity: 0;
}
.history-q-meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 15px;
  color: #888;
}
.history-q-status {
  font-weight: 700;
  color: #1677ff;
}
.history-q-time {
  color: #bbb;
  font-size: 14px;
}
.history-close-btn {
  margin: 28px auto 0 auto;
  display: block;
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 14px 48px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(22,119,255,0.10);
  transition: background 0.2s;
  position: absolute;
  left: 50%;
  bottom: 18px;
  transform: translateX(-50%);
  z-index: 3;
}
.history-close-btn:hover {
  background: linear-gradient(90deg, #0d5ad7 0%, #1677ff 100%);
}
.history-q-expand {
  background: #f8faff;
  border-radius: 12px;
  margin: 12px 0 0 0;
  padding: 16px 18px 10px 18px;
  font-size: 16px;
  color: #333;
}
.expand-q-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
}
.expand-q-option {
  padding: 3px 0;
  font-size: 16px;
  color: #1677ff;
  font-weight: 600;
}
.expand-q-option-correct {
  color: #1ca01c;
  font-weight: bold;
}
.expand-q-correct {
  color: #1ca01c;
  margin-left: 8px;
}
.expand-q-count {
  color: #888;
  font-size: 14px;
  margin-left: 10px;
}
.expand-q-ans-row {
  margin: 10px 0 4px 0;
  font-size: 16px;
}
.expand-q-ans {
  color: #1ca01c;
  font-weight: bold;
}
.expand-q-stats-row {
  color: #888;
  font-size: 15px;
  margin-top: 4px;
}
.history-stats {
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 70px;
  background: #f5faff;
  border-radius: 0 0 28px 28px;
  border-top: 1.5px solid #e6f0ff;
  color: #333;
  font-size: 16px;
  padding: 18px 24px 10px 24px;
  z-index: 2;
  box-shadow: 0 2px 12px rgba(22,119,255,0.04);
  text-align: center;
}
.history-stats-title {
  font-size: 17px;
  font-weight: bold;
  color: #1677ff;
  margin-bottom: 8px;
}
.chat-msg-system {
  text-align: center;
  color: #ff9800;
  background: #fffbe6;
  border-radius: 8px;
  padding: 4px 12px;
  margin: 4px 0;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 1px;
}
.option-row {
  display: flex;
  align-items: center;
  font-size: 1.1em;
  margin-bottom: 8px;
}
.option-label {
  font-weight: 700;
  margin-right: 16px;
  font-size: 1.1em;
}
.option-text {
  flex: 1;
  text-align: left;
  font-size: 1.1em;
  font-weight: 600;
}
</style> 