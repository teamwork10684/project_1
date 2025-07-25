<template>
  <div class="room-bg">
    <div class="room-topbar">
      <span class="back-arrow" @click="goBack">&#8592; {{ roomName || '房间' }}</span>
      <div class="topbar-right">
        <button class="topbar-btn" @click="showHistory">历史</button>
        <span class="topbar-timer" v-if="countdown">{{ countdown }}</span>
        <span class="topbar-timer" v-else>--:--</span>
      </div>
    </div>
    <div class="main-vertical">
      <div class="question-card tight-card">
        <div class="question-title">
          <template v-if="currentQuestion && currentQuestion.question && options.length && options.some(opt => opt.text)">
            <span class="main-question-text">{{ currentQuestion.question }}</span>
            <div class="question-options vertical-options">
              <div v-for="opt in options" :key="opt.value" :class="['option-row', {selected: selectedOption === opt.value}]" @click="selectedOption = opt.value">
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
        <!-- <div class="stats-title">选项统计</div> -->
        <div class="stats-options-panel" v-if="currentStats && options.length">
           <table class="stats-table">
             <tbody>
               <tr v-for="opt in options" :key="opt.value">
                 <td class="stats-td stats-option-label">{{ opt.value }}</td>
                 <td class="stats-td">
                   <span :class="['stats-count', currentStats['option_' + opt.value.toLowerCase() + '_count'] > 0 ? 'stats-count-active' : '']">
                     {{ currentStats['option_' + opt.value.toLowerCase() + '_count'] || 0 }}
                   </span>
                 </td>
               </tr>
               <tr>
                 <td class="stats-td stats-unselected-label" colspan="2">
                   <span class="unselected-label-text">未选择人数</span>
                   <span class="unselected-count">{{ currentStats.unselected_count || 0 }}</span>
                 </td>
               </tr>
             </tbody>
           </table>
        </div>
        <div v-else>暂无统计数据</div>
      </div>
      <div class="chat-card tight-card">
        <div class="chat-header">
          <span class="online-dot"></span> <span class="online-count">{{ onlineCount }}人在线</span>
        </div>
        <div class="chat-list" ref="chatListRef">
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
      <input v-model="chatInput" placeholder="请分享您的看法" />
      <button @click="sendChat">发送</button>
    </div>
    <!-- 历史题目弹窗 -->
    <div v-if="historyVisible" class="history-modal-bg">
      <div class="history-modal">
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
                  <!-- 新增：题目讨论区 -->
                  <div class="expand-q-discussions">
                    <div v-if="expandedQuestionDiscussions.loading">讨论加载中...</div>
                    <div v-else-if="expandedQuestionDiscussions.error" style="color:#f00;">{{ expandedQuestionDiscussions.error }}</div>
                    <template v-else>
                      <div v-if="Array.isArray(expandedQuestionDiscussions) && expandedQuestionDiscussions.length === 0" style="color:#888;">暂无讨论</div>
                      <div v-else>
                        <div v-for="d in expandedQuestionDiscussions" :key="d.id" class="expand-q-discussion-item">
                          <span class="expand-q-discussion-username">{{ d.username }}：</span>
                          <span class="expand-q-discussion-content">{{ d.content }}</span>
                          <span class="expand-q-discussion-time">{{ d.created_at }}</span>
                        </div>
                      </div>
                    </template>
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { questionAPI, getToken, discussionAPI, speechRoomAPI } from '@/api'
import axios from 'axios'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
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
const expandedQuestionDiscussions = ref({})

// 新增：聊天板相关
const chatList = ref([])
const onlineCount = ref(0)
const chatListRef = ref(null)

// 新增：在线用户列表
const onlineUsers = ref([])

// 新增：答题相关状态
const selectedOption = ref('')
const myAnswer = ref('')
const correctAnswer = ref('')
const options = ref([])
const questionStatus = ref(0) // 0进行中 1已结束
const showSubmit = ref(false)
const showMyAnswer = ref(false)
const currentStats = ref(null) // 新增：当前题目统计数据

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
      // 新增：拉取历史消息后自动滚动到底部
      nextTick(() => {
        if (chatListRef.value) {
          chatListRef.value.scrollTop = chatListRef.value.scrollHeight
        }
      })
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
  nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
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
    expandedQuestionDiscussions.value = {}
    return
  }
  expandedQuestionId.value = q.id
  expandedQuestionStats.value = { loading: true }
  expandedQuestionDiscussions.value = { loading: true }
  const token = getToken()
  try {
    
    // 获取统计信息
    const statsRes = await axios.get(`/popquiz/published-questions/${q.id}/statistics-for-audience`, { params: { token } })
    if (statsRes.data && statsRes.data.question_info && statsRes.data.statistics) {
      expandedQuestionStats.value = statsRes.data
    } else {
      expandedQuestionStats.value = { error: '暂无统计信息' }
    }
  } catch (e) {
    expandedQuestionStats.value = { error: '获取统计失败' }
  }

  try {
    
    console.log('获取题目讨论信息', q.question_id)
    // 获取讨论信息
    const discussRes = await discussionAPI.getQuestionDiscussions(q.question_id, token)
    console.log('获取题目讨论信息', discussRes)
    if (discussRes.data && Array.isArray(discussRes.data.discussions)) {
      expandedQuestionDiscussions.value = discussRes.data.discussions
      console.log('获取题目讨论信息成功', discussRes.data.discussions)
    } else {
      expandedQuestionDiscussions.value = []
      console.log('获取题目讨论信息为空', discussRes)
    }
  } catch (e) {
    expandedQuestionDiscussions.value = { error: '获取讨论失败' }
    console.log('获取题目讨论信息失败', e)
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
    // 倒计时结束自动刷新题目
    fetchCurrentQuestion()
    return
  }
  const mm = String(Math.floor(diff / 60)).padStart(2, '0')
  const ss = String(diff % 60).padStart(2, '0')
  countdown.value = `${mm}:${ss}`
}

// 实现 fetchCurrentQuestion 方法，调用后端接口获取题目
async function fetchCurrentQuestion() {
  const roomId = route.params.id
  const token = getToken()
  if (!roomId || !token) return
  try {
    const res = await questionAPI.getCurrentQuestionForAudience(roomId, token)
    if (res.data && res.data.published_question && res.data.published_question.question) {
      const q = res.data.published_question
      // 题干和选项都在 q.question 里
      currentQuestion.value = {
        id: q.id, // published_question.id
        question_id: q.question_id, // 新增：原始题目id
        question: q.question.question,
        hasAnswered: q.has_answered,
        userAnswer: q.user_answer
      }
      // 记录发布时间和限时
      questionPublishTime.value = q.start_time
      questionLimitSeconds.value = q.time_limit
      // 启动倒计时
      if (countdownTimer) clearInterval(countdownTimer)
      updateCountdown()
      countdownTimer = setInterval(updateCountdown, 1000)
      // 在 fetchCurrentQuestion 赋值 options 时，过滤掉无效选项
      options.value = [
        { value: 'A', text: q.question.option_a },
        { value: 'B', text: q.question.option_b },
        { value: 'C', text: q.question.option_c },
        { value: 'D', text: q.question.option_d }
      ].filter(opt => typeof opt.text === 'string' && opt.text.trim().length > 0)
      showSubmit.value = !q.has_answered && q.status === 0
    } else {
      currentQuestion.value = null
      options.value = []
      showSubmit.value = false
      questionPublishTime.value = null
      questionLimitSeconds.value = 0
      countdown.value = ''
      if (countdownTimer) clearInterval(countdownTimer)
      countdownTimer = null
    }
  } catch (e) {
    currentQuestion.value = null
    options.value = []
    showSubmit.value = false
    questionPublishTime.value = null
    questionLimitSeconds.value = 0
    countdown.value = ''
    if (countdownTimer) clearInterval(countdownTimer)
    countdownTimer = null
  }
}

// 题目提交按钮逻辑（接口实现）
async function submitAnswer() {
  if (!selectedOption.value || !currentQuestion.value) return
  const roomId = route.params.id
  const token = getToken()
  // 修正：始终用原始题目的 question_id
  const questionId = currentQuestion.value.question_id
  const answer = selectedOption.value
  try {
    const res = await axios.post(`/popquiz/speech-rooms/${roomId}/answer-question`, {
      token,
      question_id: questionId,
      answer
    })
    window.$message?.success?.('答题成功！')
    selectedOption.value = ''
    await fetchCurrentQuestion()
  } catch (e) {
    window.$message?.error?.(e.response?.data?.message || '提交失败')
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

// 获取当前题目的统计数据
async function fetchCurrentStats() {
  if (!currentQuestion.value || !currentQuestion.value.id) {
    currentStats.value = null
    return
  }
  const publishedQuestionId = currentQuestion.value.id // published_question.id
  const token = getToken()
  try {
    const res = await axios.get(`/popquiz/published-questions/${publishedQuestionId}/statistics-for-audience`, { params: { token } })
    if (res.data && res.data.statistics) {
      currentStats.value = res.data.statistics
    } else {
      currentStats.value = null
    }
  } catch (e) {
    currentStats.value = null
  }
}

// 移除 fetchOnlineParticipants 相关内容

// 进入房间后自动获取最新题目和讨论列表
onMounted(async () => {
  const roomId = route.params.id
  const token = getToken()
  if (!roomId || !token) return
  try {
    // 获取题目
    await fetchCurrentQuestion()
    // 获取题目统计
    await fetchCurrentStats()
    // 获取讨论列表（历史消息）
    await fetchHistoryChats(roomId, token)
    await fetchPublishedQuestions()
    // 移除：await fetchOnlineParticipants(roomId, token)
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
    onlineUsers.value = []
    currentStats.value = null
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
  eventBus.on('answerSubmitted', async () => {
    await fetchCurrentQuestion()
    await fetchCurrentStats()
  })
  eventBus.on('questionPublished', async (data) => {
    // 新题目推送，刷新题目栏和历史题目
    await fetchPublishedQuestions()
    await fetchCurrentQuestion()
    await fetchCurrentStats() // 新增：刷新统计数据
  })
  // 监听 room_users 信号
  wsManager.socket?.on('room_users', (data) => {
    onlineCount.value = data.total_online || (data.users ? data.users.length : 0)
    onlineUsers.value = data.users || []
  })
  // 新增：监听 user_joined/user_left 信号
  wsManager.socket?.on('user_joined', () => {
    onlineCount.value++
  })
  wsManager.socket?.on('user_left', () => {
    if (onlineCount.value > 0) onlineCount.value--
  })
  // 保留 join/left 事件用于动画等（可选）
})

onUnmounted(() => {
  wsManager.disconnect()
  eventBus.off('newMessage', handleNewMessage)
  eventBus.off('answerSubmitted', fetchCurrentQuestion)
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
  // 新增：调用 RESTful API 存储消息
  const roomId = route.params.id
  const token = getToken()
  try {
    await discussionAPI.createDiscussion({
      token,
      room_id: roomId,
      content,
      question_id: -1 // 或根据实际需求传递题目ID
    })
  } catch (e) {
    // 可选：提示用户消息存储失败
    window.$message?.error?.(e.response?.data?.message || '消息存储失败')
  }
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
.question-card {
  height: 36%;
  max-height: 260px;
  min-height: 180px;
  overflow-y: auto;
  background: #fff;
  padding: 18px 16px 14px 16px; /* 左右padding一致，选项与题目左对齐 */
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(22,119,255,0.06);
}
.question-title {
  font-size: 18px;
  font-weight: bold;
  color: #1677ff;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  text-align: center;
}
.main-question-text {
  font-size: 0.98em;
  font-weight: 700;
  color: #222;
  display: block;
  margin-bottom: 0;
  line-height: 1.7;
  word-break: break-word;
  text-align: left;
  padding: 0;
}
.question-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 14px 0 0 0;
  align-items: stretch;
}
.option-row {
  display: flex;
  align-items: center;
  font-size: 0.91em;
  margin-bottom: 0;
  padding-left: 0; /* 继承父容器对齐 */
  background: #f5faff;
  border-radius: 8px;
  /* 移除 box-shadow、border、margin-left 等 */
  box-shadow: none;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.option-row.selected {
  background: #e6f0ff;
}
.option-label {
  font-weight: 600;
  margin-right: 7px;
  color: #1677ff;
  font-size: 1em;
  text-align: left;
}
.option-text {
  font-size: 0.97em;
  color: #222;
  text-align: left;
  word-break: break-word;
}
.option-count {
  color: #888;
  font-size: 0.98em;
  margin-left: 12px;
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
  max-height: 260px;
  min-height: 120px;
  background: #fff;
  scroll-behavior: smooth;
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
  max-height: 480px;
  /* margin-bottom: 14px; */
  /* padding-bottom: 12px; */
  margin-bottom: 0;
  padding-bottom: 0;
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
  margin-bottom: 0;
  padding: 22px 20px 14px 20px;
  transition: box-shadow 0.2s;
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
  font-size: 0.92em;
  margin: 0;
  padding: 6px 0;
  border-radius: 8px;
  background: #f5faff;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: none;
  border: none;
  text-align: left;
}
.option-row.selected {
  background: #e6f4ff;
  color: #1677ff;
}
.option-label {
  font-weight: 600;
  margin-right: 6px;
  padding: 0;
  font-size: 1em;
}
.option-text {
  padding: 0;
  margin: 0;
  text-align: left;
  flex: 1;
  font-size: 0.98em;
  word-break: break-word;
}
.stats-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}
.stats-th {
  text-align: left;
  font-weight: 700;
  color: #222;
  padding: 4px 0 6px 0;
  font-size: 15px;
}
.stats-td {
  text-align: left;
  padding: 3px 0 3px 0;
  font-size: 15px;
  color: #222;
}
.stats-option-label {
  color: #1677ff;
  font-weight: bold;
  width: 48px;
}
.stats-unselected-label {
  color: #888;
  font-size: 13px;
  padding-top: 8px;
  padding-bottom: 2px;
  text-align: left;
  vertical-align: middle;
}
.unselected-label-text {
  color: #888;
  font-size: 13px;
  margin-right: 8px;
}
.unselected-count {
  display: inline-block;
  min-width: 18px;
  padding: 2px 10px;
  border-radius: 4px;
  background: #f5faff;
  color: #222;
  font-weight: 500;
  font-size: 14px;
  vertical-align: middle;
}
.stats-count {
  display: inline-block;
  min-width: 18px;
  padding: 2px 10px;
  border-radius: 4px;
  background: #f5faff;
  color: #222;
  font-weight: 500;
  text-align: left;
}
.stats-count-active {
  background: #1677ff;
  color: #fff;
}
/* 新增讨论区样式 */
.expand-q-discussions {
  margin-top: 14px;
  background: #f5faff;
  border-radius: 8px;
  padding: 10px 12px;
}
.expand-q-discussion-item {
  font-size: 15px;
  color: #333;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.expand-q-discussion-username {
  color: #1677ff;
  font-weight: 600;
}
.expand-q-discussion-content {
  flex: 1;
}
.expand-q-discussion-time {
  color: #bbb;
  font-size: 13px;
  margin-left: 8px;
}
</style> 