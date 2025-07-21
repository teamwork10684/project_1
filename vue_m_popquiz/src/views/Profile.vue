<template>
  <div class="profile-bg">
    <a-card class="profile-card" bordered>
      <div class="profile-header">
        <div>
          <div class="profile-nickname">昵称：路飞</div>
          <div class="profile-username">账号：海贼王</div>
        </div>
        <a-button type="primary" danger class="logout-btn" @click="logout">退出登录</a-button>
      </div>
      <a-divider />
      <a-button type="default" class="edit-btn" block>编辑个人资料</a-button>

      <!-- My Courses Section -->
      <a-card class="course-card" hoverable>
        <template #title>
          <a-icon type="star" style="color:#1677ff" /> 我的课程
        </template>
        <div class="course-list-empty">暂无课程</div>
      </a-card>

      <!-- My Questions Section -->
      <a-card class="questions-card" hoverable>
        <template #title>
          <a-icon type="question-circle" style="color:#1890ff" /> 我的问题
        </template>
        <div class="questions-list-empty">暂无问题</div>
      </a-card>

      <!-- Submit Content Section -->
      <a-card class="submit-card" hoverable>
        <template #title>
          <a-icon type="form" style="color:#9254de" /> 提交内容
        </template>
        <div class="submit-content-placeholder">
          <p>在这里提交您的问题、反馈或建议。</p>
          <a-button type="dashed" block>点击提交</a-button>
        </div>
      </a-card>

      <!-- Settings Section -->
      <a-card class="settings-card" hoverable>
        <template #title>
          <a-icon type="setting" style="color:#faad14" /> 设置
        </template>
        <div class="settings-list">
          <div class="setting-item">
            <span>隐私设置</span>
            <a-icon type="right" />
          </div>
          <div class="setting-item">
            <span>通知设置</span>
            <a-icon type="right" />
          </div>
          <div class="setting-item">
            <span>关于我们</span>
            <a-icon type="right" />
          </div>
        </div>
      </a-card>
    </a-card>

    <div class="mobile-bottom-bar">
      <div :class="['bottom-tab', activeBottom==='home' ? 'active' : '']" @click="handleBottomTab('home')">首页</div>
      <div :class="['bottom-tab', activeBottom==='mine' ? 'active' : '']" @click="handleBottomTab('mine')">我的</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
// Assuming userAPI is correctly imported and available
// import { userAPI } from '@/api';

const router = useRouter();

// Mock userAPI for demonstration purposes if not available
const userAPI = {
  logout: () => new Promise(resolve => setTimeout(resolve, 500)) // Simulate API call
};

function logout() {
  const token = localStorage.getItem('token');
  userAPI.logout({ token }).finally(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    message.success('已退出登录');
    router.push('/auth'); // Redirect to auth page after logout
  });
}

const activeBottom = ref('mine');

function handleBottomTab(tab) {
  activeBottom.value = tab;
  if(tab === 'mine') {
    router.push('/profile'); // Assuming /profile is the route for this component
  } else if(tab === 'home') {
    router.push('/'); // Assuming / is the home route
  }
}
</script>

<style scoped>
.profile-bg {
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 48px;
  padding-bottom: 60px; /* Add padding for the fixed bottom bar */
}
.profile-card {
  width: 340px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(127, 83, 255, 0.08);
  background: #fff;
  padding: 24px 18px 18px 18px;
  margin-bottom: 20px; /* Ensure space above the bottom bar */
}
.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.profile-nickname {
  font-size: 1.1rem;
  font-weight: 600;
  color: #222;
  margin-bottom: 2px;
}
.profile-username {
  font-size: 1rem;
  color: #888;
}
.logout-btn {
  margin-left: 8px;
  font-weight: 600;
  background: #ff4d4f;
  border: none;
  border-radius: 8px; /* Added border-radius for consistency */
}
.edit-btn {
  margin: 18px 0 12px 0;
  font-weight: 500;
  border-radius: 8px;
}
/* Common card styling for consistency */
.course-card, .questions-card, .submit-card, .settings-card {
  border-radius: 12px;
  margin-top: 16px; /* Increased margin for better separation */
  box-shadow: 0 2px 8px rgba(127, 83, 255, 0.04);
}

.course-card {
  background: linear-gradient(90deg, #e0e7ff 0%, #f7f8fa 100%);
}

.questions-card {
  background: linear-gradient(90deg, #e0f7fa 0%, #f7f8fa 100%); /* Light blue gradient for questions */
}

.submit-card {
  background: linear-gradient(90deg, #f0e6ff 0%, #f7f8fa 100%); /* Light purple gradient for submit content */
}

.settings-card {
  background: linear-gradient(90deg, #fffbe0 0%, #f7f8fa 100%); /* Yellowish gradient */
}

.course-list-empty, .questions-list-empty {
  color: #bbb;
  text-align: center;
  padding: 18px 0;
  font-size: 1rem;
}

.submit-content-placeholder {
  text-align: center;
  padding: 18px 0;
}

.submit-content-placeholder p {
  color: #888;
  margin-bottom: 12px;
}

.settings-list {
  padding: 10px 0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  font-size: 1rem;
  color: #333;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item:hover {
  background-color: #f9f9f9;
}

.mobile-bottom-bar {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  height: 48px;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.05); /* Added shadow for better separation */
}
.bottom-tab {
  flex: 1;
  text-align: center;
  font-size: 16px;
  color: #888;
  padding: 8px 0;
  cursor: pointer;
  transition: color 0.2s ease, background 0.2s ease;
}
.bottom-tab.active {
  color: #1677ff;
  font-weight: bold;
  background: #f0f7ff;
  border-radius: 8px 8px 0 0;
}
</style>
