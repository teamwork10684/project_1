<template>
  <a-card class="answer-board-card" :body-style="{height: '100%', padding: '0', minHeight: '0'}">
    <div class="answer-board-content">
      <div class="main-board-flex">
        <!-- 答题区 -->
        <div class="question-section">
          <div class="question-header">
            <div class="question-title">{{ question }}</div>
            <div class="timer">
              <span class="countdown-timer" :class="{ 'ended': realCountdown <= 0 }">
                <svg class="timer-icon" viewBox="0 0 20 20" width="18" height="18">
                  <circle cx="10" cy="10" r="8" :stroke="realCountdown <= 0 ? '#b88600' : '#1677ff'" stroke-width="2" fill="none"/>
                  <path d="M10 5v5l3 2" :stroke="realCountdown <= 0 ? '#b88600' : '#1677ff'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                </svg>
                {{ countdownText }}
              </span>
            </div>
          </div>
          <div class="options-group">
            <div
              v-for="opt in options"
              :key="opt.value"
              :class="optionClass(opt.value)"
              @click="selectOption(opt.value)"
            >
              <span class="option-label">{{ opt.value }}.</span> {{ opt.text }}
              <span v-if="showCorrect && correctValue === opt.value" class="correct-badge">正确答案</span>
              <span v-if="showMyAnswer && myAnswer === opt.value" class="my-badge">我的选择</span>
            </div>
          </div>
          <a-button v-if="status === 0 && !myAnswer" type="primary" class="submit-btn" :disabled="!selected" @click="submitAnswer">提交答案</a-button>
        </div>
        <!-- 统计区 -->
        <div class="stats-section">
          <div ref="chartRef" class="bar-chart"></div>
          <div class="stats-info">
            <span class="stats-info-item accuracy" v-if="showCorrect && accuracy !== undefined && accuracy !== null">
              正确率：<span class="stats-number">{{ safeAccuracy }}%</span>
            </span>
            <span class="stats-info-item total">
              答题人数：<span class="stats-number">{{ statistics.answered_count }}</span>
            </span>
          </div>
        </div>
        <!-- 讨论区 -->
        <div class="discussion-section">
          <div class="discussion-title">讨论区</div>
          <div class="discussion-list">
            <template v-if="sortedDiscussions && sortedDiscussions.length">
              <div class="discussion-item" v-for="(msg, idx) in sortedDiscussions" :key="idx">
                <div class="discussion-msg-user-row">
                  <span class="author">{{ msg.username }}</span>
                  <span class="discussion-msg-time">{{ formatTime(msg.created_at || msg.timestamp) }}</span>
                </div>
                <div class="content">{{ msg.content }}</div>
              </div>
            </template>
            <div v-else class="discussion-empty">当前暂无讨论</div>
          </div>
        </div>
      </div>
    </div>
  </a-card>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch, onUnmounted } from 'vue';
import * as echarts from 'echarts';
const props = defineProps({
  question: String,
  options: Array,
  statistics: Object,
  status: Number, // 0进行中 1已结束
  myAnswer: String,
  correctValue: String,
  showCorrect: Boolean,
  showMyAnswer: Boolean,
  accuracy: Number,
  countdown: Number,
  start_time: String,
  end_time: String,
  discussions: Array
});
const selected = ref('');
const selectOption = (val) => {
  if (props.status === 0 && !props.myAnswer) {
    selected.value = val;
  }
};
const emit = defineEmits(['submit']);
const submitAnswer = () => {
  if (!selected.value) return;
  emit('submit', selected.value);
};
// 选项样式逻辑
const optionClass = (val) => {
  if (props.status === 1 && props.showCorrect) {
    // 已结束，正确答案高亮，若我选错也标记
    if (props.correctValue === val) return ['custom-option', 'correct'];
    if (props.myAnswer === val) return ['custom-option', 'my-selected', props.correctValue !== val ? 'wrong' : ''];
    return ['custom-option'];
  } else if (props.status === 0 && props.myAnswer) {
    // 进行中，已答题，标记我的选择
    if (props.myAnswer === val) return ['custom-option', 'my-selected', 'my-answered'];
    return ['custom-option'];
  } else if (props.status === 0 && !props.myAnswer) {
    // 进行中，未答题，选中项高亮
    if (selected.value === val) return ['custom-option', 'my-selected'];
    return ['custom-option'];
  } else {
    return ['custom-option'];
  }
};
// 统计区echarts
const chartRef = ref(null);
let chartInstance = null;
const renderChart = () => {
  if (!chartRef.value) return;
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  const option = {
    grid: { left: 35, right: 40, top: 10, bottom: 10 },
    xAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: {
        fontSize: 20,
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
      data: props.options.map(opt => opt.value),
      inverse: true,
      axisLabel: {
        fontSize: 22,
        color: '#1557c0',
        fontWeight: 'bold',
        fontFamily: 'Segoe UI, Arial, sans-serif',
        shadowColor: '#e6f0ff',
        shadowBlur: 2
      },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    series: [
      {
        type: 'bar',
        data: props.options.map(opt => ({
          value: opt.count,
          itemStyle: {
            color: props.showCorrect && props.correctValue === opt.value ? '#52c41a' : (props.myAnswer && props.myAnswer === opt.value && props.status === 0 ? '#1677ff' : '#1677ff'),
            borderRadius: [8, 8, 8, 8],
            borderWidth: props.showCorrect && props.correctValue === opt.value ? 3 : (props.myAnswer && props.myAnswer === opt.value && props.status === 0 ? 3 : 0),
            borderColor: props.showCorrect && props.correctValue === opt.value ? '#52c41a' : (props.myAnswer && props.myAnswer === opt.value && props.status === 0 ? '#1677ff' : 'transparent')
          }
        })),
        barWidth: 44,
        label: {
          show: true,
          position: 'right',
          fontSize: 22,
          fontWeight: 'bold',
          color: '#223354',
          formatter: function(params) {
            return params.value;
          },
          offset: [10, 0]
        }
      }
    ]
  };
  chartInstance.setOption(option);
};
onMounted(() => {
  nextTick(renderChart);
});
// 正确率和答题人数示例
const totalAnswered = computed(() => props.options.reduce((sum, o) => sum + o.count, 0));
const accuracy = computed(() => props.options.length > 0 ? Math.round((props.options[0].count / totalAnswered.value) * 100) : 0);

// 安全的accuracy，防止NaN
const safeAccuracy = computed(() => {
  return typeof props.accuracy === 'number' && !isNaN(props.accuracy) ? props.accuracy : 0;
});

// 实时倒计时
const realCountdown = ref(0);
let timer = null;
const calcCountdown = () => {
  if (!props.start_time || !props.end_time) {
    realCountdown.value = props.countdown || 0;
    return;
  }
  const end = new Date(props.end_time).getTime();
  const now = Date.now();
  const left = Math.max(0, Math.round((end - now) / 1000));
  realCountdown.value = left;
};
const startTimer = () => {
  stopTimer();
  calcCountdown();
  timer = setInterval(() => {
    calcCountdown();
    if (realCountdown.value <= 0) {
      stopTimer();
    }
  }, 1000);
};
const stopTimer = () => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
};
watch(() => [props.start_time, props.end_time, props.status], () => {
  if (props.status === 0) {
    startTimer();
  } else {
    stopTimer();
    calcCountdown();
  }
}, { immediate: true });

// 监听options和statistics变化，刷新图表
watch(
  () => [props.options, props.statistics],
  () => {
    nextTick(renderChart);
  },
  { deep: true }
);

onUnmounted(stopTimer);

const countdownText = computed(() => {
  if (realCountdown.value <= 0) return '已结束';
  const min = String(Math.floor(realCountdown.value / 60)).padStart(2, '0');
  const sec = String(realCountdown.value % 60).padStart(2, '0');
  return `${min}:${sec}`;
});

// 格式化时间（如 14:23:05 或 2024-05-01 14:23）
function formatTime(val) {
  if (!val) return '';
  const d = new Date(val);
  const h = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  return `${h}:${min}`;
}

// 升序排序讨论内容
const sortedDiscussions = computed(() => {
  if (!props.discussions) return [];
  return props.discussions.slice().sort((a, b) => new Date(a.created_at || a.timestamp) - new Date(b.created_at || b.timestamp));
});
</script>

<style scoped>
.answer-board-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.3);
  min-height: 0;
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  overflow: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}
.answer-board-card::-webkit-scrollbar {
  display: none;
}
.answer-board-content {
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1 1 auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
  border-radius: 12px;
}
.answer-board-content::-webkit-scrollbar {
  display: none;
}
.main-board-flex {
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1 1 auto;
  overflow: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}
.main-board-flex::-webkit-scrollbar {
  display: none;
}
.question-section {
  flex: 0 0 auto;
  min-height: 35%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding: 24px 24px 8px 24px;
  background: #fff;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}
.question-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.question-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #1677ff;
  flex: 1;
  word-break: break-word;
  line-height: 1.6;
}
.timer {
  flex-shrink: 0;
  align-self: flex-start;
}
.options-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 12px;
  flex: 0 0 auto;
}
.custom-option {
  background: #fff;
  color: #222;
  border: 2.5px solid #e6e6e6; /* 默认灰色边框 */
  border-radius: 10px;
  padding: 14px 18px;
  font-size: 1.15em;
  font-weight: 700; /* 所有状态都加粗，避免字体抖动 */
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  box-shadow: 0 2px 8px rgba(22,119,255,0.03);
  display: flex;
  align-items: center;
  min-height: 44px; /* 保证高度一致 */
}
.custom-option.selected {
  background: #1677ff;
  color: #fff;
  border-color: #1677ff;
  box-shadow: 0 4px 16px rgba(22,119,255,0.08);
}
.custom-option:hover {
  border-color: #1677ff;
  background: #f0f7ff;
}
.custom-option.selected:hover {
  background: #1677ff;
  color: #fff;
}
.option-label {
  font-weight: 700;
  margin-right: 10px;
}
.submit-btn {
  margin-top: 16px;
  align-self: flex-end;
}
.stats-section {
  flex: 0 0 auto;
  min-height: 120px;
  padding: 8px 24px 8px 24px;
  background: #fafcff;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}
.bar-chart {
  width: 100%;
  height: 280px;
  min-height: 280px;
  background: #f4f8ff;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.06);
  padding: 8px 0 8px 0;
  margin-bottom: 0;
}
.stats-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.15em;
  color: #3a4a5a;
  margin-top: 16px;
  font-weight: 500;
  letter-spacing: 0.2px;
  background: transparent;
  border-radius: 10px;
  gap: 18px;
}
.stats-info-item {
  background: #f0f7ff;
  border-radius: 18px;
  padding: 6px 18px;
  display: flex;
  align-items: center;
  font-size: 1.08em;
  font-weight: 500;
  color: #1677ff;
  box-shadow: 0 1px 4px rgba(22, 119, 255, 0.04);
}
.stats-info-item.accuracy {
  background: #e6fffb;
  color: #13c2c2;
}
.stats-info-item.total {
  background: #f0f7ff;
  color: #1677ff;
}
.stats-number {
  font-size: 1.25em;
  font-weight: 700;
  margin-left: 4px;
  margin-right: 2px;
}
.stat-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 24px;
}
.stat-item {
  color: #333;
  font-size: 1em;
}
.discussion-section {
  min-height: 100px;
  max-height: 90%;
  display: flex;
  flex-direction: column;
  padding: 12px 24px 24px 24px;
  overflow-y: auto;
  overflow-x: hidden;
  /* 不要设置height */
}
.discussion-title {
  font-weight: 600;
  color: #1677ff;
  margin-bottom: 8px;
}
.discussion-list {
  flex: 1 1 auto;
  margin-bottom: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.discussion-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  gap: 2px;
  font-size: 15px;
  color: #223354;
  line-height: 1.7;
  background: #f0f7ff;
  border-radius: 7px;
  padding: 2px 8px;
  border: 1px solid #b3d1ff;
  margin-bottom: 1px;
  transition: background 0.15s, border 0.15s;
}
.discussion-item:hover {
  background: #e6f0ff;
  border: 1px solid #1677ff;
}
.author {
  font-weight: 600;
  color: #1677ff;
  font-size: 15px;
  margin-right: 8px;
  padding-left: 1px;
}
.content {
  color: #223354;
  font-size: 15px;
  word-break: break-all;
  flex: none;
  padding-left: 1px;
}
.discussion-input {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.custom-option.correct {
  background: #eaffea;
  color: #52c41a;
  border-color: #52c41a;
}
.custom-option.my-selected {
  background: #1677ff;
  color: #fff;
  border-color: #1677ff;
}
/* 进行中已答题时我的选项：蓝色内边框，白底蓝字 */
.custom-option.my-selected.my-answered {
  background: #fff;
  color: #1677ff;
  border-color: #1677ff;
}
.custom-option.my-selected.wrong {
  background: #fff1f0;
  color: #ff4d4f;
  border-color: #ff4d4f;
}
.correct-badge,
.my-badge {
  margin-left: 10px;
  font-size: 0.95em;
  font-weight: 600;
  line-height: 1.5;
  min-height: 1.5em;
  display: inline-block;
}
.countdown-timer {
  display: inline-flex;
  align-items: center;
  font-size: 1.15em;
  font-weight: bold;
  color: #1677ff;
  background: #f0f7ff;
  border-radius: 18px;
  padding: 4px 16px 4px 10px;
  margin-left: 0;
  margin-right: 0;
  gap: 6px;
  box-shadow: 0 1px 4px rgba(22, 119, 255, 0.04);
  border: 1.5px solid #e6f0ff;
}
.countdown-timer.ended {
  color: #b88600;
  background: #fffbe6;
  border-color: #ffe58f;
}
.timer-icon {
  margin-right: 6px;
}
.discussion-msg-user-row {
  display: flex;
  align-items: baseline;
  width: 100%;
  justify-content: space-between;
  margin-bottom: 1px;
}
.discussion-msg-time {
  color: #b3b3b3;
  font-size: 12px;
  white-space: nowrap;
  align-self: flex-end;
  font-family: 'Segoe UI', Arial, sans-serif;
  letter-spacing: 0.5px;
  margin-left: auto;
}
.discussion-empty {
  color: #b3b3b3;
  text-align: center;
  margin: 0 auto;
  font-size: 16px;
  border-radius: 10px;
  padding: 24px 0;
  border: 1.5px dashed #e6f0ff;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
  width: 100%;
}
</style> 