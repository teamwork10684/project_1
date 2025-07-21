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
      <a-card class="course-card" hoverable>
        <template #title>
          <a-icon type="star" style="color:#1677ff" /> 我的课程
        </template>
        <div class="course-list-empty">暂无课程</div>
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
import { userAPI } from '@/api';
const router = useRouter();
function logout() {
  const token = localStorage.getItem('token');
  userAPI.logout({ token }).finally(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    message.success('已退出登录');
    router.push('/auth');
  });
}
const activeBottom = ref('mine');
function handleBottomTab(tab) {
  activeBottom.value = tab;
  if(tab === 'mine') {
    router.push('/profile');
  } else if(tab === 'home') {
    router.push('/');
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
}
.profile-card {
  width: 340px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(127, 83, 255, 0.08);
  background: #fff;
  padding: 24px 18px 18px 18px;
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
}
.edit-btn {
  margin: 18px 0 12px 0;
  font-weight: 500;
  border-radius: 8px;
}
.course-card {
  border-radius: 12px;
  margin-top: 8px;
  background: linear-gradient(90deg, #e0e7ff 0%, #f7f8fa 100%);
  box-shadow: 0 2px 8px rgba(127, 83, 255, 0.04);
}
.course-list-empty {
  color: #bbb;
  text-align: center;
  padding: 18px 0;
  font-size: 1rem;
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
}
.bottom-tab {
  flex: 1;
  text-align: center;
  font-size: 16px;
  color: #888;
  padding: 8px 0;
}
.bottom-tab.active {
  color: #1677ff;
  font-weight: bold;
  background: #f0f7ff;
  border-radius: 8px 8px 0 0;
}
</style> 