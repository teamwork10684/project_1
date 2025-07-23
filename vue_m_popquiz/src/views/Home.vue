<template>
  <div class="mobile-home">
    <!-- 顶部信息卡片 -->
    <a-card class="top-info-card" :bordered="true">
      <div class="top-title">PopQuiz</div>
      <div class="top-desc">智能演讲互动平台已经全面上线，快来加入我们吧！</div>
      <div class="top-stars">
        <a-rate :count="5" :value="5" disabled allow-half />
      </div>
    </a-card>

    <!-- 操作按钮组 -->
    <div class="quick-btn-group">
      <div class="quick-btn-item" v-for="(btn, idx) in quickBtns" :key="btn.text">
        <a-button
          class="quick-btn gradient-btn"
          :class="{ 'quick-btn-active': activeBtnIndex === idx }"
          @click="handleQuickBtn(idx)"
          block
        >
          <span class="quick-btn-icon" v-html="btn.icon"></span>
          <span class="quick-btn-text">{{ btn.text }}</span>
        </a-button>
      </div>
    </div>

    <!-- Tab切换及数量 -->
    <div class="tabs-with-count">
      <a-tabs v-model:activeKey="activeTab" class="mobile-tabs" tabBarGutter="0">
        <a-tab-pane key="created" tab="我创建的演讲">
          <div class="tab-count-bar sort-bar">
            <span>我创建的演讲共{{ createdList.length }}个</span>
            <a-select v-model:value="createdSortType" size="small" class="sort-select" @change="saveCreatedSortType" dropdown-class-name="sort-select-dropdown">
              <a-select-option value="default">默认排序</a-select-option>
              <a-select-option value="time">按创建时间排序</a-select-option>
              <a-select-option value="status">按房间状态排序</a-select-option>
              <a-select-option value="creator">自己创建的优先</a-select-option>
            </a-select>
          </div>
          <div v-if="sortedCreatedList.length === 0" class="empty-tip">暂无创建的演讲</div>
          <div v-for="item in sortedCreatedList" :key="item.id">
            <div class="custom-room-card">
              <div class="card-top-gradient">
                <a-tag v-if="item.status===1" color="green" class="status-tag">进行中</a-tag>
                <a-tag v-else-if="item.status===2" color="#d9d9d9" class="status-tag">已结束</a-tag>
                <a-tag v-else color="orange" class="status-tag">等待开始</a-tag>
                <span class="room-id">ID: {{ item.id }}</span>
              </div>
              <div class="card-main">
                <div class="room-title">{{ item.name }}</div>
                <div class="room-desc">{{ item.desc || '暂无描述' }}</div>
                <div class="room-info-row">
                  <span class="info-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#888" d="M12 12c2.7 0 8 1.34 8 4v2H4v-2c0-2.66 5.3-4 8-4zm0-2a4 4 0 1 1 0-8 4 4 0 0 1 0 8z"/></svg></span>
                  <span class="info-text">{{ item.participants }}人参与</span>
                  <span class="info-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#888" d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zm0-13H5V6h14v1z"/></svg></span>
                  <span class="info-text">{{ formatTime(item.time) }}</span>
                </div>
              </div>
              <div class="card-actions-row">
                <a-button type="link" size="small" class="action-btn">
                  <span class="btn-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#1677ff" d="M10 17l6-5-6-5v10z"/></svg></span>进入房间
                </a-button>
                <a-button type="link" size="small" class="action-btn" @click="() => showRoomDetail(item)">
                  <span class="btn-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#1677ff" d="M12 20c4.41 0 8-3.59 8-8s-3.59-8-8-8-8 3.59-8 8 3.59 8 8 8zm0-14c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6 2.69-6 6-6zm-1 9h2v2h-2zm0-8h2v6h-2z"/></svg></span>查看详情
                </a-button>
                <a-button type="link" size="small" class="action-btn" @click="() => copyInvite(item.invite)">
                  <span class="btn-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#1677ff" d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg></span>复制邀请码
                </a-button>
              </div>
            </div>
          </div>
        </a-tab-pane>
        <a-tab-pane key="ended" tab="已结束的演讲">
          <div class="tab-count-bar sort-bar">
            <span>已结束的演讲共{{ endedList.length }}个</span>
            <a-select v-model:value="endedSortType" size="small" class="sort-select" @change="saveEndedSortType" dropdown-class-name="sort-select-dropdown">
              <a-select-option value="default">默认排序</a-select-option>
              <a-select-option value="time">按创建时间排序</a-select-option>
              <a-select-option value="status">按房间状态排序</a-select-option>
              <a-select-option value="creator">自己创建的优先</a-select-option>
            </a-select>
          </div>
          <div v-if="sortedEndedList.length === 0" class="empty-tip">暂无已结束的演讲</div>
          <div v-for="item in sortedEndedList" :key="item.id">
            <PresentationCard :item="item" />
          </div>
        </a-tab-pane>
        <a-tab-pane key="joined" tab="我参与的演讲">
          <div class="tab-count-bar sort-bar">
            <span>我参与的演讲共{{ joinedList.length }}个</span>
            <a-select v-model:value="sortType" size="small" class="sort-select" @change="saveSortType" dropdown-class-name="sort-select-dropdown">
              <a-select-option value="default">默认排序</a-select-option>
              <a-select-option value="time">按创建时间排序</a-select-option>
              <a-select-option value="status">按房间状态排序</a-select-option>
              <a-select-option value="creator">自己创建的优先</a-select-option>
            </a-select>
          </div>
          <div v-if="sortedJoinedList.length === 0" class="empty-tip">暂无参与的演讲</div>
          <div v-for="item in sortedJoinedList" :key="item.id">
            <div class="custom-room-card">
              <div class="card-top-gradient">
                <a-tag v-if="item.status===1" color="green" class="status-tag">进行中</a-tag>
                <a-tag v-else color="orange" class="status-tag">等待开始</a-tag>
                <span class="room-id">ID: {{ item.id }}</span>
              </div>
              <div class="card-main">
                <div class="room-title">{{ item.name }}</div>
                <div class="room-desc">{{ item.desc || '暂无描述' }}</div>
                <div class="room-info-row">
                  <span class="info-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#888" d="M12 12c2.7 0 8 1.34 8 4v2H4v-2c0-2.66 5.3-4 8-4zm0-2a4 4 0 1 1 0-8 4 4 0 0 1 0 8z"/></svg></span>
                  <span class="info-text">{{ item.participants }}人参与</span>
                  <span class="info-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#888" d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zm0-13H5V6h14v1z"/></svg></span>
                  <span class="info-text">{{ formatTime(item.time) }}</span>
                </div>
              </div>
              <div class="card-actions-row">
                <a-button type="link" size="small" class="action-btn">
                  <span class="btn-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#1677ff" d="M10 17l6-5-6-5v10z"/></svg></span>进入房间
                </a-button>
                <a-button type="link" size="small" class="action-btn" @click="() => showRoomDetail(item)">
                  <span class="btn-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#1677ff" d="M12 20c4.41 0 8-3.59 8-8s-3.59-8-8-8-8 3.59-8 8 3.59 8 8 8zm0-14c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6 2.69-6 6-6zm-1 9h2v2h-2zm0-8h2v6h-2z"/></svg></span>查看详情
                </a-button>
                <a-button type="link" size="small" class="action-btn" @click="() => copyInvite(item.invite)">
                  <span class="btn-icon"><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#1677ff" d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg></span>复制邀请码
                </a-button>
              </div>
            </div>
          </div>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- 底部导航栏 -->
    <div class="mobile-bottom-bar">
      <div :class="['bottom-tab', activeBottom==='home' ? 'active' : '']" @click="handleBottomTab('home')">首页</div>
      <div :class="['bottom-tab', activeBottom==='mine' ? 'active' : '']" @click="handleBottomTab('mine')">我的</div>
    </div>

    <a-modal v-model:visible="detailModalVisible" title="房间详情" width="520px" :footer="null">
      <template #title>
        <span>房间详情</span>
      </template>
      <div v-if="currentRoomDetail">
        <div class="room-detail-title-row">
          <span class="room-detail-title">{{ currentRoomDetail.name }}</span>
          <a-tag v-if="currentRoomDetail.status===2" color="#d9d9d9">已结束</a-tag>
          <a-tag v-else-if="currentRoomDetail.status===1" color="green">进行中</a-tag>
          <a-tag v-else color="orange">等待开始</a-tag>
        </div>
        <a-table :dataSource="detailTableData" :pagination="false" :showHeader="false" class="room-detail-table">
          <a-table-column v-for="col in detailTableColumns" :key="col.key" :dataIndex="col.dataIndex" :width="col.width" />
        </a-table>
        <div class="room-detail-btn-row">
          <a-button type="primary" @click="enterRoom(currentRoomDetail)"><template #icon><svg width="16" height="16" viewBox="0 0 24 24"><path fill="#fff" d="M10 17l6-5-6-5v10z"/></svg></template>进入房间</a-button>
          <a-button @click="detailModalVisible=false">关闭</a-button>
        </div>
      </div>
    </a-modal>

    <a-modal v-model:visible="inviteModalVisible" title="发送邀请" :footer="null">
      <a-form @submit.prevent="handleInviteSubmit">
        <a-form-item label="被邀请用户名">
          <a-input v-model:value="inviteForm.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="房间">
          <a-select v-model:value="inviteForm.roomId" style="width: 100%">
            <a-select-option v-for="room in createdList" :key="room.id" :value="room.id">{{ room.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="邀请角色">
          <a-select v-model:value="inviteForm.role" style="width: 100%">
            <a-select-option :value="0">听众</a-select-option>
            <a-select-option :value="1">演讲者</a-select-option>
          </a-select>
        </a-form-item>
        <div style="text-align:right;">
          <a-button @click="inviteModalVisible=false" style="margin-right:8px;">取消</a-button>
          <a-button type="primary" @click="handleInviteSubmit">发送邀请</a-button>
        </div>
      </a-form>
    </a-modal>

    <a-modal v-model:visible="invitationModalVisible" title="被邀请情况" width="600px" :footer="null">
      <div class="invitation-modal-header">
        <span></span>
        <a-select v-model:value="invitationSortType" size="small" style="width: 120px;" class="invitation-sort-select">
          <a-select-option value="time">时间排序</a-select-option>
          <a-select-option value="status">状态排序</a-select-option>
        </a-select>
      </div>
      <div v-if="sortedInvitationList.length === 0" style="text-align:center;color:#888;padding:32px 0;">暂无被邀请记录</div>
      <div v-else>
        <div v-for="item in sortedInvitationList" :key="item.id" class="invitation-card">
          <div class="invitation-card-header">
            <a-tag v-if="item.status===0" color="#faad14">待接受</a-tag>
            <a-tag v-else-if="item.status===1" color="#52c41a">已接受</a-tag>
            <a-tag v-else color="#d9d9d9">已拒绝</a-tag>
          </div>
          <div class="invitation-card-main">
            <div class="invitation-title">{{ item.room_name }}（{{ item.role===1 ? '演讲者' : '听众' }}）</div>
            <div class="invitation-time">邀请时间：{{ formatTimeYMDHM(item.invited_time) }}</div>
          </div>
          <div class="invitation-card-actions">
            <a-button v-if="item.status===0" type="primary" size="small" style="margin-right:8px;" :loading="invitationActionLoading[item.id]" @click="acceptInvitation(item)">接受</a-button>
            <a-button v-if="item.status===0" type="default" size="small" style="margin-right:8px;" :loading="invitationActionLoading[item.id]" @click="rejectInvitation(item)">拒绝</a-button>
            <a-button type="link" size="small" @click="showInvitationDetail(item)">查看详情</a-button>
          </div>
        </div>
      </div>
    </a-modal>
    <a-modal v-model:visible="invitationDetailVisible" title="邀请详情" width="600px" :footer="null">
      <div v-if="invitationDetail">
        <div class="invitation-detail-title-row">
          <span class="invitation-detail-title">{{ invitationDetail.room_name }}</span>
          <a-tag v-if="invitationDetail.status===0" color="#faad14">待接受</a-tag>
          <a-tag v-else-if="invitationDetail.status===1" color="#52c41a">已接受</a-tag>
          <a-tag v-else color="#d9d9d9">已拒绝</a-tag>
        </div>
        <a-table :dataSource="invitationDetailTableData" :pagination="false" :showHeader="false" class="invitation-detail-table">
          <a-table-column v-for="col in invitationDetailTableColumns" :key="col.key" :dataIndex="col.dataIndex" :width="col.width" />
        </a-table>
        <div class="invitation-detail-btn-row">
          <a-button v-if="invitationDetail.status===0" type="primary" :loading="invitationActionLoading[invitationDetail.id]" @click="acceptInvitation()">接受邀请</a-button>
          <a-button v-if="invitationDetail.status===0" :loading="invitationActionLoading[invitationDetail.id]" @click="rejectInvitation()">拒绝邀请</a-button>
          <a-button @click="invitationDetailVisible=false">关闭</a-button>
        </div>
      </div>
    </a-modal>

    <a-modal v-model:visible="joinRoomModalVisible" title="加入演讲" :footer="null">
      <a-form @submit.prevent="handleJoinRoom">
        <a-form-item label="邀请码" required>
          <a-input v-model:value="joinRoomInviteCode" placeholder="请输入邀请码" />
        </a-form-item>
        <div style="text-align:right;">
          <a-button @click="joinRoomModalVisible=false" style="margin-right:8px;">Cancel</a-button>
          <a-button type="primary" @click="handleJoinRoom">OK</a-button>
        </div>
      </a-form>
    </a-modal>

    <a-modal v-model:visible="createRoomModalVisible" title="创建新演讲" :footer="null">
      <a-form @submit.prevent="handleCreateRoom">
        <a-form-item label="演讲标题" required>
          <a-input v-model:value="createRoomForm.name" placeholder="请输入演讲标题" />
        </a-form-item>
        <a-form-item label="演讲描述">
          <a-textarea v-model:value="createRoomForm.description" placeholder="请输入演讲描述" rows="4" />
        </a-form-item>
        <a-form-item>
          <a-checkbox v-model:checked="createRoomForm.isSpeaker">我担任本次演讲的演讲人</a-checkbox>
        </a-form-item>
        <div style="text-align:right;">
          <a-button @click="createRoomModalVisible=false" style="margin-right:8px;">Cancel</a-button>
          <a-button type="primary" @click="handleCreateRoom">OK</a-button>
        </div>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>

import { ref, h, onMounted, watch, computed } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { userAPI } from '@/api'
import { invitationAPI } from '@/api'
import { speechRoomAPI } from '@/api'

const createdList = ref([])
const endedList = ref([])
const joinedList = ref([])
const activeTab = ref('created')
const activeBottom = ref('home')



const detailModalVisible = ref(false)
const currentRoomDetail = ref(null)

const sortType = ref(localStorage.getItem('popquiz_joined_sortType') || 'default')
const createdSortType = ref(localStorage.getItem('popquiz_created_sortType') || 'default')
const endedSortType = ref(localStorage.getItem('popquiz_ended_sortType') || 'default')
const userId = localStorage.getItem('userId') || localStorage.getItem('userid') || localStorage.getItem('username')

function saveSortType(val) {
  localStorage.setItem('popquiz_joined_sortType', val)
}
function saveCreatedSortType(val) {
  localStorage.setItem('popquiz_created_sortType', val)
}
function saveEndedSortType(val) {
  localStorage.setItem('popquiz_ended_sortType', val)
}

const sortedCreatedList = computed(() => {
  let arr = [...createdList.value]
  if (createdSortType.value === 'default') {
    arr.sort((a, b) => a.id - b.id)
  } else if (createdSortType.value === 'time') {
    arr.sort((a, b) => new Date(b.time) - new Date(a.time))
  } else if (createdSortType.value === 'status') {
    // 进行中(status===1)在前，等待开始(0)其次，已结束(2)最后
    arr.sort((a, b) => {
      const statusOrder = {1: 0, 0: 1, 2: 2}
      return statusOrder[a.status] - statusOrder[b.status]
    })
  } else if (createdSortType.value === 'creator') {
    arr.sort((a, b) => {
      const aSelf = a.creator_id == userId ? -1 : 1
      const bSelf = b.creator_id == userId ? -1 : 1
      return aSelf - bSelf
    })
  }
  return arr
})

const sortedEndedList = computed(() => {
  let arr = [...endedList.value]
  if (endedSortType.value === 'default') {
    arr.sort((a, b) => a.id - b.id)
  } else if (endedSortType.value === 'time') {
    arr.sort((a, b) => new Date(b.time) - new Date(a.time))
  } else if (endedSortType.value === 'status') {
    // 进行中(status===1)在前，等待开始(0)其次，已结束(2)最后
    arr.sort((a, b) => {
      const statusOrder = {1: 0, 0: 1, 2: 2}
      return statusOrder[a.status] - statusOrder[b.status]
    })
  } else if (endedSortType.value === 'creator') {
    arr.sort((a, b) => {
      const aSelf = a.creator_id == userId ? -1 : 1
      const bSelf = b.creator_id == userId ? -1 : 1
      return aSelf - bSelf
    })
  }
  return arr
})

const sortedJoinedList = computed(() => {
  let arr = [...joinedList.value]
  if (sortType.value === 'default') {
    arr.sort((a, b) => a.id - b.id)
  } else if (sortType.value === 'time') {
    arr.sort((a, b) => new Date(b.time) - new Date(a.time))
  } else if (sortType.value === 'status') {
    // 进行中(status===1)在前，等待开始(0)其次，已结束(2)最后
    arr.sort((a, b) => {
      const statusOrder = {1: 0, 0: 1, 2: 2}
      return statusOrder[a.status] - statusOrder[b.status]
    })
  } else if (sortType.value === 'creator') {
    arr.sort((a, b) => {
      const aSelf = a.creator_id == userId ? -1 : 1
      const bSelf = b.creator_id == userId ? -1 : 1
      return aSelf - bSelf
    })
  }
  return arr
})

// 获取我创建的演讲室
async function fetchCreatedRooms() {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const res = await userAPI.getUserCreatedRooms(token)
    if (res.data && Array.isArray(res.data.rooms)) {
      createdList.value = res.data.rooms.map(room => ({
        id: room.id,
        name: room.name,
        desc: room.description,
        status: room.status,
        participants: room.role,
        time: room.created_at ? room.created_at.replace('T', ' ').replace('Z', '') : '',
        invite: room.invite_code,
        speaker_invite_code: room.speaker_invite_code,
        creator_id: room.creator_id,
        speaker_id: room.speaker_id,
        role: room.role
      }))
    } else {
      createdList.value = []
    }
  } catch (e) {
    message.error('获取我创建的演讲失败')
    createdList.value = []
  }
}

// 获取我参与的演讲室
async function fetchJoinedRooms() {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const res = await userAPI.getUserSpeechRooms(token)
    if (res.data && Array.isArray(res.data.rooms)) {
      joinedList.value = res.data.rooms.map(room => ({
        id: room.id,
        name: room.name,
        desc: room.description,
        status: room.status,
        participants: room.role,
        time: room.created_at ? room.created_at.replace('T', ' ').replace('Z', '') : '',
        invite: room.invite_code,
        speaker_invite_code: room.speaker_invite_code, // 保证详情弹窗可用
        creator_id: room.creator_id,
        speaker_id: room.speaker_id,
        role: room.role
      }))
    } else {
      joinedList.value = []
    }
  } catch (e) {
    message.error('获取我参与的演讲失败')
    joinedList.value = []
  }
}

// 获取已结束的演讲室
async function fetchEndedRooms() {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    // 假设有 userAPI.getUserEndedRooms
    const res = await userAPI.getUserEndedRooms(token)
    if (res.data && Array.isArray(res.data.rooms)) {
      endedList.value = res.data.rooms.map(room => ({
        id: room.id,
        name: room.name,
        desc: room.description,
        status: room.status,
        participants: room.role,
        time: room.created_at ? room.created_at.replace('T', ' ').replace('Z', '') : '',
        invite: room.invite_code,
        speaker_invite_code: room.speaker_invite_code,
        creator_id: room.creator_id,
        speaker_id: room.speaker_id,
        role: room.role
      }))
    } else {
      endedList.value = []
    }
  } catch (e) {
    message.error('获取已结束的演讲失败')
    endedList.value = []
  }
}

onMounted(() => {
  // 读取本地tab记忆
  const savedTab = localStorage.getItem('popquiz_home_activeTab')
  if (savedTab && ['created','ended','joined'].includes(savedTab)) {
    activeTab.value = savedTab
  }
  if (activeTab.value === 'created') fetchCreatedRooms()
  if (activeTab.value === 'ended') fetchEndedRooms()
  if (activeTab.value === 'joined') fetchJoinedRooms()
})
watch(activeTab, (tab) => {
  localStorage.setItem('popquiz_home_activeTab', tab)
  if (tab === 'created') fetchCreatedRooms()
  if (tab === 'ended') fetchEndedRooms()
  if (tab === 'joined') fetchJoinedRooms()
})



// 操作按钮逻辑
const quickBtns = [
  { text: '创建新演讲', icon: `<svg width='20' height='20' viewBox='0 0 24 24'><path fill='#fff' d='M19 11h-6V5h-2v6H5v2h6v6h2v-6h6z'/></svg>` },
  { text: '加入新演讲', icon: `<svg width='20' height='20' viewBox='0 0 24 24'><path fill='#fff' d='M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z'/></svg>` },
  { text: '发送邀请', icon: `<svg width='20' height='20' viewBox='0 0 24 24'><path fill='#fff' d='M21 6.5a.5.5 0 0 0-.5-.5H7.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L7.707 7H20.5a.5.5 0 0 0 .5-.5z'/></svg>` },
  { text: '被邀请情况', icon: `<svg width='20' height='20' viewBox='0 0 24 24'><path fill='#fff' d='M12 12c2.7 0 8 1.34 8 4v2H4v-2c0-2.66 5.3-4 8-4zm0-2a4 4 0 1 1 0-8 4 4 0 0 1 0 8z'/></svg>` },
]
const activeBtnIndex = ref(-1)
function handleQuickBtn(idx) {
  activeBtnIndex.value = idx
  setTimeout(() => {
    activeBtnIndex.value = -1
  }, 300)
  if (quickBtns[idx].text === '创建新演讲') {
    console.log('弹窗应弹出')
    createRoomForm.value = { name: '', description: '', isSpeaker: false }
    createRoomModalVisible.value = true
  }
  if (quickBtns[idx].text === '加入新演讲') {
    joinRoomInviteCode.value = ''
    joinRoomModalVisible.value = true
  }
  if (quickBtns[idx].text === '发送邀请') {
    showInviteModalGlobal()
  }
  if (quickBtns[idx].text === '被邀请情况') {
    fetchInvitations()
  }
  // 其他按钮逻辑...
}
async function handleCreateRoom() {
  console.log('handleCreateRoom', createRoomForm.value)
  if (!createRoomForm.value.name) {
    message.error('请输入演讲标题')
    return
  }
  const session_token = localStorage.getItem('token')
  try {
    await speechRoomAPI.createSpeechRoom({
      name: createRoomForm.value.name,
      description: createRoomForm.value.description,
      session_token,
      is_speaker: !!createRoomForm.value.isSpeaker
    })
    message.success('演讲创建成功')
    createRoomModalVisible.value = false
    fetchCreatedRooms && fetchCreatedRooms()
  } catch (e) {
    message.error(e?.response?.data?.message || '创建失败')
  }
}
async function handleJoinRoom() {
  const token = localStorage.getItem('token')
  if (!joinRoomInviteCode.value) {
    message.error('请输入邀请码')
    return
  }
  try {
    await speechRoomAPI.joinRoom({ token, invite_code: joinRoomInviteCode.value })
    message.success('加入成功')
    joinRoomModalVisible.value = false
    // 可选：刷新房间列表
    fetchJoinedRooms && fetchJoinedRooms()
  } catch (e) {
    message.error(e?.response?.data?.message || '加入失败')
  }
}

// Tab标签自定义，数量标签放在“我参与的演讲”后面
const joinedTabLabel = h('span', { class: 'tab-label-wrap' }, [
  '我参与的演讲',
  h('span', { class: 'tab-count-badge' }, `共${joinedList.value.length}个`)
])

// 卡片组件
const PresentationCard = {
  props: ['item'],
  setup(props) {
    const copy = () => {
      navigator.clipboard.writeText(props.item.invite)
      message.success('邀请码已复制')
    }
    return { copy }
  },
  template: `
    <a-card class="presentation-card" :bordered="true">
      <div class="card-header">
        <span class="card-title">{{ item.name }}</span>
        <a-tag v-if="item.status===1" color="green">进行中</a-tag>
        <a-tag v-else color="orange">等待开始</a-tag>
      </div>
      <div class="card-desc">{{ item.desc }}</div>
      <div class="card-info">
        <span>{{ item.participants }}人参与</span>
        <span>{{ item.time }}</span>
      </div>
      <div class="card-actions">
        <a-button type="link" size="small">进入房间</a-button>
        <a-button type="link" size="small">查看详情</a-button>
        <a-button type="link" size="small">演讲者邀请码</a-button>
        <a-button type="link" size="small" @click="copy">复制邀请码</a-button>
      </div>
    </a-card>
  `
}




function formatTime(timeStr) {
  if (!timeStr) return ''
  // 假设timeStr为 '2025-07-12 15:35:00' 或 '2025-07-12 15:35'
  const d = new Date(timeStr.replace(/-/g, '/'))
  if (isNaN(d.getTime())) return timeStr
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日 ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`
}
function copyInvite(invite) {
  if (!invite) return
  navigator.clipboard.writeText(invite)
  message.success('邀请码已复制')
}

function showRoomDetail(room) {
  currentRoomDetail.value = room
  detailModalVisible.value = true
}

function copyText(text) {
  if (!text) return
  navigator.clipboard.writeText(text)
  message.success('已复制')
}

function enterRoom(room) {
  // 这里预留跳转逻辑
  message.info('进入房间功能待实现')
}

const detailTableColumns = [
  { key: 'label', dataIndex: 'label', width: '120px' },
  { key: 'value', dataIndex: 'value' }
]
const detailTableData = computed(() => {
  if (!currentRoomDetail.value) return []
  const isOrganizer = currentRoomDetail.value.creator_id === currentRoomDetail.value.speaker_id
  return [
    { label: '房间ID', value: currentRoomDetail.value.id },
    { label: '听众邀请码', value: h('span', {}, [
      currentRoomDetail.value.invite || '-',
      h('a', { style: 'margin-left:8px;color:#1677ff;cursor:pointer;', onClick: () => copyText(currentRoomDetail.value.invite) }, '复制')
    ]) },
    { label: '演讲者邀请码', value: h('span', {}, [
      currentRoomDetail.value.speaker_invite_code || '-',
      h('a', { style: 'margin-left:8px;color:#1677ff;cursor:pointer;', onClick: () => copyText(currentRoomDetail.value.speaker_invite_code) }, '复制')
    ]) },
    { label: '演讲描述', value: currentRoomDetail.value.desc || '-' },
    { label: '创建时间', value: formatTime(currentRoomDetail.value.time) },
    { label: '组织者', value: h('span', { style: 'font-weight:600;color:#1677ff;' }, 'user') },
    { label: '演讲者', value: h('span', {}, [
      h('span', { style: 'font-weight:600;color:#222;' }, 'user'),
      isOrganizer ? h('span', { style: 'margin-left:8px;background:#eaf3ff;color:#1677ff;border-radius:8px;padding:2px 8px;font-size:13px;font-weight:600;display:inline-block;' }, '组织者') : null
    ]) },
    { label: '参与数量', value: (currentRoomDetail.value.participants || currentRoomDetail.value.role || 0) + '人' }
  ]
})


const router = useRouter()
function handleBottomTab(tab) {
  activeBottom.value = tab
  if(tab === 'mine') {
    router.push('/profile')
  } else if(tab === 'home') {
    router.push('/')
  }
}


// 3. showInviteModalGlobal 弹窗内容为用户名、房间、角色
const inviteModalVisible = ref(false)
const inviteForm = ref({ username: '', role: 0, roomId: null })
const allRooms = computed(() => {
  // 合并你创建和你参与的房间，去重
  const map = new Map()
  createdList.value.forEach(r => map.set(r.id, r))
  joinedList.value.forEach(r => map.set(r.id, r))
  return Array.from(map.values())
})
function showInviteModalGlobal() {
  inviteForm.value.username = ''
  inviteForm.value.role = 0
  inviteForm.value.roomId = createdList.value.length ? createdList.value[0].id : null
  inviteModalVisible.value = true
}
async function handleInviteSubmit() {
  const token = localStorage.getItem('token')
  if (!inviteForm.value.username) {
    message.error('请输入用户名')
    return
  }
  if (!inviteForm.value.roomId) {
    message.error('请选择房间')
    return
  }
  try {
    await invitationAPI.inviteUser({
      token,
      invitee_username: inviteForm.value.username,
      room_id: inviteForm.value.roomId,
      role: inviteForm.value.role
    })
    message.success('邀请已发送')
    inviteModalVisible.value = false
  } catch (e) {
    message.error(e?.response?.data?.message || '邀请失败')
  }
}

// 2. 获取被邀请信息并弹窗展示
const invitationModalVisible = ref(false)
const invitationList = ref([])
async function fetchInvitations() {
  const token = localStorage.getItem('token')
  try {
    const res = await userAPI.getUserInvitations(token)
    if (res.data && Array.isArray(res.data.invitations)) {
      invitationList.value = res.data.invitations
      invitationModalVisible.value = true
    } else {
      invitationList.value = []
      invitationModalVisible.value = true
    }
  } catch (e) {
    message.error(e?.response?.data?.message || '获取被邀请信息失败')
    invitationList.value = []
    invitationModalVisible.value = true
  }
}
function formatTimeYMDHM(timeStr) {
  if (!timeStr) return ''
  // 兼容Z结尾的UTC时间，转为本地时间
  let d = timeStr.endsWith('Z') ? new Date(Date.parse(timeStr)) : new Date(timeStr.replace(/-/g, '/'))
  if (isNaN(d.getTime())) return timeStr
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日 ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`
}
const invitationDetailVisible = ref(false)
const invitationDetail = ref(null)
function showInvitationDetail(item) {
  invitationDetail.value = item
  invitationDetailVisible.value = true
}
const invitationDetailTableColumns = [
  { key: 'label', dataIndex: 'label', width: '120px' },
  { key: 'value', dataIndex: 'value' }
]
const invitationDetailTableData = computed(() => {
  if (!invitationDetail.value) return []
  return [
    { label: '房间名称', value: invitationDetail.value.room_name },
    { label: '演讲室描述', value: invitationDetail.value.description || '-' },
    { label: '演讲室创建时间', value: formatTimeYMDHM(invitationDetail.value.created_at) },
    { label: '组织者', value: h('span', { style: 'font-weight:600;color:#1677ff;' }, invitationDetail.value.creator_name || '-') },
    { label: '演讲者', value: invitationDetail.value.speaker_name || '-' },
    { label: '参与人数', value: (invitationDetail.value.total_participants || 0) + '人' },
    { label: '邀请角色', value: h('span', { style: 'background:#eaf3ff;color:#1677ff;border-radius:8px;padding:2px 8px;font-size:13px;font-weight:600;display:inline-block;' }, invitationDetail.value.role===1 ? '演讲者' : '听众') },
    { label: '房间状态', value: invitationDetail.value.room_status===1 ? '进行中' : (invitationDetail.value.room_status===2 ? '已结束' : '等待开始') },
    { label: '邀请时间', value: formatTimeYMDHM(invitationDetail.value.invited_time) }
  ]
})
const invitationActionLoading = ref({})
async function acceptInvitation(item) {
  const id = item?.id || invitationDetail.value?.id
  if (!id) return
  invitationActionLoading.value[id] = true
  try {
    const token = localStorage.getItem('token')
    await invitationAPI.acceptInvitation({ id, token })
    message.success('已接受邀请')
    invitationActionLoading.value[id] = false
    fetchInvitations()
    invitationDetailVisible.value = false
  } catch (e) {
    message.error(e?.response?.data?.message || '操作失败')
    invitationActionLoading.value[id] = false
  }
}
async function rejectInvitation(item) {
  const id = item?.id || invitationDetail.value?.id
  if (!id) return
  invitationActionLoading.value[id] = true
  try {
    const token = localStorage.getItem('token')
    await invitationAPI.rejectInvitation({ id, token })
    message.success('已拒绝邀请')
    invitationActionLoading.value[id] = false
    fetchInvitations()
    invitationDetailVisible.value = false
  } catch (e) {
    message.error(e?.response?.data?.message || '操作失败')
    invitationActionLoading.value[id] = false
  }
}

const invitationSortType = ref('time')
const sortedInvitationList = computed(() => {
  let arr = [...invitationList.value]
  if (invitationSortType.value === 'time') {
    arr.sort((a, b) => new Date(b.invited_time) - new Date(a.invited_time))
  } else if (invitationSortType.value === 'status') {
    // 待接受(0)在前，已接受(1)，已拒绝(2)
    arr.sort((a, b) => a.status - b.status)
  }
  return arr
})

const joinRoomModalVisible = ref(false)
const joinRoomInviteCode = ref('')


</script>

<style scoped>
.mobile-home {
  max-width: 480px;
  margin: 0 auto;
  padding-bottom: 60px;
  background: #f7f8fa;
  min-height: 100vh;
}
.top-info-card {
  margin: 16px 8px 8px 8px;
  border-radius: 12px;
  text-align: center;
  font-size: 16px;
}
.top-title {
  font-size: 22px;
  font-weight: bold;
  color: #1677ff;
  margin-bottom: 4px;
}
.top-desc {
  color: #333;
  margin-bottom: 8px;
}
.top-stars {
  margin: 8px 0 0 0;
}
.quick-btn-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin: 28px 16px 20px 16px;
  background: #f4f8ff;
  border-radius: 28px;
  box-shadow: 0 6px 24px rgba(22,119,255,0.10);
  padding: 24px 16px 16px 16px;
}
.quick-btn-item {
  display: flex;
  justify-content: center;
}
.quick-btn {
  font-size: 18px;
  font-weight: 700;
  border-radius: 18px;
  height: 52px;
  background: linear-gradient(90deg, #1677ff 0%, #7f53ff 100%);
  color: #fff !important;
  border: none;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 16px rgba(22,119,255,0.10);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  width: 100%;
  min-width: 120px;
  max-width: 210px;
  box-sizing: border-box;
}
.quick-btn:hover, .quick-btn:focus, .quick-btn-active {
  background: linear-gradient(90deg, #0958d9 0%, #7f53ff 100%) !important;
  color: #fff !important;
  box-shadow: 0 6px 24px rgba(22,119,255,0.18);
}
.quick-btn-icon {
  display: inline-flex;
  align-items: center;
  margin-right: 8px;
  vertical-align: middle;
  filter: invert(34%) sepia(97%) saturate(747%) hue-rotate(186deg) brightness(97%) contrast(101%);
}
.quick-btn-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
  vertical-align: middle;
}
.tabs-with-count {
  position: relative;
}
.tab-count-bar {
  margin: 0 0 12px 0;
  padding: 8px 0 8px 16px;
  font-size: 16px;
  font-weight: bold;
  color: #1677ff;
  background: #f4f8ff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(22,119,255,0.06);
}
.mobile-tabs {
  margin-bottom: 32px;
}
.mobile-tabs {
  margin: 8px 0 8px 0;
  background: #fff;
  --ant-tabs-tab-font-size: 16px;
  --ant-tabs-tab-padding: 10px 0;
}
.mobile-tabs :deep(.ant-tabs-nav) {
  justify-content: space-around !important;
}
.mobile-tabs :deep(.ant-tabs-tab) {
  flex: 1 1 0;
  text-align: center;
  font-size: 16px;
  padding: 10px 0 !important;
  margin: 0 4px !important;
  min-width: 0;
}
.mobile-tabs :deep(.ant-tabs-tab-active) {
  font-weight: bold;
  color: #1677ff;
}
.mobile-tabs :deep(.ant-tabs-ink-bar) {
  height: 3px;
  border-radius: 2px;
  background: #1677ff;
}
.presentation-card {
  margin: 8px 8px 0 8px;
  border-radius: 10px;
  font-size: 15px;
}
.card-header {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 2px;
}
.card-title {
  flex: 1;
}
.card-desc {
  color: #666;
  margin-bottom: 2px;
  font-size: 14px;
}
.card-info {
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 13px;
  margin-bottom: 4px;
}
.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
}
.card-actions .ant-btn {
  padding: 0 4px;
  font-size: 13px;
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
.empty-tip {
  text-align: center;
  color: #888;
  padding: 20px 0;
  font-size: 16px;
}
.custom-room-card {
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(127, 83, 255, 0.08);
  background: #fff;
  margin: 18px 8px 0 8px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
}
.card-top-gradient {
  background: linear-gradient(90deg, #7f53ff 0%, #1677ff 100%);
  padding: 12px 18px 8px 18px;
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.status-tag {
  position: absolute;
  left: 18px;
  top: 12px;
  z-index: 2;
}
.room-id {
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  margin-left: auto;
  z-index: 2;
}
.card-main {
  padding: 18px 18px 8px 18px;
  background: #fff;
}
.room-title {
  font-size: 18px;
  font-weight: bold;
  color: #222;
  margin-bottom: 4px;
}
.room-desc {
  color: #666;
  font-size: 15px;
  margin-bottom: 10px;
}
.room-info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #888;
  font-size: 14px;
  margin-bottom: 2px;
}
.info-icon {
  display: flex;
  align-items: center;
  margin-right: 2px;
}
.info-text {
  margin-right: 12px;
}
.card-actions-row {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 8px;
  border-top: 1px solid #f0f0f0;
  padding: 10px 18px 10px 18px;
  background: #fafbff;
}
.action-btn {
  color: #1677ff !important;
  font-weight: 500;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0 6px;
}
.btn-icon {
  display: inline-flex;
  align-items: center;
  margin-right: 2px;
}
.room-detail-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.room-detail-title {
  font-size: 22px;
  font-weight: bold;
  color: #1677ff;
}
.room-detail-table {
  margin-bottom: 18px;
  border-radius: 14px;
  overflow: hidden;
  background: #f7faff;
  box-shadow: 0 2px 12px rgba(22,119,255,0.06);
}
.room-detail-btn-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 18px;
}
.room-detail-table :deep(.ant-table-cell) {
  font-size: 16px;
  padding: 12px 8px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
}
.room-detail-table :deep(.ant-table-row:last-child .ant-table-cell) {
  border-bottom: none;
}
.room-detail-table :deep(.ant-table-tbody) {
  background: #fff;
}
.room-detail-table :deep(.ant-table) {
  border-radius: 14px;
  overflow: hidden;
}
.room-detail-btn-row .ant-btn-primary {
  background: #1677ff;
  border-radius: 8px;
  font-weight: 600;
  border: none;
}
.room-detail-btn-row .ant-btn {
  border-radius: 8px;
  font-weight: 500;
}
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.sort-select {
  min-width: 140px;
  border-radius: 8px !important;
  border: 1.5px solid #1677ff !important;
  background: #f7faff !important;
  color: #1677ff !important;
  font-weight: 600;
}
.sort-select :deep(.ant-select-selector) {
  border-radius: 8px !important;
  background: #f7faff !important;
  color: #1677ff !important;
  font-weight: 600;
  border: none !important;
  box-shadow: none !important;
}
.sort-select-dropdown {
  border-radius: 10px !important;
  background: #fff !important;
  box-shadow: 0 4px 16px rgba(22,119,255,0.10);
}
.sort-select-dropdown .ant-select-item {
  color: #1677ff !important;
  font-weight: 500;
  border-radius: 6px;
  margin: 2px 0;
}
.sort-select-dropdown .ant-select-item-option-selected {
  background: #eaf3ff !important;
  color: #1677ff !important;
}
.sort-select-dropdown .ant-select-item-option-active {
  background: #f0f7ff !important;
  color: #1677ff !important;
}
.invitation-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(22,119,255,0.06);
  margin-bottom: 18px;
  padding: 18px 20px 12px 20px;
  border: 1.5px solid #eaf3ff;
}
.invitation-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
.invitation-title {
  font-size: 18px;
  font-weight: 600;
  color: #1677ff;
  margin-bottom: 4px;
}
.invitation-time {
  color: #888;
  font-size: 14px;
  margin-bottom: 8px;
}
.invitation-card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.invitation-detail-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.invitation-detail-title {
  font-size: 22px;
  font-weight: bold;
  color: #1677ff;
}
.invitation-detail-table {
  margin-bottom: 18px;
  border-radius: 14px;
  overflow: hidden;
  background: #f7faff;
  box-shadow: 0 2px 12px rgba(22,119,255,0.06);
}
.invitation-detail-btn-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 18px;
}
.invitation-detail-table :deep(.ant-table-cell) {
  font-size: 16px;
  padding: 12px 8px;
  border-bottom: 1px solid #f0f0f0;
}
.invitation-detail-table :deep(.ant-table-row:last-child .ant-table-cell) {
  border-bottom: none;
}
.invitation-detail-table :deep(.ant-table-tbody) {
  background: #fff;
}
.invitation-detail-table :deep(.ant-table) {
  border-radius: 14px;
  overflow: hidden;
}
.invitation-detail-btn-row .ant-btn-primary {
  background: #1677ff;
  border-radius: 8px;
  font-weight: 600;
  border: none;
}
.invitation-detail-btn-row .ant-btn {
  border-radius: 8px;
  font-weight: 500;
}
.invitation-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.invitation-sort-select {
  border-radius: 8px;
}
</style> 