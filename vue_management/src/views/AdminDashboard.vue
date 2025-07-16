<template>
  <div class="admin-home-container">
    <div class="admin-main-wrapper">
    <!-- 顶部导航栏 -->
    <div class="admin-header">
      <div class="admin-header-left">
        <span class="admin-logo">PopQuiz</span>
        <span class="admin-subtitle">后台管理系统</span>
      </div>
      <div class="admin-header-right">
        <a-dropdown>
          <a-button class="user-btn">
            <template #icon>
              <i class="anticon anticon-user"></i>
            </template>
            管理员
            <i class="anticon anticon-down"></i>
          </a-button>
          <template #overlay>
            <a-menu>
              <a-menu-item key="switch">
                <i class="anticon anticon-user-switch"></i>
                切换用户
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout">
                <i class="anticon anticon-logout"></i>
                退出登录
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>

    <!-- 统计卡片区 -->
    <div class="stats-section">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic title="用户总数" :value="stats.users" :value-style="{ color: '#1677ff' }">
              <template #prefix>
                <i class="anticon anticon-user"></i>
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic title="演讲总数" :value="stats.speeches" :value-style="{ color: '#52c41a' }">
              <template #prefix>
                <i class="anticon anticon-audio"></i>
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic title="活跃演讲" :value="stats.active" :value-style="{ color: '#fa8c16' }">
              <template #prefix>
                <i class="anticon anticon-play-circle"></i>
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic title="已结束演讲" :value="stats.ended" :value-style="{ color: '#722ed1' }">
              <template #prefix>
                <i class="anticon anticon-check-circle"></i>
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 快捷操作区 -->
    <div class="quick-actions">
      <a-card title="快捷操作" class="action-card">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-button type="primary" size="large" block>
              <i class="anticon anticon-plus"></i>
              新增用户
            </a-button>
          </a-col>
          <a-col :span="12">
            <a-button type="danger" size="large" block>
              <i class="anticon anticon-delete"></i>
              删除演讲室
            </a-button>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 管理入口Tab区 -->
    <div class="admin-tabs-section">
      <a-tabs v-model="activeTab" class="admin-tabs">
        <a-tab-pane key="users" tab="用户管理">
          <a-card title="用户信息" :bodyStyle="{padding: '0'}" :headStyle="{padding: '0 24px'}">
            <a-table :columns="userColumns" :data-source="userData" row-key="id" bordered :pagination="{ position: ['bottomCenter'] }" style="width: 100%">
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'action'">
                  <a-space>
                    <a-button type="link">编辑</a-button>
                    <a-button type="link" danger @click="handleDeleteUser(record.id)">删除</a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </a-card>
        </a-tab-pane>
        <a-tab-pane key="speeches" tab="演讲室管理">
          <a-card title="演讲室信息" :bodyStyle="{padding: '0'}" :headStyle="{padding: '0 24px'}">
            <a-table :columns="roomColumns" :data-source="roomData" row-key="id" bordered :pagination="{ position: ['bottomCenter'] }" style="width: 100%">
              <template #bodyCell="{ column }">
                <template v-if="column.key === 'action'">
                  <a-space>
                    <a-button type="link">编辑</a-button>
                    <a-button type="link" danger>删除</a-button>
                    <a-button type="link">查看成员</a-button>
                    <a-button type="link" danger>强制关闭</a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </a-card>
        </a-tab-pane>
      </a-tabs>
    </div>
    </div> <!-- admin-main-wrapper -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { message, Modal } from 'ant-design-vue'

const activeTab = ref('users')

// 统计数据
const stats = ref({
  users: 128,
  speeches: 56,
  active: 8,
  ended: 48
})

// 用户信息表头
const userColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '注册时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at' },
  { title: '操作', key: 'action' }
]
const userData = ref([])
const fetchUsers = async () => {
  try {
    const res = await api.get('/users')
    userData.value = res.data.users
  } catch (e) {
    message.error('获取用户列表失败')
  }
}
onMounted(fetchUsers)

const handleDeleteUser = (id) => {
  Modal.confirm({
    title: '确认删除该用户？',
    content: '删除后不可恢复，确定要删除吗？',
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await api.delete(`/users/${id}`)
        message.success('删除成功')
        fetchUsers()
      } catch (e) {
        message.error(e?.response?.data?.message || '删除失败')
      }
    }
  })
}

// 演讲室信息表头
const roomColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '演讲室名称', dataIndex: 'name', key: 'name' },
  { title: '创建者', dataIndex: 'creator', key: 'creator' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '人数', dataIndex: 'members', key: 'members' },
  { title: '操作', key: 'action' }
]
const roomData = [
  { id: 201, name: 'AI前沿', creator: 'admin', status: '进行中', members: 12 },
  { id: 202, name: 'Vue3实战', creator: 'user1', status: '已结束', members: 8 }
]
</script>

<style scoped>
.admin-home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 0;
  overflow: auto;
}
.admin-main-wrapper {
  width: 100%;
  margin: 0;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 40px;
  box-sizing: border-box;
}
.admin-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 32px 4vw;
  margin-bottom: 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-sizing: border-box;
}
.admin-header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}
.admin-logo {
  font-size: 2.3rem;
  font-weight: 700;
  color: #1677ff;
  margin: 0;
}
.admin-subtitle {
  color: #666;
  font-size: 1.2rem;
}
.admin-header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}
.user-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.2rem;
}
.stats-section {
  width: 100%;
  margin-bottom: 0;
}
.stat-card {
  border-radius: 18px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 1.25rem;
  min-width: 220px;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(22, 119, 255, 0.10);
  border-color: #1677ff;
}
.quick-actions {
  width: 100%;
  margin-bottom: 0;
}
.action-card {
  border-radius: 18px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.3);
  width: 100%;
}
.action-card .ant-btn {
  font-size: 1.25rem;
  height: 60px;
  border-radius: 10px;
  background: #fff;
  color: #1677ff;
  border: 1.5px solid #e6eaf1;
  transition: background 0.2s, color 0.2s;
}
.action-card .ant-btn:hover {
  background: #e6f0ff;
  color: #1677ff;
}
.admin-tabs-section {
  width: 100%;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 48px 3vw 40px 3vw;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-sizing: border-box;
  min-height: 58vh;
}
.admin-tabs {
  background: transparent;
}
.admin-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 40px;
}
.admin-tabs :deep(.ant-tabs-tab) {
  font-size: 1.25rem;
  font-weight: 600;
  border-radius: 10px 10px 0 0;
  padding: 12px 36px;
}
.admin-tabs :deep(.ant-tabs-tab-active) {
  color: #1677ff !important;
  font-weight: 700;
}
.admin-tabs :deep(.ant-card) {
  border-radius: 18px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1.5px solid #e6eaf1;
}
.admin-tabs :deep(.ant-card-head-title) {
  font-size: 1.25rem;
  font-weight: 700;
}
.admin-tabs :deep(.ant-table) {
  font-size: 1.18rem;
  border-radius: 12px;
}
.admin-tabs :deep(.ant-table-thead > tr > th) {
  font-size: 1.18rem;
  background: #f5f7fa;
}
.admin-tabs :deep(.ant-table-tbody > tr > td) {
  font-size: 1.18rem;
}
/* 侧边栏样式优化（如有侧边栏） */
.admin-sider {
  width: 120px !important;
  min-width: 120px !important;
  max-width: 200px !important;
}
@media (max-width: 1200px) {
  .admin-main-wrapper {
    padding: 0 1vw;
    gap: 24px;
  }
  .admin-header {
    padding: 16px 2vw;
  }
  .admin-tabs-section {
    padding: 24px 1vw 16px 1vw;
  }
}
@media (max-width: 900px) {
  .admin-main-wrapper {
    padding: 0 0.5vw;
    gap: 12px;
  }
  .admin-header {
    flex-direction: column;
    gap: 10px;
    padding: 10px 2vw;
  }
  .admin-tabs-section {
    padding: 10px 1vw 8px 1vw;
  }
}
</style>