<template>
  <div class="question-stats-bar-outer" :class="{ 'show-list': showList }">
    <div class="question-list-panel">
      <div class="question-list-header">题目列表</div>
      <div class="question-list-body">
        <div v-if="sortedQuestionList && sortedQuestionList.length" class="question-list-items">
          <div v-for="(item, idx) in sortedQuestionList" :key="item.id || idx" class="question-list-item" @click="handleSelectQuestion(item, idx)">
            <div class="question-info">
              <div class="question-status" :class="item.status === 0 ? 'ongoing' : 'ended'">
                {{ item.status === 0 ? '进行中' : '已结束' }}
              </div>
              <div class="question-list-title">{{ item.question }}</div>
            </div>
          </div>
        </div>
        <div v-else class="question-list-empty">暂无题目</div>
      </div>
    </div>
    <div class="question-stats-bar">
      <div class="question-title-row">
        <a-button type="link" class="back-btn" @click="handleBack">
          <svg viewBox="0 0 24 24" fill="none" width="14" height="14" style="vertical-align: middle;">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="back-text">返回</span>
        </a-button>
        <div class="title-row-spacer"></div>
        <span v-if="countdown" class="countdown-timer" :class="{ 'ended': countdown === '已结束' }">
          <svg class="timer-icon" viewBox="0 0 20 20" width="18" height="18">
            <circle cx="10" cy="10" r="8" :stroke="countdown === '已结束' ? '#b88600' : '#1677ff'" stroke-width="2" fill="none"/>
            <path d="M10 5v5l3 2" :stroke="countdown === '已结束' ? '#b88600' : '#1677ff'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
          {{ countdown }}
        </span>
      </div>
      <div class="main-content-scrollable">
        <div class="main-question-title">{{ question }}</div>
        <div class="options-content-list">
          <div v-for="(opt, idx) in options" :key="opt.label" :class="['option-content-item', opt.label === correctLabel ? 'correct' : '']">
            <span class="option-label">{{ opt.label }}.</span>
            <span class="option-text" ref="optionTextRefs" @mouseenter="showTooltip(idx, $event)" @mouseleave="hideTooltip">{{ opt.text }}</span>
          </div>
        </div>
        <div ref="chartRef" class="bar-chart"></div>
        <div class="stats-info">
          <span>未选择人数：{{ unselectedCount }}</span>
          <span>正确率：{{ (accuracy * 100).toFixed(1) }}%</span>
        </div>
        <transition name="tooltip-fade">
          <div v-if="tooltip.show" class="custom-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
            {{ tooltip.text }}
          </div>
        </transition>
        <div class="discussion-area">
          <div v-if="discussionMessages && discussionMessages.length" class="discussion-list">
            <div v-for="(msg, idx) in discussionMessages" :key="idx" class="discussion-msg-item">
              <span class="discussion-msg-user">{{ msg.username }}：</span>
              <span class="discussion-msg-text">{{ msg.message }}</span>
            </div>
          </div>
          <div v-else class="discussion-empty">暂无讨论</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  question: { type: String, required: true },
  options: { type: Array, required: true }, // [{ label: 'A', text: 'xxx', count: 10 }, ...]
  unselectedCount: { type: Number, required: true },
  accuracy: { type: Number, required: true }, // 0~1
  correctLabel: { type: String, required: true }, // 正确答案的label，如 'A'
  endTime: { type: [String, Number], required: false, default: null }, // 结束时间戳或ISO字符串
  questionList: { type: Array, required: false, default: () => [] }, // 新增题目列表
  discussionMessages: { type: Array, required: false, default: () => [] }
});

const chartRef = ref(null);
let chartInstance = null;

// --- tooltip相关 ---
const optionTextRefs = ref([]); // 存储每个option-text的DOM
const overflowed = ref([]); // 记录哪些选项溢出
const tooltip = ref({ show: false, text: '', x: 0, y: 0 });

const checkOverflow = () => {
  overflowed.value = props.options.map((_, idx) => {
    const el = optionTextRefs.value[idx];
    if (!el) return false;
    return el.scrollWidth > el.clientWidth;
  });
};

const showTooltip = (idx, event) => {
  if (!overflowed.value[idx]) return;
  const tooltipWidth = 260;
  const tooltipHeight = 48; // 预估高度，后续可动态获取
  const margin = 12;
  let x = event.clientX + 10;
  let y = event.clientY + 10;
  const winW = window.innerWidth;
  const winH = window.innerHeight;
  // 右侧溢出
  if (x + tooltipWidth + margin > winW) {
    x = winW - tooltipWidth - margin;
  }
  // 下方溢出
  if (y + tooltipHeight + margin > winH) {
    y = winH - tooltipHeight - margin;
  }
  tooltip.value = {
    show: true,
    text: props.options[idx].text,
    x,
    y
  };
};
const hideTooltip = () => {
  tooltip.value.show = false;
};

const renderChart = () => {
  if (!chartRef.value) return;
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  const option = {
    grid: { left: 25, right: 10, top: 2, bottom: 2 },
    xAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: {
        fontSize: 15,
        color: '#1557c0',
        fontWeight: 'bold',
        fontFamily: 'Segoe UI, Arial, sans-serif',
        shadowColor: '#e6f0ff',
        shadowBlur: 2
      },
      axisLine: {
        lineStyle: {
          color: '#b3d1ff',
          width: 2
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e6f0ff',
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: props.options.map(opt => opt.label),
      inverse: true,
      axisLabel: {
        fontSize: 15,
        color: '#1557c0',
        fontWeight: 'bold',
        fontFamily: 'Segoe UI, Arial, sans-serif',
        shadowColor: '#e6f0ff',
        shadowBlur: 2
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      }
    },
    series: [
      {
        type: 'bar',
        data: props.options.map(opt => ({
          value: opt.count,
          itemStyle: {
            color: opt.label === props.correctLabel ? '#52c41a' : '#1677ff',
            borderRadius: [4, 4, 4, 4]
          }
        })),
        barWidth: 22,
        label: {
          show: true,
          position: function(params) {
            return params.value === 0 ? 'right' : 'insideRight';
          },
          fontSize: 13,
          formatter: function(params) {
            return params.value;
          },
          offset: [4, 6]
        }
      }
    ]
  };
  chartInstance.setOption(option);
};

// 倒计时逻辑
const countdown = ref('');
let timer = null;
function updateCountdown() {
  if (!props.endTime) {
    countdown.value = '';
    return;
  }
  const end = new Date(props.endTime).getTime();
  const now = Date.now();
  let diff = Math.max(0, Math.floor((end - now) / 1000));
  if (diff > 0) {
    const min = String(Math.floor(diff / 60)).padStart(2, '0');
    const sec = String(diff % 60).padStart(2, '0');
    countdown.value = `${min}:${sec}`;
  } else {
    countdown.value = '已结束';
  }
}
const emit = defineEmits(['back', 'selectQuestion']);
const showList = ref(false);
function handleBack() {
  showList.value = true;
  setTimeout(() => {
    emit('back');
  }, 350); // 动画时长与css一致
}
function handleSelectQuestion(item, idx) {
  showList.value = false;
  emit('selectQuestion', item, idx);
}
const sortedQuestionList = computed(() => {
  if (!props.questionList) return [];
  return props.questionList.slice().sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
});
onMounted(() => {
  renderChart();
  nextTick(checkOverflow);
  if (props.endTime) {
    updateCountdown();
    timer = setInterval(updateCountdown, 1000);
  }
});
onUnmounted(() => {
  if (timer) clearInterval(timer);
});
watch(() => props.endTime, (val) => {
  if (timer) clearInterval(timer);
  if (val) {
    updateCountdown();
    timer = setInterval(updateCountdown, 1000);
  } else {
    countdown.value = '';
  }
});
</script>

<style scoped>
.question-stats-bar-outer {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #fafafa;
  border-radius: 8px;
  transition: background 0.2s;
  display: flex;
  flex-direction: row;
}
.question-list-panel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fff;
  z-index: 10;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.06);
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
  transform: translateX(-100%);
}
.show-list .question-list-panel {
  transform: translateX(0);
}
.question-stats-bar {
  width: 100%;
  background: #fff;
  border-radius: 14px;
  padding: 14px 16px 10px 16px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: box-shadow 0.2s, transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 20;
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  height: 100%;
  min-height: 0;
}
.show-list .question-stats-bar {
  transform: translateX(100%);
}
.question-list-panel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fff;
  z-index: 10;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.06);
  animation: slideInRight 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
.slide-right-enter-active, .slide-right-leave-active {
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-right-enter-from, .slide-right-leave-to {
  transform: translateX(100%);
}
.slide-right-enter-to, .slide-right-leave-from {
  transform: translateX(0);
}
.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 13px;
  padding: 0;
  height: auto;
  border: none;
  background: none;
}
.back-btn:hover {
  color: #1677ff;
}
.back-btn svg {
  transition: transform 0.2s ease;
  display: inline-block;
  vertical-align: middle;
}
.back-btn:hover svg {
  transform: translateX(-2px);
}
.back-text {
  display: inline-block;
  vertical-align: middle;
  line-height: 1;
}
.question-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
  border-bottom: 1px solid #e6f0ff;
  padding-bottom: 2px;
  min-height: 32px;
}
.title-row-spacer {
  flex: 1;
}
.question-title {
  font-size: 20px;
  font-weight: 800;
  color: #223354;
  background: #fff;
  padding: 0 2px;
  border-radius: 4px;
  flex: 1;
  line-height: 1.3;
}
.countdown-timer {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 16px;
  font-weight: 600;
  color: #1677ff;
  background: #f5f7fa;
  border-radius: 5px;
  padding: 2px 8px 2px 5px;
  margin-left: 8px;
}
.countdown-timer.ended {
  color: #b88600;
  background: #fffbe6;
  border: 1.2px solid #ffe58f;
}
.timer-icon {
  margin-right: 2px;
}
.bar-chart {
  width: 100%;
  height: 120px;
  min-height: 120px;
  background: #f4f8ff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.06);
  padding: 2px 0 2px 0;
  margin-bottom: 0;
}
.stats-info {
  display: flex;
  justify-content: space-between;
  font-size: 15px;
  color: #3a4a5a;
  margin-top: 8px;
  font-weight: 500;
  letter-spacing: 0.2px;
}
.stats-info span {
  background: transparent;
  border-radius: 6px;
  padding: 2px 8px;
}
.options-content-list {
  margin-top: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.option-content-item {
  display: flex;
  align-items: flex-start;
  font-size: 15px;
  color: #3a4a5a;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 2.5px 7px;
  box-shadow: none;
  transition: background 0.15s;
  cursor: pointer;
}
.option-content-item:hover {
  background: #e6f0ff;
}
/* 错误答案条：鼠标为默认，背景为悬浮蓝色 */
.option-content-item:not(.correct) {
  cursor: default;
  background: #e6f0ff;
}
.option-content-item.correct {
  background: #eaffea !important;
  border: 1.2px solid #52c41a;
}
.option-label {
  font-weight: bold;
  margin-right: 6px;
  color: #1677ff;
}
.option-content-item.correct .option-label {
  color: #52c41a;
}
.option-text {
  flex: 1;
  word-break: break-all;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.custom-tooltip {
  position: fixed;
  z-index: 9999;
  background: #eaf4ff;
  color: #1557c0;
  border: 1.5px solid #b3d1ff;
  border-radius: 8px;
  box-shadow: 0 4px 18px 0 rgba(22, 119, 255, 0.10), 0 1.5px 6px 0 rgba(22, 119, 255, 0.04);
  padding: 10px 16px;
  font-size: 15px;
  width: 260px;
  word-break: break-all;
  pointer-events: none;
  white-space: pre-line;
  transition: opacity 0.12s;
  font-weight: 500;
}
.tooltip-fade-enter-active, .tooltip-fade-leave-active {
  transition: opacity 0.15s cubic-bezier(.4,0,.2,1);
}
.tooltip-fade-enter-from, .tooltip-fade-leave-to {
  opacity: 0;
}
.tooltip-fade-enter-to, .tooltip-fade-leave-from {
  opacity: 1;
}
.question-list-header {
  font-size: 18px;
  font-weight: bold;
  color: #1677ff;
  padding: 16px 20px 10px 20px;
  border-bottom: 1.5px solid #e6f0ff;
  background: #fff;
  border-top-left-radius: 14px;
  border-top-right-radius: 14px;
}
.question-list-body {
  padding: 16px 20px;
  overflow-y: auto;
  max-height: calc(100% - 54px);
}
.question-list-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.question-list-item {
  background: #fff;
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.18s ease;
  min-height: 36px;
  cursor: pointer;
}
.question-list-item:hover {
  border-color: #1677ff;
  transform: translateY(-1px);
}
.question-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}
.question-status {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
  align-self: flex-start;
  margin-right: 8px;
  flex-shrink: 0;
}
.question-list-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
.question-status.ongoing {
  background: #e6fffb;
  color: #13c2c2;
  border: 1px solid #87e8de;
}
.question-status.ended {
  background: #fff7e6;
  color: #faad14;
  border: 1px solid #ffd591;
}
.question-list-empty {
  color: #aaa;
  text-align: center;
  margin-top: 40px;
  font-size: 15px;
}
.main-question-title {
  font-size: 20px;
  font-weight: 800;
  color: #223354;
  background: #fff;
  padding: 0 2px;
  border-radius: 4px;
  margin: 2px 0 2px 0;
  line-height: 1.3;
}
.discussion-area {
  background: #f8fafd;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(22, 119, 255, 0.04);
  flex-shrink: 0;
  margin-top: 4px;
}
.discussion-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.discussion-msg-item {
  font-size: 14px;
  color: #223354;
  line-height: 1.5;
}
.discussion-msg-user {
  font-weight: 600;
  color: #1677ff;
  margin-right: 4px;
}
.discussion-msg-text {
  color: #333;
}
.discussion-empty {
  color: #aaa;
  text-align: center;
  margin: 12px 0;
  font-size: 14px;
}
.main-content-scrollable {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
  gap: 12px;
}
.main-content-scrollable::-webkit-scrollbar {
  display: none;
}
</style> 