<template>
  <div class="admin-dashboard">
    <a-layout style="min-height: 100vh">
      <!-- 顶部栏 -->
      <a-layout-header class="main-header">
        <div class="header-title">后台管理面板</div>
      </a-layout-header>
      <a-layout>
        <!-- 侧边栏 -->
        <a-layout-sider width="200" class="main-sider">
          <a-menu theme="light" mode="inline" :selectedKeys="[selectedKey]" @click="onMenuClick">
            <a-menu-item key="users">
              <span>用户信息</span>
            </a-menu-item>
            <a-menu-item key="speeches">
              <span>演讲信息</span>
            </a-menu-item>
          </a-menu>
        </a-layout-sider>
        <a-layout>
          <a-layout-content class="main-content">
            <div v-if="selectedKey === 'users'">
              <a-card title="用户信息">
                <a-table :columns="userColumns" :data-source="userData" row-key="id" bordered />
              </a-card>
            </div>
            <div v-else-if="selectedKey === 'speeches'">
              <a-card title="演讲信息">
                <a-table :columns="speechColumns" :data-source="speechData" row-key="id" bordered />
              </a-card>
            </div>
          </a-layout-content>
        </a-layout>
      </a-layout>
    </a-layout>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const selectedKey = ref('users')
const onMenuClick = ({ key }) => {
  selectedKey.value = key
}

// 用户信息表头
const userColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '角色', dataIndex: 'role', key: 'role' }
]
// 用户信息示例数据
const userData = [
  { id: 1, username: 'admin', email: 'admin@example.com', role: '管理员' },
  { id: 2, username: 'user1', email: 'user1@example.com', role: '普通用户' }
]

// 演讲信息表头
const speechColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '演讲主题', dataIndex: 'topic', key: 'topic' },
  { title: '创建者', dataIndex: 'creator', key: 'creator' },
  { title: '状态', dataIndex: 'status', key: 'status' }
]
// 演讲信息示例数据
const speechData = [
  { id: 101, topic: 'AI与未来', creator: 'admin', status: '进行中' },
  { id: 102, topic: 'Vue3实战', creator: 'user1', status: '已结束' }
]
</script>

<style scoped>
.admin-dashboard {
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
  padding: 0;
  background: #fff;
  min-height: 280px;
  border-radius: 8px;
  box-shadow: 0 2px 8px #f0f1f2;
}
</style> 