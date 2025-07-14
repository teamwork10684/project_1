<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="header-left">
        <h1 class="logo">PopQuiz</h1>
        <span class="subtitle">智能演讲互动平台</span>
      </div>
      <div class="header-right">
        <a-dropdown>
          <a-button class="user-btn">
            <template #icon>
              <UserOutlined />
            </template>
            {{ userInfo.username }}
            <DownOutlined />
          </a-button>
          <template #overlay>
            <a-menu>
              <a-menu-item key="profile">
                <UserOutlined />
                个人资料
              </a-menu-item>
              <a-menu-item key="settings">
                <SettingOutlined />
                设置
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout" @click="handleLogout">
                <LogoutOutlined />
                退出登录
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="我创建的演讲"
              :value="stats.created"
              :value-style="{ color: '#1677ff' }"
            >
              <template #prefix>
                <FileTextOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="我参与的演讲"
              :value="stats.participated"
              :value-style="{ color: '#52c41a' }"
            >
              <template #prefix>
                <TeamOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="进行中的演讲"
              :value="stats.active"
              :value-style="{ color: '#fa8c16' }"
            >
              <template #prefix>
                <PlayCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="已结束的演讲"
              :value="stats.ended"
              :value-style="{ color: '#722ed1' }"
            >
              <template #prefix>
                <CheckCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <a-card title="快速操作" class="action-card">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-button type="primary" size="large" block @click="showCreateModal">
              <template #icon>
                <PlusOutlined />
              </template>
              创建新演讲
            </a-button>
          </a-col>
          <a-col :span="8">
            <a-button size="large" block @click="showJoinModal">
              <template #icon>
                <EnterOutlined />
              </template>
              加入演讲
            </a-button>
          </a-col>
          <a-col :span="8">
            <a-button size="large" block @click="showInviteModal">
              <template #icon>
                <UserAddOutlined />
              </template>
              发送邀请
            </a-button>
          </a-col>
        </a-row>
      </a-card>
    </div>

    <!-- 被邀请情况 -->
    <div class="invitation-section">
      <a-collapse
        class="invitation-collapse"
        :bordered="false"
        expand-icon-position="right"
        :expand-icon="() => null"
        v-model:activeKey="inviteCollapseActiveKey"
      >
        <a-collapse-panel key="1">
          <template #header>
            <div class="invite-collapse-header">
              <span class="badge-wrapper">
                <span v-if="unhandledInviteCount > 0" class="invite-badge">{{ unhandledInviteCount }}</span>
              </span>
              <span class="invite-collapse-title">被邀请情况</span>
              <span class="invite-filter-select-wrapper" v-if="inviteCollapseActiveKey.includes('1')" @click.stop>
                <a-select
                  v-model:value="inviteFilter"
                  :options="inviteFilterOptions"
                  size="small"
                  style="width: 120px; margin-left: 16px;"
                  :dropdown-style="{ minWidth: '120px' }"
                  :bordered="false"
                  :placement="'bottomRight'"
                />
              </span>
            </div>
          </template>
          <div class="invite-list-wrapper">
            <template v-if="filteredInvitedPresentations.length">
              <div v-for="item in filteredInvitedPresentations" :key="item.id" class="invite-card" @mouseover="item._hover = true" @mouseleave="item._hover = false">
                <div class="invite-item-main">
                  <div class="invite-info">
                    <div class="invite-status-tag-top">
                      <a-tag :color="getInviteStatusColor(item.status, item.room_status)">{{ getInviteStatusText(item.status, item.room_status) }}</a-tag>
                    </div>
                    <div class="invite-title">{{ item.room_name }}（{{ getInviteRoleText(item.role) }}）</div>
                    <div class="invite-desc">邀请时间：{{ formatDate(item.invited_time) }}</div>
                  </div>
                  <div class="invite-actions">
                    <div class="invite-btn-group">
                      <a-button v-if="item.status === 0" type="primary" size="small" @click.stop="acceptInvite(item)">接受</a-button>
                      <a-button v-if="item.status === 0" type="default" size="small" @click.stop="rejectInvite(item)">拒绝</a-button>
                      <a-button type="link" size="small" @click.stop="viewInviteDetails(item)">查看详情</a-button>
                    </div>
                    <div class="invite-enter-room" v-if="item.status === 1 && (item.room_status === 0 || item.room_status === 1)">
                      <a-button type="primary" size="small" @click.stop="enterRoomFromInvite(item)">
                        <PlayCircleOutlined />
                        进入房间
                      </a-button>
                    </div>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="invite-empty">暂无被邀请信息</div>
            </template>
          </div>
        </a-collapse-panel>
      </a-collapse>
    </div>

    <!-- 演讲列表 -->
    <div class="presentations-section">
      <a-tabs v-model:activeKey="activeTab" class="presentation-tabs">
        <a-tab-pane key="created" tab="我创建的演讲">
          <div class="presentation-grid">
            <a-card
              v-for="presentation in createdPresentations"
              :key="presentation.id"
              class="presentation-card"
              :hoverable="true"
            >
              <template #cover>
                <div class="card-cover">
                  <div class="status-badge" :class="getStatusClass(presentation.status)">
                    {{ getStatusText(presentation.status) }}
                  </div>
                  <div class="room-code">ID: {{ presentation.id }}</div>
                </div>
              </template>
              <a-card-meta :title="presentation.name">
                <template #description>
                  <p class="description">{{ presentation.description || '暂无描述' }}</p>
                  <div class="meta-info">
                    <span class="participants">
                      <TeamOutlined /> {{ presentation.total_participants || 0 }} 人参与
                    </span>
                    <span class="created-time">
                      <CalendarOutlined /> {{ formatDate(presentation.created_at) }}
                    </span>
                  </div>
                </template>
              </a-card-meta>
              <template #actions>
                <div class="action-buttons">
                  <div class="action-row">
                    <a-button type="link" @click.stop="enterRoom(presentation)">
                      <PlayCircleOutlined />
                      进入房间
                    </a-button>
                    <a-button type="link" @click.stop="viewDetails(presentation)">
                      <EyeOutlined />
                      查看详情
                    </a-button>
                    <a-button v-if="presentation.status === 0" type="link" @click.stop="copySpeakerCode(presentation)">
                      <UserAddOutlined />
                      演讲者邀请码
                    </a-button>
                  </div>
                  <div class="action-row">
                    <a-button type="link" @click.stop="copyRoomCode(presentation.invite_code)">
                      <CopyOutlined />
                      复制邀请码
                    </a-button>
                  </div>
                </div>
              </template>
            </a-card>
          </div>
        </a-tab-pane>

        <a-tab-pane key="participated" tab="我参与的演讲">
          <div class="presentation-grid">
            <a-card
              v-for="presentation in participatedPresentations"
              :key="presentation.id"
              class="presentation-card"
              :hoverable="true"
            >
              <template #cover>
                <div class="card-cover">
                  <div class="status-badge" :class="getStatusClass(presentation.status)">
                    {{ getStatusText(presentation.status) }}
                  </div>
                  <div class="room-code">ID: {{ presentation.id }}</div>
                </div>
              </template>
              <a-card-meta :title="presentation.name">
                <template #description>
                  <p class="description">{{ presentation.description || '暂无描述' }}</p>
                  <div class="meta-info">
                    <span class="organizer">
                      <UserOutlined /> {{ presentation.creator_name }}
                    </span>
                    <span class="joined-time">
                      <CalendarOutlined /> {{ formatDate(presentation.created_at) }}
                    </span>
                  </div>
                </template>
              </a-card-meta>
              <template #actions>
                <div class="action-buttons">
                  <div class="action-row">
                    <a-button type="link" @click.stop="enterRoom(presentation)">
                      <PlayCircleOutlined />
                      进入房间
                    </a-button>
                    <a-button type="link" @click.stop="viewDetails(presentation)">
                      <EyeOutlined />
                      查看详情
                    </a-button>
                  </div>
                </div>
              </template>
            </a-card>
          </div>
        </a-tab-pane>

        <a-tab-pane key="ended" tab="已结束的演讲">
          <div class="presentation-grid">
            <a-card
              v-for="presentation in endedPresentations"
              :key="presentation.id"
              class="presentation-card ended"
              :hoverable="true"
            >
              <template #cover>
                <div class="card-cover ended">
                  <div class="status-badge ended">已结束</div>
                  <div class="room-code">ID: {{ presentation.id }}</div>
                </div>
              </template>
              <a-card-meta :title="presentation.name">
                <template #description>
                  <p class="description">{{ presentation.description || '暂无描述' }}</p>
                  <div class="meta-info">
                    <span class="participants">
                      <TeamOutlined /> {{ presentation.total_participants || 0 }} 人参与
                    </span>
                    <span class="ended-time">
                      <CalendarOutlined /> {{ formatDate(presentation.created_at) }}
                    </span>
                  </div>
                </template>
              </a-card-meta>
              <template #actions>
                <a-button type="link" @click.stop="viewResults(presentation)">
                  <BarChartOutlined />
                  查看结果
                </a-button>
                <a-button type="link" @click.stop="viewDetails(presentation)">
                  <EyeOutlined />
                  查看详情
                </a-button>
              </template>
            </a-card>
          </div>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- 创建演讲模态框 -->
    <a-modal
      v-model:open="createModalVisible"
      title="创建新演讲"
      @ok="handleCreatePresentation"
      @cancel="createModalVisible = false"
      :confirm-loading="createLoading"
    >
      <a-form :model="createForm" :rules="createRules" ref="createFormRef">
        <a-form-item label="演讲标题" name="name">
          <a-input v-model:value="createForm.name" placeholder="请输入演讲标题" />
        </a-form-item>
        <a-form-item label="演讲描述" name="description">
          <a-textarea
            v-model:value="createForm.description"
            placeholder="请输入演讲描述"
            :rows="4"
          />
        </a-form-item>
        <a-form-item name="is_speaker">
          <a-checkbox v-model:checked="createForm.is_speaker">
            我担任本次演讲的演讲人
          </a-checkbox>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 加入演讲模态框 -->
    <a-modal
      v-model:open="joinModalVisible"
      title="加入演讲"
      @ok="handleJoinPresentation"
      @cancel="joinModalVisible = false"
      :confirm-loading="joinLoading"
    >
      <a-form :model="joinForm" :rules="joinRules" ref="joinFormRef">
        <a-form-item label="邀请码" name="invite_code">
          <a-input
            v-model:value="joinForm.invite_code"
            placeholder="请输入邀请码"
            style="text-transform: uppercase;"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 发送邀请模态框 -->
    <a-modal
      v-model:open="inviteModalVisible"
      title="发送邀请"
      @ok="handleSendInvitation"
      @cancel="inviteModalVisible = false"
      :confirm-loading="inviteLoading"
    >
      <a-form :model="inviteForm" :rules="inviteRules" ref="inviteFormRef">
        <a-form-item label="选择演讲室" name="room_id">
          <a-select
            v-model:value="inviteForm.room_id"
            placeholder="请选择要邀请的演讲室"
            :options="createdPresentations.map(room => ({
              label: room.name,
              value: room.id
            }))"
          />
        </a-form-item>
        <a-form-item label="被邀请用户名" name="invitee_username">
          <a-input
            v-model:value="inviteForm.invitee_username"
            placeholder="请输入被邀请用户的用户名"
          />
        </a-form-item>
        <a-form-item label="邀请角色" name="role">
          <a-radio-group v-model:value="inviteForm.role">
            <a-radio :value="0">听众</a-radio>
            <a-radio :value="1">演讲者</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 房间详情弹窗 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="房间详情"
      width="600px"
      :footer="null"
      @cancel="detailModalVisible = false"
    >
      <div v-if="currentPresentation" class="presentation-detail">
        <div class="detail-header">
          <h2>{{ currentPresentation.name }}</h2>
          <a-tag :color="getStatusColor(currentPresentation.status)">
            {{ getStatusText(currentPresentation.status) }}
          </a-tag>
        </div>
        
        <div class="detail-content">
          <a-descriptions :column="1" bordered>
            <a-descriptions-item label="房间ID">
              <span class="room-code-display">{{ currentPresentation.id }}</span>
            </a-descriptions-item>
            <a-descriptions-item v-if="currentPresentation.role === 0" label="听众邀请码">
              <span class="room-code-display">{{ currentPresentation.invite_code }}</span>
              <a-button type="link" size="small" @click="copyRoomCode(currentPresentation.invite_code)">
                <CopyOutlined /> 复制
              </a-button>
            </a-descriptions-item>
            <a-descriptions-item v-if="currentPresentation.role === 0" label="演讲者邀请码">
              <span class="room-code-display">{{ currentPresentation.speaker_invite_code }}</span>
              <a-button type="link" size="small" @click="copySpeakerCode(currentPresentation)">
                <CopyOutlined /> 复制
              </a-button>
            </a-descriptions-item>
            <a-descriptions-item label="演讲描述">
              {{ currentPresentation.description || '暂无描述' }}
            </a-descriptions-item>
            <a-descriptions-item label="创建时间">
              {{ formatDate(currentPresentation.created_at) }}
            </a-descriptions-item>
            <a-descriptions-item label="组织者">
              <div class="user-info">
                <a-avatar :size="32" style="background-color: #1677ff">
                  {{ currentPresentation.creator_name?.charAt(0) || 'O' }}
                </a-avatar>
                <span class="username">{{ currentPresentation.creator_name || '未知' }}</span>
              </div>
            </a-descriptions-item>
            <a-descriptions-item label="演讲者">
              <div class="speaker-info">
                <div v-if="currentPresentation.speaker_name" class="speaker-item">
                  <a-avatar :size="32" style="background-color: #52c41a">
                    {{ currentPresentation.speaker_name?.charAt(0) || 'S' }}
                  </a-avatar>
                  <span class="username">{{ currentPresentation.speaker_name }}</span>
                  <a-tag v-if="currentPresentation.speaker_id === currentPresentation.creator_id" color="blue" size="small">组织者</a-tag>
                </div>
                <div v-else class="no-speaker">
                  暂无演讲者
                </div>
              </div>
            </a-descriptions-item>
            <a-descriptions-item label="参与者数量">
              {{ currentPresentation.total_participants || 0 }} 人
            </a-descriptions-item>
          </a-descriptions>
        </div>
        
        <div class="detail-actions">
          <a-button type="primary" @click="enterRoom(currentPresentation)">
            <PlayCircleOutlined />
            进入房间
          </a-button>
          <a-button @click="detailModalVisible = false">
            关闭
          </a-button>
        </div>
      </div>
    </a-modal>

    <!-- 被邀请条详情弹窗 -->
    <a-modal
      v-model:open="inviteDetailModalVisible"
      title="邀请详情"
      width="500px"
      :footer="null"
      @cancel="inviteDetailModalVisible = false"
    >
      <div v-if="currentInvite" class="invite-detail">
        <div class="invite-detail-header">
          <h3>{{ currentInvite.room_name }}</h3>
          <a-tag :color="getInviteStatusColor(currentInvite.status, currentInvite.room_status)">
            {{ getInviteStatusText(currentInvite.status, currentInvite.room_status) }}
          </a-tag>
        </div>
        
        <div class="invite-detail-content">
          <a-descriptions :column="1" bordered size="small">
            <a-descriptions-item label="房间名称">
              <span class="room-code-display">{{ currentInvite.room_name }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="演讲室描述">
              {{ currentInvite.description || '暂无描述' }}
            </a-descriptions-item>
            <a-descriptions-item label="演讲室创建时间">
              {{ formatDate(currentInvite.created_at) }}
            </a-descriptions-item>
            <a-descriptions-item label="组织者">
              <div class="user-info">
                <a-avatar :size="24" style="background-color: #1677ff">
                  {{ currentInvite.creator_name?.charAt(0) || 'O' }}
                </a-avatar>
                <span class="username">{{ currentInvite.creator_name || '未知' }}</span>
              </div>
            </a-descriptions-item>
            <a-descriptions-item label="演讲者">
              <div class="speaker-info">
                <div v-if="currentInvite.speaker_name" class="speaker-item">
                  <a-avatar :size="24" style="background-color: #52c41a">
                    {{ currentInvite.speaker_name?.charAt(0) || 'S' }}
                  </a-avatar>
                  <span class="username">{{ currentInvite.speaker_name }}</span>
                </div>
                <div v-else class="no-speaker">
                  暂无演讲者
                </div>
              </div>
            </a-descriptions-item>
            <a-descriptions-item label="参与人数">
              {{ currentInvite.total_participants || 0 }} 人
            </a-descriptions-item>
            <a-descriptions-item label="邀请角色">
              <a-tag :color="currentInvite.role === 1 ? 'green' : 'blue'">
                {{ getInviteRoleText(currentInvite.role) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="房间状态">
              <a-tag :color="getStatusColor(currentInvite.room_status)">
                {{ getStatusText(currentInvite.room_status) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="邀请时间">
              {{ formatDate(currentInvite.invited_time) }}
            </a-descriptions-item>
          </a-descriptions>
        </div>
        
        <div class="invite-detail-actions">
          <a-button v-if="currentInvite.status === 0" type="primary" @click="acceptInvite(currentInvite)">
            <CheckCircleOutlined />
            接受邀请
          </a-button>
          <a-button v-if="currentInvite.status === 0" @click="rejectInvite(currentInvite)">
            <CloseCircleOutlined />
            拒绝邀请
          </a-button>
          <a-button v-if="currentInvite.status === 1 && (currentInvite.room_status === 0 || currentInvite.room_status === 1)" type="primary" @click="enterRoomFromInvite(currentInvite)">
            <PlayCircleOutlined />
            进入房间
          </a-button>
          <a-button @click="inviteDetailModalVisible = false">
            关闭
          </a-button>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, h } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { Select } from 'ant-design-vue';
import {
  PlusOutlined,
  UserOutlined,
  DownOutlined,
  SettingOutlined,
  LogoutOutlined,
  FileTextOutlined,
  TeamOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  EnterOutlined,
  ReloadOutlined,
  CalendarOutlined,
  EyeOutlined,
  CopyOutlined,
  BarChartOutlined,
  UserAddOutlined,
  CloseCircleOutlined
} from '@ant-design/icons-vue';
import { userAPI, speechRoomAPI, invitationAPI, checkTokenExpired } from '../../api';

const router = useRouter();

// 响应式数据
const activeTab = ref('created');
const createModalVisible = ref(false);
const joinModalVisible = ref(false);
const inviteModalVisible = ref(false);
const detailModalVisible = ref(false);
const inviteDetailModalVisible = ref(false);
const createLoading = ref(false);
const joinLoading = ref(false);
const inviteLoading = ref(false);
const currentPresentation = ref(null);
const currentInvite = ref(null);
const createFormRef = ref();
const joinFormRef = ref();
const inviteFormRef = ref();

// 用户信息
const userInfo = ref({
  username: localStorage.getItem('username') || '用户'
});

// 统计数据
const stats = ref({
  created: 0,
  participated: 0,
  active: 0,
  ended: 0
});

// 演讲数据
const createdPresentations = ref([]);
const participatedPresentations = ref([]);
const endedPresentations = ref([]);
const invitedPresentations = ref([]);
const unhandledInviteCount = computed(() => invitedPresentations.value.filter(i => i.status === 0).length);

// 新增：筛选状态
const inviteFilter = ref(0); // 0: 待接受, 1: 已接受, 2: 已拒绝, 3: 房间已关闭, -1: 全部
const inviteFilterOptions = [
  { label: '待接受', value: 0 },
  { label: '已接受', value: 1 },
  { label: '已拒绝', value: 2 },
  { label: '房间已关闭', value: 3 },
  { label: '全部', value: -1 }
];
const filteredInvitedPresentations = computed(() => {
  if (inviteFilter.value === -1) return invitedPresentations.value;
  return invitedPresentations.value.filter(i => i.status === inviteFilter.value);
});

// 折叠栏展开状态
const inviteCollapseActiveKey = ref([]);

// 表单数据
const createForm = reactive({
  name: '',
  description: '',
  is_speaker: false
});

const joinForm = reactive({
  invite_code: ''
});

const inviteForm = reactive({
  room_id: null,
  invitee_username: '',
  role: 0
});

// 表单验证规则
const createRules = {
  name: [{ required: true, message: '请输入演讲标题', trigger: 'blur' }]
};

const joinRules = {
  invite_code: [
    { required: true, message: '请输入邀请码', trigger: 'blur' }
  ]
};

const inviteRules = {
  room_id: [
    { required: true, message: '请选择演讲室', trigger: 'change' }
  ],
  invitee_username: [
    { required: true, message: '请输入被邀请用户名', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择邀请角色', trigger: 'change' }
  ]
};

// 获取用户演讲室数据
const fetchUserSpeechRooms = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      checkTokenExpired();
      return;
    }

    const response = await userAPI.getUserSpeechRooms(token);
    const rooms = response.data.rooms || [];
    
    // 分类演讲室
    createdPresentations.value = rooms.filter(room => room.role === 0);
    participatedPresentations.value = rooms.filter(room => room.role === 1 || room.role === 2);
    endedPresentations.value = rooms.filter(room => room.status === 2);
    
    // 更新统计数据
    stats.value = {
      created: createdPresentations.value.length,
      participated: participatedPresentations.value.length,
      active: rooms.filter(room => room.status === 1).length,
      ended: endedPresentations.value.length
    };
  } catch (error) {
    console.error('获取用户演讲室失败:', error);
    message.error('获取数据失败');
  }
};

// 获取用户邀请数据
const fetchUserInvitations = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      checkTokenExpired();
      return;
    }

    const response = await userAPI.getUserInvitations(token);
    invitedPresentations.value = response.data.invitations || [];
  } catch (error) {
    console.error('获取用户邀请失败:', error);
    message.error('获取邀请数据失败');
  }
};

// 方法
const showCreateModal = () => {
  createModalVisible.value = true;
};

const showJoinModal = () => {
  joinModalVisible.value = true;
};

const showInviteModal = () => {
  inviteModalVisible.value = true;
};

const handleSendInvitation = async () => {
  try {
    // 先进行表单验证
    await inviteFormRef.value.validate();
    
    inviteLoading.value = true;
    const token = localStorage.getItem('token');
    if (!token) {
      checkTokenExpired();
      return;
    }

    const response = await invitationAPI.inviteUser({
      token: token,
      invitee_username: inviteForm.invitee_username,
      room_id: inviteForm.room_id,
      role: inviteForm.role
    });

    message.success('邀请发送成功！');
    inviteModalVisible.value = false;
    
    // 重置表单
    inviteForm.room_id = null;
    inviteForm.invitee_username = '';
    inviteForm.role = 0;
    
    refreshData();
  } catch (error) {
    if (error?.errorFields) {
      // 表单验证失败，不显示错误消息
      return;
    }
    console.error('发送邀请失败:', error);
    message.error(error.response?.data?.message || '发送邀请失败，请重试');
  } finally {
    inviteLoading.value = false;
  }
};

const handleCreatePresentation = async () => {
  try {
    // 先进行表单验证
    await createFormRef.value.validate();
    
    createLoading.value = true;
    const token = localStorage.getItem('token');
    if (!token) {
      checkTokenExpired();
      return;
    }

    const response = await speechRoomAPI.createSpeechRoom({
      session_token: token,
      name: createForm.name,
      description: createForm.description,
      is_speaker: createForm.is_speaker
    });

    message.success('演讲创建成功！');
    createModalVisible.value = false;
    
    // 重置表单
    createForm.name = '';
    createForm.description = '';
    createForm.is_speaker = false;
    
    refreshData();
  } catch (error) {
    if (error?.errorFields) {
      // 表单验证失败，不显示错误消息
      return;
    }
    console.error('创建演讲失败:', error);
    message.error(error.response?.data?.message || '创建失败，请重试');
  } finally {
    createLoading.value = false;
  }
};

const handleJoinPresentation = async () => {
  try {
    // 先进行表单验证
    await joinFormRef.value.validate();
    
    joinLoading.value = true;
    const token = localStorage.getItem('token');
    if (!token) {
      checkTokenExpired();
      return;
    }

    const response = await speechRoomAPI.joinRoom({
      token: token,
      invite_code: joinForm.invite_code
    });

    message.success('成功加入演讲！');
    joinModalVisible.value = false;
    
    // 重置表单
    joinForm.invite_code = '';
    
    refreshData();
  } catch (error) {
    if (error?.errorFields) {
      // 表单验证失败，不显示错误消息
      return;
    }
    console.error('加入演讲失败:', error);
    message.error(error.response?.data?.message || '加入失败，请检查邀请码');
  } finally {
    joinLoading.value = false;
  }
};

const refreshData = async () => {
  await Promise.all([
    fetchUserSpeechRooms(),
    fetchUserInvitations()
  ]);
  message.success('数据已刷新');
};

const viewPresentation = (presentation) => {
  router.push(`/presentation/${presentation.id}`);
};

const enterRoom = (presentation) => {
  // 根据用户角色决定跳转到哪个页面
  // role: 0-创建者，1-演讲者，2-听众
  if (presentation.role === 0 || presentation.role === 1) {
    // 创建者或演讲者进入Speakerroom
    router.push(`/speakerroom/${presentation.id}`);
  } else {
    // 听众进入Room
    router.push(`/room/${presentation.id}`);
  }
};

// 新增：处理邀请条进入房间的逻辑
const enterRoomFromInvite = (invite) => {
  // 邀请中的role表示被邀请成为的角色：0-听众，1-演讲者
  if (invite.role === 1) {
    // 被邀请为演讲者，进入Speakerroom
    router.push(`/speakerroom/${invite.room_id}`);
  } else {
    // 被邀请为听众，进入Room
    router.push(`/room/${invite.room_id}`);
  }
};

const viewDetails = (presentation) => {
  currentPresentation.value = presentation;
  detailModalVisible.value = true;
};

const viewInviteDetails = (invite) => {
  currentInvite.value = invite;
  inviteDetailModalVisible.value = true;
};

const viewResults = (presentation) => {
  router.push(`/presentation/${presentation.id}/results`);
};

const copyRoomCode = (roomCode) => {
  if (!roomCode) {
    message.warning('暂无邀请码');
    return;
  }
  navigator.clipboard.writeText(roomCode);
  message.success('邀请码已复制到剪贴板');
};

const copySpeakerCode = (presentation) => {
  if (!presentation.speaker_invite_code) {
    message.warning('暂无演讲者邀请码');
    return;
  }
  navigator.clipboard.writeText(presentation.speaker_invite_code);
  message.success('演讲者邀请码已复制到剪贴板');
};

const handleLogout = async () => {
  try {
    const token = localStorage.getItem('token');
    if (token) {
      await userAPI.logout({ token });
    }
  } catch (error) {
    console.error('退出登录失败:', error);
  } finally {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    router.push('/auth');
    message.success('已退出登录');
  }
};

const getStatusText = (status) => {
  const statusMap = {
    0: '等待开始',
    1: '进行中',
    2: '已结束'
  };
  return statusMap[status] || status;
};

const getStatusClass = (status) => {
  const classMap = {
    0: 'pending',
    1: 'active',
    2: 'ended'
  };
  return classMap[status] || '';
};

const getStatusColor = (status) => {
  const colorMap = {
    0: 'orange',
    1: 'green',
    2: 'purple'
  };
  return colorMap[status] || 'default';
};

const getInviteRoleText = (role) => {
  if (role === 1) return '演讲者';
  if (role === 0) return '听众';
  return '未知';
};

const acceptInvite = async (item) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      checkTokenExpired();
      return;
    }

    await invitationAPI.acceptInvitation({
      id: item.id,
      token: token
    });

    item.status = 1;
    message.success('已接受邀请');
    refreshData();
  } catch (error) {
    console.error('接受邀请失败:', error);
    message.error(error.response?.data?.message || '接受邀请失败');
  }
};

const rejectInvite = async (item) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      checkTokenExpired();
      return;
    }

    await invitationAPI.rejectInvitation({
      id: item.id,
      token: token
    });

    item.status = 2;
    message.info('已拒绝邀请');
    refreshData();
  } catch (error) {
    console.error('拒绝邀请失败:', error);
    message.error(error.response?.data?.message || '拒绝邀请失败');
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '未知时间';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 新增方法
const getInviteStatusText = (status, roomStatus) => {
  if (status === 0) {
    // 如果邀请状态是待接受，根据房间状态显示
    switch (roomStatus) {
      case 0: return '待接受';
      case 1: return '房间进行中';
      case 2: return '房间已结束';
      default: return '待接受';
    }
  } else {
    switch (status) {
      case 1: return '已接受';
      case 2: return '已拒绝';
      default: return '未知';
    }
  }
};

const getInviteStatusColor = (status, roomStatus) => {
  if (status === 0) {
    // 如果邀请状态是待接受，根据房间状态显示颜色
    switch (roomStatus) {
      case 0: return 'orange';
      case 1: return 'blue';
      case 2: return 'gray';
      default: return 'orange';
    }
  } else {
    switch (status) {
      case 1: return 'green';
      case 2: return 'red';
      default: return 'default';
    }
  }
};

const panelExpandIcon = ({ isActive }) => {
  return isActive
    ? h('span', { class: 'invite-collapse-arrow' }, [
        h('svg', { width: 28, height: 28, viewBox: '0 0 24 24' }, [
          h('path', { d: 'M7 10l5 5 5-5z', fill: '#1677ff' })
        ])
      ])
    : h('span', { class: 'invite-collapse-arrow' }, [
        h('svg', { width: 28, height: 28, viewBox: '0 0 24 24' }, [
          h('path', { d: 'M10 7l5 5-5 5z', fill: '#1677ff' })
        ])
      ]);
};

// 生命周期
onMounted(() => {
  // 检查token是否存在
  if (checkTokenExpired()) {
    return;
  }
  refreshData();
});
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px 30px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  font-size: 2rem;
  font-weight: 700;
  color: #1677ff;
  margin: 0;
}

.subtitle {
  color: #666;
  font-size: 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.stat-card:hover {
  transform: translateY(-4px);
}

.invitation-section {
  margin-bottom: 24px;
}

.invitation-collapse {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: none;
  background: #fff;
}
.invitation-collapse .ant-collapse-item {
  border: none;
}
.invitation-collapse .ant-collapse-content {
  border: none;
  background: transparent;
}
.invite-collapse-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  font-size: 1.15rem;
  font-weight: 600;
  color: #1677ff;
  padding: 2px 0;
  position: relative;
  min-height: 44px;
}
.invite-collapse-title {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  height: 32px;
}
.badge-wrapper {
  display: flex;
  align-items: center;
  margin-left: 0;
  margin-right: 8px;
}
.invite-badge {
  display: inline-block;
  min-width: 22px;
  height: 22px;
  line-height: 22px;
  background: #52c41a;
  color: #fff;
  border-radius: 50%;
  text-align: center;
  font-size: 14px;
  font-weight: bold;
  margin-left: 0;
}
.invite-collapse-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  margin-left: 12px;
}
.invite-list-wrapper {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-top: 12px;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: height, padding, margin;
  max-height: calc(4 * 84px + 3 * 2px + 36px); /* 3条邀请卡高度+2个间隔 */
  overflow-y: auto;
  padding-right: 4px;
}
/* 美化滚动条 */
.invite-list-wrapper::-webkit-scrollbar {
  width: 8px;
  background: transparent;
}
.invite-list-wrapper::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #4f54ee 0%, #0b45a3 100%);
  border-radius: 6px;
}
.invite-list-wrapper::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #b3d8ff 0%, #a0aec0 100%);
}
/* Firefox */
.invite-list-wrapper {
  scrollbar-width: thin;
  scrollbar-color: #e6f0ff #f5f7fa;
}
.invite-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(22, 119, 255, 0.08);
  border: 1px solid #f0f0f0;
  padding: 20px 24px 16px 24px;
  transition: box-shadow 0.2s, border-color 0.2s;
  cursor: pointer;
  position: relative;
}
.invite-card:hover {
  box-shadow: 0 6px 24px rgba(22, 119, 255, 0.18);
  border-color: #1677ff;
}
.invite-empty {
  color: #aaa;
  text-align: center;
  padding: 32px 0;
  font-size: 1.1rem;
}

.invitation-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.quick-actions {
  margin-bottom: 24px;
}

.action-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.presentations-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.presentation-tabs {
  background: transparent;
}

.presentation-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 24px;
}

.presentation-tabs :deep(.ant-tabs-tab) {
  font-size: 1.1rem;
  font-weight: 500;
}

.presentation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.presentation-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.95);
  min-width: 380px;
}

.presentation-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  border-color: rgba(22, 119, 255, 0.3);
}

.card-cover {
  height: 120px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  border-radius: 8px 8px 0 0;
}

.card-cover.ended {
  background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
}

.status-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.pending {
  background: rgba(250, 140, 22, 0.9);
  color: white;
}

.status-badge.active {
  background: rgba(82, 196, 26, 0.9);
  color: white;
}

.status-badge.ended {
  background: rgba(114, 46, 209, 0.9);
  color: white;
}

.room-code {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 0.9rem;
  opacity: 0.8;
}

.description {
  color: #666;
  margin-bottom: 12px;
  line-height: 1.5;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #999;
}

.meta-info span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.presentation-card :deep(.ant-card-actions) {
  background: rgba(250, 250, 250, 0.8);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  padding: 12px 0;
}

.presentation-card :deep(.ant-card-actions li) {
  margin: 0;
  padding: 0;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.action-row:last-child {
  justify-content: flex-start;
}

.presentation-card :deep(.ant-card-actions .ant-btn) {
  color: #1677ff;
  border: none;
  padding: 4px 8px;
  flex: 1;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  font-size: 15px;
}

.presentation-card :deep(.ant-card-actions .ant-btn:hover) {
  background: rgba(22, 119, 255, 0.1);
  border-radius: 4px;
}

/* 房间详情样式 */
.presentation-detail {
  padding: 16px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-header h2 {
  margin: 0;
  color: #1677ff;
  font-size: 1.5rem;
}

.detail-content {
  margin-bottom: 24px;
}

.room-code-display {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  color: #1677ff;
  font-size: 1.1rem;
  margin-right: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-weight: 500;
  color: #333;
}

.speaker-info {
  display: flex;
  align-items: center;
}

.speaker-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #fafafa;
  border-radius: 6px;
}

.no-speaker {
  color: #999;
  font-style: italic;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 邀请详情样式 */
.invite-detail {
  padding: 16px 0;
}

.invite-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.invite-detail-header h3 {
  margin: 0;
  color: #1677ff;
  font-size: 1.3rem;
}

.invite-detail-content {
  margin-bottom: 20px;
}

.invite-detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .presentation-grid {
    grid-template-columns: 1fr;
  }
  
  .presentation-card {
    min-width: auto;
  }
  
  .stats-section .ant-col {
    margin-bottom: 16px;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .detail-actions {
    flex-direction: column;
  }
}

/* 新增样式 */
.invite-item-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
}
.invite-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  position: relative;
}
.invite-status-tag-top {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}
.invite-title {
  font-weight: 500;
  font-size: 1.05rem;
  color: #222;
  margin-top: 24px;
}
.invite-desc {
  color: #888;
  font-size: 0.95rem;
}
.invite-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}
.invite-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.invite-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.invite-enter-room {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
.invitation-section .ant-collapse-item {
  transition: border-color 0.3s, box-shadow 0.3s, background 0.3s, border-radius 0.3s;
  border-radius: 12px;
  border: 1.5px solid transparent;
}
.invitation-section .ant-collapse-item:hover {
  border: 1.5px solid #1677ff;
  background: #fff;
  box-shadow: none;
  border-radius: 12px;
}
.invitation-section .ant-collapse-item-active,
.invitation-section .ant-collapse-item-active:hover {
  border: 1.5px solid transparent;
  background: #fff;
  box-shadow: none;
  border-radius: 12px;
}

/* 邀请筛选下拉框样式 */
.invite-filter-select-wrapper {
  margin-left: auto;
  display: flex;
  align-items: center;
  min-width: 120px;
  background: #f5f7fa;
  border-radius: 18px;
  padding: 2px 12px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.06);
  border: 1px solid #e6eaf1;
  transition: box-shadow 0.2s, border-color 0.2s;
  height: 36px;
}
.invite-filter-select-wrapper:hover {
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.12);
  border-color: #1677ff;
}
.invite-filter-select-wrapper .ant-select {
  background: transparent !important;
  border: none !important;
}
.invite-filter-select-wrapper .ant-select-selector {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  font-size: 15px;
  color: #1677ff;
  padding: 0 4px;
  border-radius: 16px;
  min-height: 32px;
}
.invite-filter-select-wrapper .ant-select-arrow {
  color: #1677ff;
}
.invite-filter-select-wrapper .ant-select-dropdown {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.12);
  background: #fff;
  border: 1px solid #e6eaf1;
  padding: 6px 0;
}
.invite-filter-select-wrapper .ant-select-item {
  border-radius: 8px;
  margin: 0 8px;
  padding: 6px 16px;
  transition: background 0.2s, color 0.2s;
  font-size: 15px;
}
.invite-filter-select-wrapper .ant-select-item-option-active:not(.ant-select-item-option-selected),
.invite-filter-select-wrapper .ant-select-item-option:hover:not(.ant-select-item-option-selected) {
  background: #e6f0ff !important;
  color: #1677ff !important;
}
.invite-filter-select-wrapper .ant-select-item-option-selected {
  background: #1677ff !important;
  color: #fff !important;
}
</style>
