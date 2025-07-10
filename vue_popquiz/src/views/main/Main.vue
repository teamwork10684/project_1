<template>
  <div class="main-layout">
    <a-layout style="min-height: 100vh">
      <!-- 顶部栏 -->
      <a-layout-header class="main-header">
        <a-button type="text" class="header-collapse-btn" @click="toggleCollapse">
          <svg v-if="!collapsed" viewBox="0 0 1024 1024" width="22" height="22">
            <rect x="160" y="256" width="704" height="80" rx="20" fill="#1677ff"/>
            <rect x="160" y="472" width="704" height="80" rx="20" fill="#1677ff"/>
            <rect x="160" y="688" width="704" height="80" rx="20" fill="#1677ff"/>
          </svg>
          <svg v-else viewBox="0 0 1024 1024" width="22" height="22">
            <rect x="160" y="472" width="704" height="80" rx="20" fill="#1677ff"/>
          </svg>
        </a-button>
        <div class="header-title">PopQuiz</div>
      </a-layout-header>
      <a-layout>
        <!-- 侧边栏 -->
        <a-layout-sider v-if="!collapsed" width="200" class="main-sider">
          <a-menu theme="light" mode="inline" :selectedKeys="[selectedKey]" @click="onMenuClick">
            <a-menu-item key="home">
              <span>主页</span>
            </a-menu-item>
            <a-menu-item key="demo">
              <span>Demo 演示</span>
            </a-menu-item>
          </a-menu>
        </a-layout-sider>
        <a-layout>
          <a-layout-content class="main-content">
            <router-view />
          </a-layout-content>
        </a-layout>
      </a-layout>
    </a-layout>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const collapsed = ref(false);
const router = useRouter();
const route = useRoute();

const selectedKey = computed(() => {
  if (route.path === '/main/demo') return 'demo';
  return 'home';
});

const onMenuClick = ({ key }) => {
  if (key === 'home') {
    router.push('/main');
  } else if (key === 'demo') {
    router.push('/main/demo');
  }
};

const toggleCollapse = () => {
  collapsed.value = !collapsed.value;
};
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}
.main-header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 56px;
  background: #fff;
  box-shadow: 0 2px 8px #f0f1f2;
  position: relative;
  z-index: 10;
  padding: 0;
}
.header-collapse-btn {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  color: #1677ff;
  border: none;
  background: none;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: none;
}
.header-title {
  font-size: 1.6rem;
  font-weight: bold;
  color: #1677ff;
  text-align: center;
  width: 100%;
  letter-spacing: 2px;
}
.main-sider {
  background: #fff;
  box-shadow: 2px 0 8px #f0f1f2;
  transition: width 0.2s;
  min-height: calc(100vh - 56px);
}
.main-content {
  margin: 24px 16px;
  padding: 24px;
  background: #fff;
  min-height: 280px;
  border-radius: 8px;
  box-shadow: 0 2px 8px #f0f1f2;
}
</style>
