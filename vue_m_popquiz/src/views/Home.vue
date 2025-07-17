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
      <a-button
        v-for="(btn, idx) in quickBtns"
        :key="btn.text"
        type="primary"
        class="quick-btn"
        :class="{ 'quick-btn-active': activeBtnIndex === idx }"
        @click="handleQuickBtn(idx)"
      >
        {{ btn.text }}
      </a-button>
    </div>

    <!-- Tab切换及数量 -->
    <div class="tabs-with-count">
      <a-tabs v-model:activeKey="activeTab" class="mobile-tabs" tabBarGutter="0">
        <a-tab-pane key="created" tab="我创建的演讲">
          <div class="tab-count-bar">我创建的演讲共{{ createdList.length }}个</div>
          <div v-for="item in createdList" :key="item.id">
            <PresentationCard :item="item" />
          </div>
        </a-tab-pane>
        <a-tab-pane key="ended" tab="已结束的演讲">
          <div class="tab-count-bar">已结束的演讲共{{ endedList.length }}个</div>
          <div v-for="item in endedList" :key="item.id">
            <PresentationCard :item="item" />
          </div>
        </a-tab-pane>
        <a-tab-pane key="joined" tab="我参与的演讲">
          <div class="tab-count-bar">我参与的演讲共{{ joinedList.length }}个</div>
          <div v-for="item in joinedList" :key="item.id">
            <PresentationCard :item="item" />
          </div>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- 底部导航栏 -->
    <div class="mobile-bottom-bar">
      <div :class="['bottom-tab', activeBottom==='home' ? 'active' : '']" @click="activeBottom='home'">首页</div>
      <div :class="['bottom-tab', activeBottom==='mine' ? 'active' : '']" @click="activeBottom='mine'">我的</div>
    </div>
  </div>
</template>

<script setup>
import { ref, h } from 'vue'
import { message } from 'ant-design-vue'

// mock数据
const createdList = ref([
  {
    id: 8,
    name: 'JavaScrip 介绍',
    desc: '介绍JS语言的基础知识',
    status: 1,
    participants: 2,
    time: '2025年7月12日 15:35',
    invite: 'ABCD1234',
  },
  {
    id: 10,
    name: 'PopQuiz 智能演讲互动平台',
    desc: '暂无描述',
    status: 0,
    participants: 2,
    time: '2025年7月12日 20:13',
    invite: 'EFGH5678',
  },
])
const endedList = ref([])
const joinedList = ref([
  {
    id: 21,
    name: '参与的课程1',
    desc: '参与课程简介',
    status: 1,
    participants: 3,
    time: '2025年8月1日 10:00',
    invite: 'JOIN1234',
  }
])
const activeTab = ref('created')
const activeBottom = ref('home')

// 操作按钮逻辑
const quickBtns = [
  { text: '创建新演讲' },
  { text: '加入新演讲' },
  { text: '发送邀请' },
  { text: '被邀请情况' },
]
const activeBtnIndex = ref(-1)
function handleQuickBtn(idx) {
  activeBtnIndex.value = idx
  setTimeout(() => {
    activeBtnIndex.value = -1
  }, 300)
  // 这里可以加具体业务逻辑
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
.quick-btn {
  font-size: 18px;
  font-weight: 600;
  border-radius: 16px;
  height: 48px;
  background: #1677ff;
  color: #fff;
  border: none;
  transition: background 0.2s;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.quick-btn:active,
.quick-btn:focus,
.quick-btn:hover,
.quick-btn-active {
  background: #0958d9 !important;
  color: #fff !important;
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
</style> 