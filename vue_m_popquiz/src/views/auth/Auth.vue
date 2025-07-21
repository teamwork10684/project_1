<template>
  <div class="auth-bg">
    <transition name="card-zoom">
      <a-card class="auth-card" bordered :key="mode">
        <div class="auth-logo-bar">
          <span class="logo-gradient">PopQuiz</span>
          <span class="logo-sub">智能演讲互动平台</span>
        </div>
        <div class="auth-top-gradient"></div>
        <div class="auth-divider">
          <span class="auth-divider-line"></span>
          <span class="auth-divider-icon">★</span>
          <span class="auth-divider-line"></span>
        </div>
        <a-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit" layout="vertical">
          <a-form-item label="用户名" name="username" :rules="rules.username">
            <a-input v-model:value="form.username" size="large" placeholder="请输入用户名" allow-clear>
              <template #prefix>
                <icon-user-outlined style="color:#1677ff" />
              </template>
            </a-input>
          </a-form-item>
          <a-form-item label="密码" name="password" :rules="rules.password">
            <a-input-password v-model:value="form.password" size="large" placeholder="请输入密码" allow-clear>
              <template #prefix>
                <icon-lock-outlined style="color:#1677ff" />
              </template>
            </a-input-password>
          </a-form-item>
          <a-form-item v-if="mode === 'register'" label="确认密码" name="confirmPassword" :rules="rules.confirmPassword">
            <a-input-password v-model:value="form.confirmPassword" size="large" placeholder="请再次输入密码" allow-clear>
              <template #prefix>
                <icon-lock-outlined style="color:#1677ff" />
              </template>
            </a-input-password>
          </a-form-item>
          <a-form-item>
            <a-button class="gradient-btn" type="primary" html-type="submit" block size="large" :loading="loading">{{ mode === 'login' ? '登录' : '注册' }}</a-button>
          </a-form-item>
          <a-form-item>
            <a-button type="link" class="switch-btn" block size="large" @click="toggleMode">
              {{ mode === 'login' ? '没有账号？去注册' : '已有账号？去登录' }}
            </a-button>
          </a-form-item>
        </a-form>
        <div class="auth-footer">© 2024 PopQuiz 智能演讲互动平台</div>
      </a-card>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue';
import { UserOutlined as IconUserOutlined, LockOutlined as IconLockOutlined } from '@ant-design/icons-vue';
import { userAPI } from '@/api';

const router = useRouter();
const route = useRoute();
const formRef = ref();
const mode = ref(route.name === 'Register' || route.path === '/register' ? 'register' : 'login');
const loading = ref(false);
const form = ref({ username: '', password: '', confirmPassword: '' });

const validateConfirmPassword = (rule, value) => {
  if (mode.value === 'register') {
    if (!value) {
      return Promise.reject('请再次输入密码');
    }
    if (value !== form.value.password) {
      return Promise.reject('两次输入的密码不一致');
    }
  }
  return Promise.resolve();
};

const rules = ref({
  username: [ { required: true, message: '请输入用户名', trigger: 'blur' } ],
  password: [ { required: true, message: '请输入密码', trigger: 'blur' } ],
  confirmPassword: []
});

// 监听模式变化，更新验证规则
watch(mode, (newMode) => {
  if (newMode === 'register') {
    rules.value.confirmPassword = [
      { validator: validateConfirmPassword, trigger: 'blur' }
    ];
  } else {
    rules.value.confirmPassword = [];
  }
}, { immediate: true });

const handleSubmit = async () => {
  // 手动验证表单数据
  if (!form.value.username.trim()) {
    message.error('请输入用户名');
    return;
  }
  
  if (!form.value.password.trim()) {
    message.error('请输入密码');
    return;
  }
  
  if (mode.value === 'register') {
    if (!form.value.confirmPassword.trim()) {
      message.error('请再次输入密码');
      return;
    }
    if (form.value.password !== form.value.confirmPassword) {
      message.error('两次输入的密码不一致');
      return;
    }
  }
  
  // 验证通过后，根据模式调用相应的处理函数
  if (mode.value === 'login') {
    await handleLogin();
  } else {
    await handleRegister();
  }
};

const handleLogin = async () => {
  loading.value = true;
  try {
    const res = await userAPI.login({
      username: form.value.username,
      password: form.value.password
    });
    const data = res.data;
    // 严格判断token字段
    if (data && data.token) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('username', form.value.username);
      message.success(data.message || '登录成功');
      router.push('/'); // 跳转首页
    } else {
      message.error(data.message || '登录失败');
    }
  } catch (error) {
    // 401等错误时显示后端返回的message
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('网络错误，请稍后重试');
    }
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  loading.value = true;
  try {
    const res = await userAPI.register({
      username: form.value.username,
      password: form.value.password
    });
    const data = res.data;
    if (data.id) {
      message.success('注册成功');
      setTimeout(() => {
        mode.value = 'login';
        router.replace({ name: 'Auth', query: {} });
      }, 1000);
    } else {
      message.error(data.message || '注册失败');
    }
  } catch (error) {
    if (error.response?.data?.message) {
      message.error(error.response.data.message);
    } else {
      message.error('网络错误，请稍后重试');
    }
  } finally {
    loading.value = false;
  }
};

const toggleMode = () => {
  if (mode.value === 'login') {
    mode.value = 'register';
    router.replace({ name: 'Auth', path: '/register' });
  } else {
    mode.value = 'login';
    router.replace({ name: 'Auth', path: '/' });
  }
  form.value = { username: '', password: '', confirmPassword: '' };
  // 清除表单验证状态
  formRef.value?.clearValidate();
};

watch(() => route.path, (newPath) => {
  if (newPath === '/register') mode.value = 'register';
  else mode.value = 'login';
});
</script>

<style scoped>
.auth-bg {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.auth-bg::before, .auth-bg::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  z-index: 0;
}
.auth-bg::before {
  width: 480px;
  height: 480px;
  left: -120px;
  top: -120px;
  background: radial-gradient(circle, #6dd5ed 0%, #2193b0 100%);
  animation: float1 8s ease-in-out infinite alternate;
}
.auth-bg::after {
  width: 360px;
  height: 360px;
  right: -100px;
  bottom: -100px;
  background: radial-gradient(circle, #fcb69f 0%, #ffecd2 100%);
  animation: float2 10s ease-in-out infinite alternate;
}
@keyframes float1 {
  0% { transform: translateY(0) scale(1); }
  100% { transform: translateY(40px) scale(1.1); }
}
@keyframes float2 {
  0% { transform: translateY(0) scale(1); }
  100% { transform: translateY(-30px) scale(1.05); }
}
.auth-card {
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  border-radius: 18px;
  padding: 36px 32px 24px 32px;
  position: relative;
  z-index: 1;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(2px);
  overflow: visible;
}
.auth-logo-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 8px;
  margin-top: -8px;
}
.logo-gradient {
  font-family: 'Segoe UI', 'Arial', sans-serif;
  font-size: 2.4rem;
  font-weight: 900;
  letter-spacing: 2px;
  background: linear-gradient(90deg, #1677ff 10%, #7f53ff 90%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-fill-color: transparent;
  margin-bottom: 2px;
}
.logo-sub {
  font-size: 1.05rem;
  color: #888;
  font-weight: 400;
  margin-bottom: 6px;
  letter-spacing: 1px;
}
.auth-top-gradient {
  height: 4px;
  width: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #1677ff 0%, #7f53ff 100%);
  margin-bottom: 18px;
  margin-top: 2px;
}
.auth-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  gap: 10px;
}
.auth-divider-line {
  flex: 1;
  height: 1.5px;
  background: linear-gradient(90deg, #e0e7ff 0%, #1677ff 50%, #e0e7ff 100%);
  border-radius: 2px;
}
.auth-divider-icon {
  color: #1677ff;
  font-size: 1.2rem;
  font-weight: bold;
  padding: 0 8px;
  letter-spacing: 1px;
}
.gradient-btn {
  background: linear-gradient(90deg, #1677ff 0%, #7f53ff 100%);
  border: none;
  color: #fff;
  font-weight: 600;
  transition: box-shadow 0.2s, transform 0.2s;
  box-shadow: 0 2px 8px rgba(127, 83, 255, 0.08);
}
.gradient-btn:hover, .gradient-btn:focus {
  filter: brightness(1.08);
  box-shadow: 0 4px 16px rgba(127, 83, 255, 0.18);
  transform: scale(1.03);
}
.switch-btn {
  color: #7f53ff !important;
  font-size: 1rem;
  margin-top: -10px;
  margin-bottom: -10px;
  font-weight: 500;
  transition: color 0.2s;
}
.switch-btn:hover {
  color: #1677ff !important;
}
.auth-footer {
  text-align: center;
  color: #bbb;
  font-size: 0.95rem;
  margin-top: 18px;
  letter-spacing: 1px;
  user-select: none;
}
.card-zoom-enter-active, .card-zoom-leave-active {
  transition: transform 0.25s cubic-bezier(.4,2,.6,1), opacity 0.25s;
}
.card-zoom-enter-from, .card-zoom-leave-to {
  transform: scale(0.97);
  opacity: 0.7;
}
.card-zoom-enter-to, .card-zoom-leave-from {
  transform: scale(1);
  opacity: 1;
}
</style>
