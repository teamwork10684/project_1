<template>
  <view class="login-bg">
    <view class="login-card">
      <view class="login-logo">
        <image src="/static/logo.png" mode="aspectFit" class="logo-img" />
      </view>
      <view class="login-title">PopQuiz 登录</view>
      <a-form :model="form" class="login-form" @submit="handleLogin">
        <a-form-item>
          <a-input v-model:value="form.username" placeholder="用户名" size="large" prefix-icon="user" allow-clear />
        </a-form-item>
        <a-form-item>
          <a-input v-model:value="form.password" type="password" placeholder="密码" size="large" prefix-icon="lock" allow-clear />
        </a-form-item>
        <a-form-item>
          <a-select v-model:value="form.role" placeholder="请选择身份" size="large">
            <a-select-option value="student">学生</a-select-option>
            <a-select-option value="teacher">老师</a-select-option>
            <a-select-option value="organizer">组织人</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block size="large">登录</a-button>
        </a-form-item>
        <a-form-item>
          <a-button type="link" block size="large" @click="goRegister">没有账号？去注册</a-button>
        </a-form-item>
      </a-form>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
const form = ref({ username: '', password: '', role: '' });

const handleLogin = (e) => {
  e.preventDefault && e.preventDefault();
  if (!form.value.username || !form.value.password || !form.value.role) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' });
    return;
  }
  uni.request({
    url: 'http://localhost/popquiz/login',
    method: 'POST',
    data: {
      username: form.value.username,
      password: form.value.password
    },
    success: (res) => {
      if (res.data && res.data.token) {
        uni.setStorageSync('token', res.data.token);
        uni.setStorageSync('role', res.data.role);
        uni.showToast({ title: '登录成功', icon: 'success' });
        uni.reLaunch({ url: '/pages/index/index' });
      } else {
        uni.showToast({ title: res.data.message || '登录失败', icon: 'none' });
      }
    },
    fail: () => {
      uni.showToast({ title: '网络错误', icon: 'none' });
    }
  });
};

const goRegister = () => {
  uni.navigateTo({ url: '/pages/login/register' });
};
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0e7ff 0%, #f0fdfa 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-card {
  width: 90vw;
  max-width: 420px;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.08);
  padding: 60rpx 40rpx 40rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.login-logo {
  margin-bottom: 32rpx;
}
.logo-img {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: #f0f0f0;
}
.login-title {
  font-size: 44rpx;
  font-weight: 600;
  color: #222;
  margin-bottom: 48rpx;
  text-align: center;
}
.login-form {
  width: 100%;
}
</style>
