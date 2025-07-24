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
              <a-menu-item key="logout" @click="handleLogout">
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
            <a-button type="primary" size="large" block @click="showAddUserModal">
              <i class="anticon anticon-plus"></i>
              新增用户
            </a-button>
          </a-col>
          <a-col :span="12">
            <a-button type="danger" size="large" block @click="handleQuickDeleteRoom">
              <i class="anticon anticon-delete"></i>
              删除演讲室
            </a-button>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 新增用户模态窗 -->
    <a-modal v-model:open="addUserModalVisible" title="新增用户" :confirm-loading="addUserLoading" @ok="handleAddUserOk" @cancel="handleAddUserCancel" destroyOnClose>
      <a-form ref="addUserFormRef" :model="addUserForm" :rules="addUserRules.value" :label-col="{span: 5}" :wrapper-col="{span: 19}">
        <a-form-item label="用户名" name="username">
          <a-input v-model:value="addUserForm.username" autocomplete="off" />
        </a-form-item>
        <a-form-item label="密码" name="password">
          <a-input v-model:value="addUserForm.password" type="password" autocomplete="off" />
        </a-form-item>
        <a-form-item label="确认密码" name="confirmPassword">
          <a-input v-model:value="addUserForm.confirmPassword" type="password" autocomplete="off" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 管理入口Tab区 -->
    <div class="admin-tabs-section">
      <a-tabs v-model="activeTab" class="admin-tabs">
        <a-tab-pane key="users" tab="用户管理">
          <a-card title="用户信息" :bodyStyle="{padding: '0'}" :headStyle="{padding: '0 24px'}">
            <div style="padding: 16px 24px 0 24px; display: flex; align-items: center; gap: 12px;">
              <a-input v-model:value="userSearch" placeholder="搜索用户名" style="width: 200px;" @pressEnter="handleUserSearch" allow-clear />
              <a-button type="primary" @click="handleUserSearch">搜索</a-button>
            </div>
            <a-table
              :columns="userColumns"
              :data-source="userData"
              row-key="id"
              bordered
              :pagination="{ current: userPagination.current, pageSize: userPagination.pageSize, total: userPagination.total, position: ['bottomCenter'] }"
              style="width: 100%"
              @change="handleUserTableChange"
              :locale="{ emptyText: userTableEmptyText }"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'action'">
                  <a-space>
                    <a-button type="link" @click="openUserDetailModal(record)">详情</a-button>
                    <a-button type="link" @click="openEditUserModal(record)">编辑</a-button>
                    <a-button type="link" danger @click="handleDeleteUser(record.id)">删除</a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </a-card>
        </a-tab-pane>
        <a-tab-pane key="speeches" tab="演讲室管理">
          <a-card title="演讲室信息" :bodyStyle="{padding: '0'}" :headStyle="{padding: '0 24px'}">
            <a-table :columns="roomColumns" :data-source="roomData" row-key="id" bordered :pagination="{ current: roomPagination.current, pageSize: roomPagination.pageSize, total: roomPagination.total, position: ['bottomCenter'] }" style="width: 100%" @change="handleRoomTableChange">
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'action'">
                  <a-space>
                    <!-- 删除编辑按钮 -->
                    <a-button type="link" danger @click="handleRoomDelete(record)">删除</a-button>
                    <a-button type="link" @click="handleRoomViewMembers(record)">查看成员</a-button>
                    <a-button type="link" danger @click="handleRoomForceClose(record)">强制关闭</a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </a-card>
        </a-tab-pane>
      </a-tabs>
    </div>
    <!-- 用户新增/编辑弹窗 -->
    <a-modal v-model:open="userModalVisible" :title="userModalType === 'add' ? '新增用户' : '编辑用户'" :confirm-loading="userModalLoading" @ok="handleUserModalOk" @cancel="handleUserModalCancel" destroyOnClose>
      <a-form ref="userFormRef" :model="userForm" :rules="userEditRules.value" :label-col="{span: 5}" :wrapper-col="{span: 19}">
        <a-form-item label="用户名" name="username">
          <a-input v-model:value="userForm.username" autocomplete="off" />
        </a-form-item>
        <a-form-item label="密码" name="password">
          <a-input v-model:value="userForm.password" type="password" autocomplete="off" placeholder="请输入新密码" />
        </a-form-item>
        <a-form-item label="确认密码" name="confirmPassword">
          <a-input v-model:value="userForm.confirmPassword" type="password" autocomplete="off" placeholder="请再次输入新密码" />
        </a-form-item>
      </a-form>
    </a-modal>
    <!-- 用户详情弹窗 -->
    <a-modal v-model:open="userDetailModalVisible" title="用户详情" :footer="null" width="800px" @cancel="handleUserDetailCancel">
      <template v-if="userDetailLoading">
        <a-spin />
      </template>
      <template v-else>
        <div style="margin-bottom: 12px; font-weight: bold;">用户名：{{ userDetail.username }}</div>
        <div style="margin-bottom: 8px; font-weight: bold;">参与的所有演讲室：</div>
        <a-table :columns="[{title:'ID',dataIndex:'id'},{title:'名称',dataIndex:'name'},{title:'描述',dataIndex:'description'}]" :data-source="userDetail.speechRooms" row-key="id" size="small" :pagination="false" />
        <div style="margin: 12px 0 8px 0; font-weight: bold;">所有被邀请记录：</div>
        <a-table :columns="invitationColumns" :data-source="userDetail.invitations" row-key="id" size="small" :pagination="false" />
        <div style="margin: 12px 0 8px 0; font-weight: bold;">创建的所有演讲室：</div>
        <a-table :columns="[{title:'ID',dataIndex:'id'},{title:'名称',dataIndex:'name'},{title:'描述',dataIndex:'description'}]" :data-source="userDetail.createdRooms" row-key="id" size="small" :pagination="false" />
      </template>
    </a-modal>
    <!-- 演讲室成员弹窗 -->
    <a-modal v-model:open="roomMemberModalVisible" title="演讲室成员" :footer="null" width="600px" @cancel="handleRoomMemberCancel">
      <div style="margin-bottom: 16px; display: flex; justify-content: center; align-items: center; gap: 16px;">
        <a-radio-group v-model:value="roomMemberSortKey" @change="sortRoomMembers" button-style="solid">
          <a-radio-button value="role">按角色排序</a-radio-button>
          <a-radio-button value="joined_at">按加入时间排序</a-radio-button>
        </a-radio-group>
        <a-tooltip :title="roomMemberSortOrder === 'asc' ? '升序' : '降序'">
          <a-button
            size="small"
            type="primary"
            shape="circle"
            @click="roomMemberSortOrder = roomMemberSortOrder === 'asc' ? 'desc' : 'asc'; sortRoomMembers()"
            style="margin-left: 8px; display: flex; align-items: center; justify-content: center;"
          >
            <template #icon>
              <i :class="roomMemberSortOrder === 'asc' ? 'anticon anticon-arrow-up' : 'anticon anticon-arrow-down'" />
            </template>
          </a-button>
        </a-tooltip>
      </div>
      <a-table
        :columns="roomMemberColumns"
        :data-source="roomMemberData"
        row-key="user_id"
        size="small"
        :pagination="{ current: roomMemberPagination.current, pageSize: roomMemberPagination.pageSize, showSizeChanger: false }"
        @change="(pagination) => { roomMemberPagination.value.current = pagination.current }"
        bordered
      />
    </a-modal>
    </div> <!-- admin-main-wrapper -->
  </div>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import api, { userAPI, adminAPI } from '@/api'
import { message, Modal, Form, Input } from 'ant-design-vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const activeTab = ref('users')

// 统计数据
const stats = ref({
  users: 0,
  speeches: 0,
  active: 0,
  ended: 0
})

const fetchAdminStats = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await adminAPI.getStats(token)
    stats.value = {
      users: res.data.user_count,
      speeches: res.data.room_count,
      active: res.data.active_room_count,
      ended: res.data.ended_room_count
    }
  } catch (e) {
    message.error('获取统计数据失败')
  }
}
onMounted(fetchAdminStats)

// 在用户表格数据处理处添加格式化函数
function formatDateTime(str) {
  if (!str) return '';
  return str.replace('T', ' ');
}

// 用户管理搜索与分页参数
const userSearch = ref('')
const userPagination = ref({ current: 1, pageSize: 5, total: 0 })
const userSorter = ref({ field: 'created_at', order: 'descend' })

// 用户信息表头
const userColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', sorter: true },
  { title: '用户名', dataIndex: 'username', key: 'username', sorter: true },
  { title: '注册时间', dataIndex: 'created_at', key: 'created_at', sorter: true,
    customRender: ({ text }) => formatDateTime(text) },
  { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', sorter: true,
    customRender: ({ text }) => formatDateTime(text) },
  { title: '操作', key: 'action' }
]

const userData = ref([])

// 用户表格空状态自定义
const userTableEmptyText = ref('暂无数据')

// 获取用户列表，支持搜索、分页、排序
const fetchUsers = async () => {
  try {
    const token = localStorage.getItem('token')
    const params = {
      page: userPagination.value.current,
      per_page: userPagination.value.pageSize,
      sort_by: userSorter.value.field,
      order: userSorter.value.order === 'ascend' ? 'asc' : 'desc',
      username: userSearch.value.trim() ? userSearch.value.trim() : undefined
    }
    const res = await adminAPI.getUsers(token, params)
    userData.value = res.data.users
    if (res.data.pagination) {
      userPagination.value.total = res.data.pagination.total
    }
    // 搜索有内容时且无结果，显示“查询不到该用户”
    if (userSearch.value.trim() && userData.value.length === 0) {
      userTableEmptyText.value = '查询不到该用户'
    } else {
      userTableEmptyText.value = '暂无数据'
    }
  } catch (e) {
    message.error('获取用户列表失败')
    userData.value = []
    userTableEmptyText.value = '查询不到该用户'
  }
}

onMounted(fetchUsers)

// 搜索事件
const handleUserSearch = () => {
  userPagination.value.current = 1
  fetchUsers()
}

// 表格分页、排序事件
const handleUserTableChange = (pagination, filters, sorter) => {
  userPagination.value.current = pagination.current
  userPagination.value.pageSize = pagination.pageSize
  if (sorter && sorter.field) {
    userSorter.value.field = sorter.field
    userSorter.value.order = sorter.order
  }
  fetchUsers()
}

const handleDeleteUser = (id) => {
  Modal.confirm({
    title: '确认删除该用户？',
    content: '删除后不可恢复，确定要删除吗？',
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        const token = localStorage.getItem('token')
        await adminAPI.deleteUser(id, token)
        message.success('删除成功')
        fetchUsers()
        fetchAdminStats() // 新增：自动更新统计卡片
      } catch (e) {
        message.error(e?.response?.data?.message || '删除失败')
      }
    }
  })
}

// 新增/编辑用户弹窗相关
const userModalVisible = ref(false)
const userModalType = ref('add') // 'add' or 'edit'
const userModalLoading = ref(false)
const userForm = ref({ id: null, username: '', password: '', confirmPassword: '' })
const userFormRef = ref()

// 编辑用户校验规则，和注册/新增一致
const userEditRules = ref({
  username: [ { required: true, message: '请输入用户名', trigger: 'blur' } ],
  password: [ { required: true, message: '请输入新密码', trigger: 'blur' } ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: (rule, value) => {
        if (!value) {
          return Promise.reject('请再次输入新密码');
        }
        if (value !== userForm.value.password) {
          return Promise.reject('两次输入的密码不一致');
        }
        return Promise.resolve();
      }, trigger: 'blur' }
  ]
})

const openEditUserModal = (record) => {
  userModalType.value = 'edit'
  userForm.value = { id: record.id, username: record.username, password: '', confirmPassword: '' }
  userModalVisible.value = true
  userFormRef.value?.clearValidate?.();
}

const handleUserModalOk = async () => {
  try {
    await userFormRef.value.validate();
  } catch (e) {
    return;
  }
  if (!userForm.value.username.trim()) {
    message.error('请输入用户名');
    return;
  }
  if (!userForm.value.password.trim()) {
    message.error('请输入新密码');
    return;
  }
  if (!userForm.value.confirmPassword.trim()) {
    message.error('请再次输入新密码');
    return;
  }
  if (userForm.value.password !== userForm.value.confirmPassword) {
    message.error('两次输入的密码不一致');
    return;
  }
  userModalLoading.value = true
  try {
    const token = localStorage.getItem('token');
    await userAPI.editUser(userForm.value.id, { username: userForm.value.username, password: userForm.value.password }, token)
    message.success('编辑成功')
    userModalVisible.value = false
    fetchUsers()
  } catch (e) {
    message.error(e?.response?.data?.message || '编辑失败')
  } finally {
    userModalLoading.value = false
  }
}
const handleUserModalCancel = () => {
  userModalVisible.value = false
}

// 密码确认校验器（Promise风格，兼容Ant Design Vue 3.x）
const confirmPasswordValidator = (rule, value) => {
  return new Promise((resolve, reject) => {
    if (value === userForm.value.password) {
      resolve();
    } else {
      reject('两次输入的密码不一致');
    }
  });
};

// 新增用户弹窗相关（重命名变量和方法，避免与编辑用户冲突）
const addUserModalVisible = ref(false)
const addUserLoading = ref(false)
const addUserForm = ref({ username: '', password: '', confirmPassword: '' })
const addUserFormRef = ref()

// 校验规则
const addUserRules = ref({
  username: [ { required: true, message: '请输入用户名', trigger: 'blur' } ],
  password: [ { required: true, message: '请输入密码', trigger: 'blur' } ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: (rule, value) => {
        if (!value) {
          return Promise.reject('请再次输入密码');
        }
        if (value !== addUserForm.value.password) {
          return Promise.reject('两次输入的密码不一致');
        }
        return Promise.resolve();
      }, trigger: 'blur' }
  ]
})

const showAddUserModal = () => {
  addUserForm.value = { username: '', password: '', confirmPassword: '' }
  addUserModalVisible.value = true
  addUserFormRef.value?.clearValidate?.();
}

const handleAddUserOk = async () => {
  // 手动校验表单
  try {
    await addUserFormRef.value.validate();
  } catch (e) {
    return;
  }
  if (!addUserForm.value.username.trim()) {
    message.error('请输入用户名');
    return;
  }
  if (!addUserForm.value.password.trim()) {
    message.error('请输入密码');
    return;
  }
  if (!addUserForm.value.confirmPassword.trim()) {
    message.error('请再次输入密码');
    return;
  }
  if (addUserForm.value.password !== addUserForm.value.confirmPassword) {
    message.error('两次输入的密码不一致');
    return;
  }
  addUserLoading.value = true;
  try {
    const token = localStorage.getItem('token');
    const res = await userAPI.addUser({ username: addUserForm.value.username, password: addUserForm.value.password }, token);
    if (res.data && res.data.id) {
      message.success('新增成功');
      addUserModalVisible.value = false;
      fetchUsers();
      fetchAdminStats(); // 新增：自动更新统计卡片
    } else {
      message.error(res.data?.message || '新增失败');
    }
  } catch (e) {
    message.error(e?.response?.data?.message || '新增失败');
  } finally {
    addUserLoading.value = false;
  }
}

const handleAddUserCancel = () => {
  addUserModalVisible.value = false
}

const handleLogout = () => {
  localStorage.clear();
  router.push('/');
}

// 演讲室信息表头
const roomStatusFilter = ref(null)

const roomColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', sorter: true },
  { title: '演讲室名称', dataIndex: 'name', key: 'name' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '创建者', dataIndex: 'creator_name', key: 'creator_name' },
  { title: '状态', dataIndex: 'status', key: 'status',
    customRender: ({ text }) => {
      if (text === 0) return '等待开始';
      if (text === 1) return '进行中';
      if (text === 2) return '已结束';
      return text;
    },
    filters: [
      { text: '全部', value: null },
      { text: '等待开始', value: 0 },
      { text: '进行中', value: 1 },
      { text: '已结束', value: 2 }
    ],
    filterMultiple: false
  },
  { title: '人数', dataIndex: 'total_participants', key: 'total_participants', sorter: true },
  { title: '操作', key: 'action' }
]

// 新增排序状态
const roomSorter = ref({ field: 'id', order: 'descend' })

const roomData = ref([])
// 新增分页状态
const roomPagination = ref({ current: 1, pageSize: 5, total: 0 })

// 修改fetchRooms，支持状态筛选
const fetchRooms = async () => {
  try {
    const token = localStorage.getItem('token')
    const params = {
      page: roomPagination.value.current,
      per_page: roomPagination.value.pageSize,
      sort_by: roomSorter.value.field,
      order: roomSorter.value.order === 'ascend' ? 'asc' : 'desc',
      status: roomStatusFilter.value !== null ? roomStatusFilter.value : undefined
    }
    const res = await adminAPI.getRooms(token, params)
    roomData.value = res.data.rooms
    if (res.data.pagination) {
      roomPagination.value.total = res.data.pagination.total
    }
  } catch (e) {
    message.error('获取演讲室列表失败')
  }
}
onMounted(fetchRooms)

// 分页、排序、筛选切换事件
const handleRoomTableChange = (pagination, filters, sorter) => {
  roomPagination.value.current = pagination.current
  roomPagination.value.pageSize = pagination.pageSize
  if (sorter && sorter.field) {
    roomSorter.value.field = sorter.field
    roomSorter.value.order = sorter.order
  }
  // 状态筛选
  if (filters && filters.status !== undefined) {
    if (filters.status && filters.status.length > 0) {
      roomStatusFilter.value = filters.status[0] !== null ? filters.status[0] : null
    } else {
      roomStatusFilter.value = null
    }
  }
  fetchRooms()
}

const handleRoomDelete = (room) => {
  Modal.confirm({
    title: `确认删除演讲室「${room.name}」？`,
    content: '删除后不可恢复，确定要删除吗？',
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        const token = localStorage.getItem('token')
        await api.delete(`/admin/speech-rooms/${room.id}`, { data: { token } })
        message.success('删除成功')
        fetchRooms()
        fetchAdminStats() // 新增：删除后立即刷新统计卡片
      } catch (e) {
        message.error(e?.response?.data?.message || '删除失败')
      }
    }
  })
}

// 1. 演讲室成员表格列定义
const roomMemberColumns = [
  { title: '用户ID', dataIndex: 'user_id', key: 'user_id' },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '角色', dataIndex: 'role', key: 'role',
    customRender: ({ text }) => {
      if (text === 0) return '创建者'
      if (text === 1) return '演讲者'
      if (text === 2) return '听众'
      return text
    }
  },
  { title: '加入时间', dataIndex: 'joined_at', key: 'joined_at' }
]
const roomMemberModalVisible = ref(false)
const roomMemberData = ref([])
const roomMemberPagination = ref({ current: 1, pageSize: 10 })
// 新增排序相关变量
const roomMemberSortKey = ref('role') // 'role' 或 'joined_at'
const roomMemberSortOrder = ref('asc') // 'asc' 或 'desc'

// 排序函数
const sortRoomMembers = () => {
  let data = roomMemberData.value.slice()
  if (roomMemberSortKey.value === 'role') {
    data.sort((a, b) => {
      if (a.role !== b.role) return (roomMemberSortOrder.value === 'asc' ? a.role - b.role : b.role - a.role)
      if (a.role === 2 && b.role === 2) return (roomMemberSortOrder.value === 'asc' ? a.user_id - b.user_id : b.user_id - a.user_id)
      return 0
    })
  } else if (roomMemberSortKey.value === 'joined_at') {
    data.sort((a, b) => {
      const t1 = new Date(a.joined_at).getTime()
      const t2 = new Date(b.joined_at).getTime()
      return roomMemberSortOrder.value === 'asc' ? t1 - t2 : t2 - t1
    })
  }
  roomMemberData.value = data
}

// 2. 修改handleRoomViewMembers方法，弹窗表格展示成员信息
const handleRoomViewMembers = async (room) => {
  try {
    const token = localStorage.getItem('token')
    const res = await adminAPI.getRoomMembers(room.id, token)
    // 默认排序：创建者 > 演讲者 > 听众（用户id升序）
    roomMemberData.value = (res.data.members || []).slice().sort((a, b) => {
      if (a.role !== b.role) return a.role - b.role
      if (a.role === 2 && b.role === 2) return a.user_id - b.user_id
      return 0
    })
    roomMemberModalVisible.value = true
    roomMemberSortKey.value = 'role'
    roomMemberSortOrder.value = 'asc'
  } catch (e) {
    message.error('获取成员失败')
  }
}
const handleRoomMemberCancel = () => {
  roomMemberModalVisible.value = false
}
const handleRoomForceClose = (room) => {
  Modal.confirm({
    title: `强制关闭演讲室「${room.name}」？`,
    content: '此操作将强制结束演讲室，确定要继续吗？',
    okText: '强制关闭',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        const token = localStorage.getItem('token')
        await api.post(`/admin/speech-rooms/${room.id}/force-close`, { token })
        message.success('演讲室已强制关闭')
        fetchRooms()
        fetchAdminStats() // 新增：强制关闭后立即刷新统计卡片
      } catch (e) {
        message.error(e?.response?.data?.message || '强制关闭失败')
      }
    }
  })
}
const handleQuickDeleteRoom = () => {
  Modal.confirm({
    title: '删除演讲室',
    content: '请在表格中选择要删除的演讲室',
    okText: '知道了',
    cancelButtonProps: { style: { display: 'none' } },
    onOk: () => {}
  })
}

// 1. 新增用户详情弹窗相关变量
const userDetailModalVisible = ref(false)
const userDetailLoading = ref(false)
const userDetail = ref({
  username: '',
  speechRooms: [],
  invitations: [],
  createdRooms: []
})

// 新增：被邀请记录表格列定义，带映射
const invitationColumns = [
  { title: '房间名', dataIndex: 'room_name', key: 'room_name' },
  { title: '角色', dataIndex: 'role', key: 'role',
    customRender: ({ text }) => {
      if (text === 0) return '听众';
      if (text === 1) return '演讲者';
      return text;
    }
  },
  { title: '状态', dataIndex: 'status', key: 'status',
    customRender: ({ text }) => {
      if (text === 0) return '待接受';
      if (text === 1) return '已接受';
      if (text === 2) return '已拒绝';
      if (text === 3) return '已失效';
      return text;
    }
  }
]

// 2. 新增API调用（通过user_id调用管理后台接口）
const fetchUserDetails = async (user) => {
  userDetailLoading.value = true
  userDetail.value.username = user.username
  try {
    const token = localStorage.getItem('token')
    // 参与的所有演讲室
    const speechRoomsRes = await api.get(`/admin/user/${user.id}/speech-rooms?token=${token}`)
    // 所有被邀请记录
    const invitationsRes = await api.get(`/admin/user/${user.id}/invitations?token=${token}`)
    // 创建的所有演讲室
    const createdRoomsRes = await api.get(`/admin/user/${user.id}/created-rooms?token=${token}`)
    userDetail.value.speechRooms = speechRoomsRes.data.rooms || []
    userDetail.value.invitations = invitationsRes.data.invitations || []
    userDetail.value.createdRooms = createdRoomsRes.data.rooms || []
  } catch (e) {
    message.error('获取用户详情失败')
    userDetail.value.speechRooms = []
    userDetail.value.invitations = []
    userDetail.value.createdRooms = []
  } finally {
    userDetailLoading.value = false
  }
}

const openUserDetailModal = (user) => {
  userDetailModalVisible.value = true
  fetchUserDetails(user)
}
const handleUserDetailCancel = () => {
  userDetailModalVisible.value = false
}
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