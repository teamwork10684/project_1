<template>
  <div class="room-bg">
    <div class="room-topbar">
      <span class="back-arrow" @click="goBack">&#8592; 数据结构</span>
      <div class="topbar-right">
        <button class="topbar-btn">历史</button>
        <span class="topbar-timer">2:23</span>
      </div>
    </div>
    <div class="main-vertical">
      <div class="question-card tight-card">
        <div class="question-title">
          4.以下哪种数据结构通常用于实现LIFO（后进先出）原则？
        </div>
        <div class="question-options">
          <span class="option correct">A) 栈</span>
          <span class="option">B) 链表</span>
          <span class="option">C) 二叉树</span>
          <span class="option">D) 队列</span>
          <button class="publish-btn">提交</button>
        </div>
      </div>
      <div class="stats-card tight-card">
        <div class="stats-title">正确率统计</div>
        <img src="https://img2.baidu.com/it/u=1813931372,1843083532&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=375" alt="统计图" class="stats-img" />
      </div>
      <div class="chat-card tight-card">
        <div class="chat-header">
          聊天板 <span class="online-dot"></span> <span class="online-count">10人在线</span>
        </div>
        <div class="chat-list">
          <div>A: 肯定选B！</div>
          <div>B: 我看未必</div>
        </div>
      </div>
    </div>
    <div class="chat-input-row">
      <input v-model="chatInput" placeholder="同学们可以说一下理由哦" />
      <button @click="sendChat">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const chatInput = ref('')
function sendChat() {
  chatInput.value = ''
}
function goBack() {
  router.push('/')
}
</script>

<style scoped>
.room-bg {
  min-height: 100vh;
  background: #ededed;
  padding: 0;
}
.room-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #eaeaea;
  padding: 0 16px;
  height: 48px;
  border-radius: 0 0 12px 12px;
  margin-bottom: 0;
}
.back-arrow {
  font-size: 20px;
  color: #888;
  cursor: pointer;
  user-select: none;
  font-weight: 600;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.topbar-btn {
  background: #222;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 4px 18px;
  font-size: 15px;
  font-weight: 600;
  margin-right: 8px;
}
.topbar-timer {
  background: #222;
  color: #fff;
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 15px;
  font-weight: 600;
}
.main-vertical {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 48px - 60px);
  margin: 0;
  gap: 0;
}
.tight-card {
  margin: 0;
  border-radius: 0;
  box-shadow: none;
}
.question-card, .stats-card, .chat-card {
  background: #fff;
  padding: 10px 14px 8px 14px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.question-card { height: 38%; }
.stats-card { height: 21%; border-top: 1px solid #e0e0e0; }
.chat-card { height: 41%; border-top: 1px solid #e0e0e0; }
.question-title {
  font-size: 17px;
  font-weight: bold;
  color: #222;
  margin-bottom: 8px;
}
.question-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 18px;
  margin-bottom: 6px;
  align-items: center;
}
.option {
  font-size: 15px;
  color: #222;
  padding: 2px 8px;
  border-radius: 6px;
  background: #f7faff;
}
.option.correct {
  color: #1ca01c;
  font-weight: bold;
  background: #eafbe7;
}
.publish-btn {
  margin-left: auto;
  background: #222;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 4px 18px;
  font-size: 15px;
  font-weight: 600;
}
.stats-title {
  font-size: 15px;
  font-weight: 600;
  color: #1677ff;
  margin-bottom: 6px;
}
.stats-img {
  width: 100%;
  border-radius: 8px;
  margin-top: 4px;
}
.chat-header {
  font-size: 15px;
  font-weight: 600;
  color: #1677ff;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.online-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #52c41a;
  border-radius: 50%;
  margin-right: 2px;
}
.online-count {
  color: #52c41a;
  font-size: 13px;
}
.chat-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
  font-size: 14px;
  color: #333;
}
.chat-input-row {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 0 0 12px 12px;
  margin: 0;
  padding: 10px 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border-top: 1px solid #e0e0e0;
}
.chat-input-row input {
  flex: 1;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 8px;
  margin-right: 8px;
  font-size: 15px;
}
.chat-input-row button {
  background: #222;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 15px;
}
</style> 