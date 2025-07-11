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
              <div v-for="item in filteredInvitedPresentations" :key="item.id" class="invite-card" @mouseover="item._hover = true" @mouseleave="item._hover = false" @click="enterRoom(item)">
                <div class="invite-item-main">
                  <div class="invite-info">
                    <div class="invite-status-tag-top">
                      <a-tag :color="getInviteStatusColor(item.status)">{{ getInviteStatusText(item.status) }}</a-tag>
                    </div>
                    <div class="invite-title">{{ item.title }}（{{ getInviteRoleText(item.role) }}）</div>
                    <div class="invite-desc">邀请人：{{ item.inviter_name }}，房间号：{{ item.room_code }}</div>
                  </div>
                  <div class="invite-actions">
                    <div class="invite-btn-group">
                      <a-button v-if="item.status === 0" type="primary" size="small" @click.stop="acceptInvite(item)">接受</a-button>
                      <a-button v-if="item.status === 0" type="default" size="small" @click.stop="rejectInvite(item)">拒绝</a-button>
                      <a-button type="link" size="small" @click.stop="viewDetails(item)">查看详情</a-button>
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
            <a-button size="large" block @click="refreshData">
              <template #icon>
                <ReloadOutlined />
              </template>
              刷新数据
            </a-button>
          </a-col>
        </a-row>
      </a-card>
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
              @click="viewPresentation(presentation)"
            >
              <template #cover>
                <div class="card-cover">
                  <div class="status-badge" :class="presentation.status">
                    {{ getStatusText(presentation.status) }}
                  </div>
                  <div class="room-code">{{ presentation.room_code }}</div>
                </div>
              </template>
              <a-card-meta :title="presentation.title">
                <template #description>
                  <p class="description">{{ presentation.description || '暂无描述' }}</p>
                  <div class="meta-info">
                    <span class="participants">
                      <TeamOutlined /> {{ presentation.participant_count || 0 }} 人参与
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
                    <a-button v-if="presentation.status === 'pending'" type="link" @click.stop="copySpeakerCode(presentation)">
                      <UserAddOutlined />
                      演讲者邀请码
                    </a-button>
                  </div>
                  <div class="action-row">
                    <a-button type="link" @click.stop="copyRoomCode(presentation.room_code)">
                      <CopyOutlined />
                      复制房间号
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
              @click="viewPresentation(presentation)"
            >
              <template #cover>
                <div class="card-cover">
                  <div class="status-badge" :class="presentation.status">
                    {{ getStatusText(presentation.status) }}
                  </div>
                  <div class="room-code">{{ presentation.room_code }}</div>
                </div>
              </template>
              <a-card-meta :title="presentation.title">
                <template #description>
                  <p class="description">{{ presentation.description || '暂无描述' }}</p>
                  <div class="meta-info">
                    <span class="organizer">
                      <UserOutlined /> {{ presentation.organizer_name }}
                    </span>
                    <span class="joined-time">
                      <CalendarOutlined /> {{ formatDate(presentation.joined_at) }}
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
                    <a-button v-if="presentation.status === 'pending'" type="link" @click.stop="copySpeakerCode(presentation)">
                      <UserAddOutlined />
                      复制演讲者邀请码
                    </a-button>
                  </div>
                  <div class="action-row">
                    <a-button type="link" @click.stop="copyRoomCode(presentation.room_code)">
                      <CopyOutlined />
                      复制房间号
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
              @click="viewPresentation(presentation)"
            >
              <template #cover>
                <div class="card-cover ended">
                  <div class="status-badge ended">已结束</div>
                  <div class="room-code">{{ presentation.room_code }}</div>
                </div>
              </template>
              <a-card-meta :title="presentation.title">
                <template #description>
                  <p class="description">{{ presentation.description || '暂无描述' }}</p>
                  <div class="meta-info">
                    <span class="participants">
                      <TeamOutlined /> {{ presentation.participant_count || 0 }} 人参与
                    </span>
                    <span class="ended-time">
                      <CalendarOutlined /> {{ formatDate(presentation.ended_at) }}
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
        <a-form-item label="演讲标题" name="title">
          <a-input v-model:value="createForm.title" placeholder="请输入演讲标题" />
        </a-form-item>
        <a-form-item label="演讲描述" name="description">
          <a-textarea
            v-model:value="createForm.description"
            placeholder="请输入演讲描述"
            :rows="4"
          />
        </a-form-item>
        <a-form-item name="isSpeaker">
          <a-checkbox v-model:checked="createForm.isSpeaker">
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
        <a-form-item label="房间号" name="roomCode">
          <a-input
            v-model:value="joinForm.roomCode"
            placeholder="请输入6位房间号"
            maxlength="6"
            style="text-transform: uppercase;"
          />
        </a-form-item>
        <a-form-item label="加入身份" name="joinRole">
          <a-radio-group v-model:value="joinForm.joinRole">
            <a-radio value="audience">观众</a-radio>
            <a-radio value="speaker">演讲者</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item v-if="joinForm.joinRole === 'speaker'" label="演讲者邀请码" name="speakerCode">
          <a-input
            v-model:value="joinForm.speakerCode"
            placeholder="请输入演讲者邀请码"
            maxlength="8"
            style="text-transform: uppercase;"
          />
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
          <h2>{{ currentPresentation.title }}</h2>
          <a-tag :color="getStatusColor(currentPresentation.status)">
            {{ getStatusText(currentPresentation.status) }}
          </a-tag>
        </div>
        
        <div class="detail-content">
          <a-descriptions :column="1" bordered>
            <a-descriptions-item label="房间号">
              <span class="room-code-display">{{ currentPresentation.room_code }}</span>
              <a-button type="link" size="small" @click="copyRoomCode(currentPresentation.room_code)">
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
                  {{ currentPresentation.organizer_name?.charAt(0) || 'O' }}
                </a-avatar>
                <span class="username">{{ currentPresentation.organizer_name || '未知' }}</span>
              </div>
            </a-descriptions-item>
            <a-descriptions-item label="演讲者">
              <div class="speaker-info">
                <div v-if="currentPresentation.speaker" class="speaker-item">
                  <a-avatar :size="32" style="background-color: #52c41a">
                    {{ currentPresentation.speaker.name?.charAt(0) || 'S' }}
                  </a-avatar>
                  <span class="username">{{ currentPresentation.speaker.name }}</span>
                  <a-tag v-if="currentPresentation.speaker.is_organizer" color="blue" size="small">组织者</a-tag>
                </div>
                <div v-else class="no-speaker">
                  暂无演讲者
                </div>
              </div>
            </a-descriptions-item>
            <a-descriptions-item label="参与者数量">
              {{ currentPresentation.participant_count || 0 }} 人
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
  UserAddOutlined
} from '@ant-design/icons-vue';

const router = useRouter();

// 响应式数据
const activeTab = ref('created');
const createModalVisible = ref(false);
const joinModalVisible = ref(false);
const detailModalVisible = ref(false);
const createLoading = ref(false);
const joinLoading = ref(false);
const currentPresentation = ref(null);

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
  title: '',
  description: '',
  isSpeaker: false
});

const joinForm = reactive({
  roomCode: '',
  joinRole: 'audience',
  speakerCode: ''
});

// 表单验证规则
const createRules = {
  title: [{ required: true, message: '请输入演讲标题', trigger: 'blur' }]
};

const joinRules = {
  roomCode: [
    { required: true, message: '请输入房间号', trigger: 'blur' },
    { pattern: /^[A-Z0-9]{6}$/, message: '房间号格式不正确', trigger: 'blur' }
  ],
  speakerCode: [
    { 
      required: true, 
      message: '请输入演讲者邀请码', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (joinForm.joinRole === 'speaker' && !value) {
          return Promise.reject('请输入演讲者邀请码');
        }
        return Promise.resolve();
      }
    },
    { 
      pattern: /^[A-Z0-9]{8}$/, 
      message: '邀请码格式不正确', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (joinForm.joinRole === 'speaker' && value && !/^[A-Z0-9]{8}$/.test(value)) {
          return Promise.reject('邀请码格式不正确');
        }
        return Promise.resolve();
      }
    }
  ]
};

// 模拟数据（实际项目中应该从API获取）
const mockData = () => {
  createdPresentations.value = [
    {
      id: '1',
      title: 'Vue.js 3.0 新特性介绍',
      description: '详细介绍Vue.js 3.0的新特性和使用方法',
      room_code: 'ABC123',
      status: 'active',
      participant_count: 15,
      created_at: '2024-01-15T10:00:00Z',
      organizer_name: '李老师',
      speaker: { id: '1', name: '李老师', is_organizer: true }
    },
    {
      id: '2',
      title: 'React Hooks 深度解析',
      description: '深入理解React Hooks的工作原理和最佳实践',
      room_code: 'DEF456',
      status: 'pending',
      participant_count: 8,
      created_at: '2024-01-14T14:30:00Z',
      organizer_name: '张老师',
      speaker: null // 组织者未担任演讲人
    }
  ];

  participatedPresentations.value = [
    {
      id: '3',
      title: 'TypeScript 高级技巧',
      description: '学习TypeScript的高级特性和实用技巧',
      room_code: 'GHI789',
      status: 'active',
      organizer_name: '陈老师',
      joined_at: '2024-01-13T09:00:00Z',
      speaker: { id: '2', name: '刘专家', is_organizer: false }
    }
  ];

  endedPresentations.value = [
    {
      id: '4',
      title: 'JavaScript 异步编程',
      description: '深入理解JavaScript的异步编程模式',
      room_code: 'JKL012',
      status: 'ended',
      participant_count: 25,
      ended_at: '2024-01-12T16:00:00Z',
      organizer_name: '赵老师',
      speaker: { id: '1', name: '赵老师', is_organizer: true }
    }
  ];

  invitedPresentations.value = [
    {
      id: '5',
      title: 'Node.js 实战',
      room_code: 'MNO345',
      inviter_name: '王老师',
      role: 0, // 听众
      status: 0 // 待接受
    },
    {
      id: '6',
      title: 'AI 未来趋势',
      room_code: 'PQR678',
      inviter_name: '李教授',
      role: 1, // 演讲者
      status: 1 // 已接受
    },
    {
      id: '7',
      title: '大数据分析',
      room_code: 'XYZ999',
      inviter_name: '赵老师',
      role: 0, // 听众
      status: 2 // 已拒绝
    },
    {
      id: '8',
      title: '云计算安全',
      room_code: 'CLOUD1',
      inviter_name: '孙教授',
      role: 1, // 演讲者
      status: 3 // 房间已关闭
    }
  ];

  // 更新统计数据
  stats.value = {
    created: createdPresentations.value.length,
    participated: participatedPresentations.value.length,
    active: createdPresentations.value.filter(p => p.status === 'active').length + 
            participatedPresentations.value.filter(p => p.status === 'active').length,
    ended: endedPresentations.value.length
  };
};

// 方法
const showCreateModal = () => {
  createModalVisible.value = true;
};

const showJoinModal = () => {
  joinModalVisible.value = true;
};

const handleCreatePresentation = async () => {
  createLoading.value = true;
  try {
    // 这里应该调用API创建演讲
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const roleText = createForm.isSpeaker ? '组织者兼演讲人' : '组织者';
    message.success(`演讲创建成功！您将作为${roleText}。`);
    createModalVisible.value = false;
    
    // 重置表单
    createForm.title = '';
    createForm.description = '';
    createForm.isSpeaker = false;
    
    refreshData();
  } catch (error) {
    message.error('创建失败，请重试');
  } finally {
    createLoading.value = false;
  }
};

const handleJoinPresentation = async () => {
  joinLoading.value = true;
  try {
    // 这里应该调用API加入演讲
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const roleText = joinForm.joinRole === 'audience' ? '观众' : '演讲者';
    message.success(`成功以${roleText}身份加入演讲！`);
    joinModalVisible.value = false;
    
    // 重置表单
    joinForm.roomCode = '';
    joinForm.joinRole = 'audience';
    joinForm.speakerCode = '';
    
    refreshData();
  } catch (error) {
    message.error('加入失败，请检查房间号和邀请码');
  } finally {
    joinLoading.value = false;
  }
};

const refreshData = () => {
  mockData();
  message.success('数据已刷新');
};

const viewPresentation = (presentation) => {
  router.push(`/presentation/${presentation.id}`);
};

const enterRoom = (presentation) => {
  router.push(`/room/${presentation.id}`);
};

const viewDetails = (presentation) => {
  currentPresentation.value = presentation;
  detailModalVisible.value = true;
};

const viewResults = (presentation) => {
  router.push(`/presentation/${presentation.id}/results`);
};

const copyRoomCode = (roomCode) => {
  navigator.clipboard.writeText(roomCode);
  message.success('房间号已复制到剪贴板');
};

const copySpeakerCode = (presentation) => {
  // 生成演讲者邀请码（实际项目中应该从后端获取）
  const speakerCode = generateSpeakerCode(presentation.room_code);
  navigator.clipboard.writeText(speakerCode);
  message.success('演讲者邀请码已复制到剪贴板');
};

const generateSpeakerCode = (roomCode) => {
  // 基于房间号生成演讲者邀请码（实际项目中应该从后端获取）
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = roomCode.substring(0, 2); // 取房间号前两位
  for (let i = 0; i < 6; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  router.push('/login');
  message.success('已退出登录');
};

const getStatusText = (status) => {
  const statusMap = {
    pending: '等待开始',
    active: '进行中',
    ended: '已结束'
  };
  return statusMap[status] || status;
};

const getStatusColor = (status) => {
  const colorMap = {
    pending: 'orange',
    active: 'green',
    ended: 'purple'
  };
  return colorMap[status] || 'default';
};

const getInviteRoleText = (role) => {
  if (role === 1) return '演讲者';
  if (role === 0) return '听众';
  return '未知';
};

const acceptInvite = (item) => {
  item.status = 1;
  message.success('已接受邀请');
};
const rejectInvite = (item) => {
  item.status = 2;
  message.info('已拒绝邀请');
};

const formatDate = (dateString) => {
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
const getInviteStatusText = (status) => {
  switch (status) {
    case 0: return '待接受';
    case 1: return '已接受';
    case 2: return '已拒绝';
    case 3: return '房间已关闭';
    default: return '未知';
  }
};
const getInviteStatusColor = (status) => {
  switch (status) {
    case 0: return 'orange';
    case 1: return 'green';
    case 2: return 'red';
    case 3: return 'gray';
    default: return 'default';
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
  mockData();
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
  cursor: pointer;
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
