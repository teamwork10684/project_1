<template>
  <div class="chat-panel">
    <!-- 顶部栏 -->
    <div class="chat-header" @mouseenter="showToggleBtn = true" @mouseleave="showToggleBtn = false">
      <span>{{ onlineCount }}人在线</span>
      <transition name="toggle-btn">
        <button 
          v-show="showToggleBtn" 
          class="toggle-btn" 
          @click="toggleUsers"
          :class="{ 'active': showUsers }"
        >
          <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </transition>
    </div>
    <!-- 用户列表下拉 -->
    <transition name="dropdown">
    <div v-if="showUsers" class="user-dropdown">
        <div class="user-dropdown-content">
      <div v-for="user in users" :key="user.user_id" class="user-item">
            <span class="role-tag" :class="roleClass(user.role)">{{ roleText(user.role) }}</span>
        <span>{{ user.username }}</span>
          </div>
        </div>
      </div>
    </transition>
    <!-- 讨论区 -->
    <div class="chat-messages" ref="chatMessages" @scroll="handleScroll">
      <div
        v-for="msg in messages"
        :key="msg.timestamp + msg.username"
        class="msg"
        :class="{ self: msg.username === myName, system: msg.is_system === true }"
      >
        <template v-if="!msg.is_system">
          <span class="bubble-avatar">{{ msg.username?.charAt(0) || 'U' }}</span>
          <span class="bubble" :class="{ self: msg.username === myName }">
            {{ msg.message }}
          </span>
        </template>
        <template v-else>
          <span class="bubble system">{{ msg.message }}</span>
        </template>
      </div>
    </div>
    
    <!-- 悬浮滚动到底部按钮 -->
    <transition name="scroll-btn">
      <button 
        v-show="showScrollBtn" 
        class="scroll-to-bottom-btn"
        @click="scrollToBottom"
        title="滚动到底部"
      >
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M7 13L12 18L17 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </transition>
    <!-- 输入区 -->
    <div class="chat-input">
      <input v-model="input" @keyup.enter="send" placeholder="输入讨论内容..." />
      <button @click="send">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue';

const props = defineProps({
  users: {
    type: Array,
    default: () => []
  },
  onlineCount: {
    type: Number,
    default: 0
  },
  messages: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(['send']);

const showUsers = ref(false);
const showToggleBtn = ref(false);
const showScrollBtn = ref(false);
const input = ref('');
const chatMessages = ref(null);

const myName = computed(() => {
  // 尝试从localStorage获取当前用户名
  return localStorage.getItem('username') || '';
});

const toggleUsers = () => {
  showUsers.value = !showUsers.value;
};

const send = () => {
  if (!input.value.trim()) return;
  emit('send', input.value.trim());
  input.value = '';
  
  // 发送消息后自动滚动到底部
  setTimeout(() => {
    scrollToBottom();
  }, 100);
};

const handleScroll = () => {
  if (!chatMessages.value) return;
  
  const { scrollTop, scrollHeight, clientHeight } = chatMessages.value;
  const isAtBottom = scrollTop + clientHeight >= scrollHeight - 50; // 增加容差到50px
  
  // 如果用户在底部，隐藏按钮
  if (isAtBottom) {
    showScrollBtn.value = false;
  } else {
    // 如果用户不在底部，显示按钮
    showScrollBtn.value = true;
  }
};

const scrollToBottom = () => {
  if (!chatMessages.value) return;
  
  console.log('执行滚动到底部');
  
  // 使用 nextTick 确保DOM更新后再滚动
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTo({
        top: chatMessages.value.scrollHeight,
        behavior: 'smooth'
      });
      
      // 备用方法：直接设置scrollTop
      setTimeout(() => {
        if (chatMessages.value) {
          chatMessages.value.scrollTop = chatMessages.value.scrollHeight;
        }
      }, 200);
    }
  });
};

// 检查滚动位置并更新按钮状态
const checkScrollPosition = () => {
  nextTick(() => {
    if (chatMessages.value) {
      const { scrollTop, scrollHeight, clientHeight } = chatMessages.value;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 50; // 增加容差到50px
      
      console.log('滚动位置检查:', {
        scrollTop,
        scrollHeight,
        clientHeight,
        isAtBottom,
        willShowButton: !isAtBottom
      });
      
      // 如果用户在底部，隐藏按钮并自动滚动
      if (isAtBottom) {
        showScrollBtn.value = false;
        scrollToBottom();
      } else {
        // 如果用户不在底部，显示按钮
        showScrollBtn.value = true;
      }
    }
  });
};

// 监听消息数组变化
watch(() => props.messages.length, (newLength, oldLength) => {
  console.log('消息长度变化:', { 
    oldLength, 
    newLength,
    hasNewMessage: newLength > oldLength 
  });
  
  if (newLength > oldLength) {
    // 有新消息到达时，检查滚动位置
    console.log('检测到新消息，检查滚动位置');
    
    // 延迟检查，确保DOM已更新
    setTimeout(() => {
      if (chatMessages.value) {
        const { scrollTop, scrollHeight, clientHeight } = chatMessages.value;
        const isAtBottom = scrollTop + clientHeight >= scrollHeight - 50; // 增加容差到50px
        
        console.log('新消息滚动检查:', {
          scrollTop,
          scrollHeight,
          clientHeight,
          isAtBottom,
          difference: scrollHeight - (scrollTop + clientHeight)
        });
        
        // 如果用户在底部，自动滚动到最新消息
        if (isAtBottom) {
          showScrollBtn.value = false;
          scrollToBottom();
        } else {
          // 如果用户不在底部，显示按钮
          showScrollBtn.value = true;
        }
      }
    }, 100);
  }
});

const roleText = (role) => {
  if (role === 0) return '创建者';
  if (role === 1) return '演讲者';
  if (role === 2) return '听众';
  return '未知';
};
const roleClass = (role) => {
  if (role === 0) return 'creator';
  if (role === 1) return 'speaker';
  if (role === 2) return 'audience';
  return '';
};
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #e3eafc 100%);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
.chat-header {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: rgba(255,255,255,0.95);
  position: relative;
  z-index: 2;
  font-size: 1.05rem;
  font-weight: 500;
}
.toggle-btn {
  background: rgba(22, 119, 255, 0.1);
  border: 1px solid rgba(22, 119, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  color: #1677ff;
  padding: 6px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.15);
}

.toggle-btn:hover {
  background: rgba(22, 119, 255, 0.2);
  border-color: rgba(22, 119, 255, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.25);
}

.toggle-btn.active {
  background: rgba(22, 119, 255, 0.25);
  border-color: rgba(22, 119, 255, 0.5);
}

.toggle-btn.active .toggle-icon {
  transform: rotate(180deg);
}

.toggle-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 下拉按钮显示/隐藏过渡 */
.toggle-btn-enter-active,
.toggle-btn-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toggle-btn-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(-2px);
}

.toggle-btn-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(-2px);
}

.toggle-btn-enter-to,
.toggle-btn-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: top;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-20px);
  max-height: 0;
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-20px);
  max-height: 0;
}

.dropdown-enter-to,
.dropdown-leave-from {
  opacity: 1;
  transform: translateY(0);
  max-height: 220px;
}

.user-dropdown {
  position: absolute;
  top: 52px;
  left: 0;
  right: 0;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  z-index: 10;
  max-height: 220px;
  overflow: hidden;
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
  padding: 8px 0;
}

.user-dropdown-content {
  overflow-y: auto;
  max-height: 220px; /* Match user-dropdown max-height */
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  font-size: 15px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin: 0 4px;
  border-radius: 8px;
}

.user-item:hover {
  background: rgba(22, 119, 255, 0.08);
  transform: translateX(4px);
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1677ff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
}
.role-tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  color: #fff;
  font-weight: 500;
  min-width: 40px;
  text-align: center;
  display: inline-block;
}
.role-tag.creator {
  background: #1677ff;
}
.role-tag.speaker {
  background: #52c41a;
}
.role-tag.audience {
  background: #faad14;
}
.chat-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 18px 12px 12px 12px;
  background: linear-gradient(135deg, #fafdff 0%, #e3eafc 100%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  scrollbar-width: none;
  -ms-overflow-style: none;
  position: relative;
}
.chat-messages::-webkit-scrollbar {
  display: none;
}
.msg {
  display: flex;
  align-items: center; /* 修正为居中对齐 */
  gap: 8px;
  font-size: 14px;
  padding: 2px 0;
  position: relative;
}
.msg.self {
  flex-direction: row-reverse;
}
.msg.system {
  justify-content: center;
}
.author {
  font-weight: 600;
  color: #1677ff;
  min-width: 40px;
  font-size: 13px;
  margin-bottom: 2px;
}
.author.system {
  color: #1677ff;
  font-style: normal;
  font-weight: bold;
}
.bubble {
  display: inline-block;
  padding: 8px 14px;
  border-radius: 8px;
  background: #fff;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  max-width: 70%;
  word-break: break-word;
  font-size: 14px;
  margin-bottom: 2px;
  transition: background 0.2s;
}
.bubble.self {
  background: linear-gradient(90deg, #eafff0 0%, #b7eb8f 100%);
  color: #389e0d;
  text-align: left;
}
.bubble.system {
  background: none !important;
  color: #1677ff;
  font-style: normal;
  font-weight: bold;
  text-align: center;
  box-shadow: none;
  font-size: 13px;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-left: 0;
  margin-right: 0;
  padding: 0;
}
.bubble.system::before {
  content: '📢';
  font-size: 1em;
  margin-right: 4px;
}
.chat-input {
  display: flex;
  align-items: center;
  padding: 12px 12px 14px 12px;
  background: rgba(255,255,255,0.98);
  box-shadow: 0 -2px 8px rgba(0,0,0,0.03);
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
  gap: 10px;
}
.chat-input input {
  flex: 1;
  border: 1.5px solid #e6e6e6;
  border-radius: 18px;
  padding: 10px 16px;
  font-size: 15px;
  outline: none;
  margin-right: 0;
  background: #fafdff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  transition: border 0.2s;
}
.chat-input input:focus {
  border: 1.5px solid #1677ff;
  background: #fff;
}
.chat-input button {
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  color: #fff;
  border: none;
  border-radius: 18px;
  padding: 8px 22px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
  transition: background 0.2s;
}
.chat-input button:hover {
  background: linear-gradient(90deg, #0958d9 0%, #1677ff 100%);
}

.bubble-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1677ff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  margin-right: 6px;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
}
.msg.self .bubble-avatar {
  background: #52c41a;
  margin-left: 6px;
  margin-right: 0;
}

/* 悬浮滚动到底部按钮 */
.scroll-to-bottom-btn {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(22, 119, 255, 0.9);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
  backdrop-filter: blur(10px);
}

.scroll-to-bottom-btn:hover {
  background: rgba(22, 119, 255, 1);
  transform: translateX(-50%) translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.4);
}

.scroll-to-bottom-btn svg {
  width: 20px;
  height: 20px;
}

/* 悬浮按钮过渡动画 */
.scroll-btn-enter-active,
.scroll-btn-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.scroll-btn-enter-from {
  opacity: 0;
  transform: translateX(-50%) scale(0.8) translateY(10px);
}

.scroll-btn-leave-to {
  opacity: 0;
  transform: translateX(-50%) scale(0.8) translateY(10px);
}

.scroll-btn-enter-to,
.scroll-btn-leave-from {
  opacity: 1;
  transform: translateX(-50%) scale(1) translateY(0);
}

/* 响应式优化 */
@media (max-width: 600px) {
  .chat-panel {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .chat-header {
    height: 44px;
    padding: 0 10px;
    font-size: 0.98rem;
  }
  .user-dropdown {
    top: 44px;
    padding: 0 2px;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
  }
  .user-dropdown-content {
    max-height: 180px; /* Adjust for smaller screens */
  }
  .user-item {
    padding: 8px 10px;
    font-size: 14px;
  }
  .avatar {
    width: 22px;
    height: 22px;
    font-size: 13px;
  }
  .chat-messages {
    padding: 8px 4px 8px 4px;
    gap: 4px;
  }
  .bubble {
    padding: 6px 10px;
    font-size: 13px;
    max-width: 90%;
  }
  .chat-input {
    padding: 8px 4px 10px 4px;
    gap: 6px;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
  }
  .chat-input input {
    padding: 7px 10px;
    font-size: 13px;
    border-radius: 12px;
  }
  .chat-input button {
    padding: 6px 12px;
    font-size: 13px;
    border-radius: 12px;
  }
}
</style> 