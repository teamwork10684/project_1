<template>
  <div class="question-stats-bar">
    <div class="question-title-row">
      <span class="question-title">{{ question }}</span>
      <span v-if="countdown" class="countdown-timer">
        <svg class="timer-icon" viewBox="0 0 20 20" width="18" height="18"><circle cx="10" cy="10" r="8" stroke="#1677ff" stroke-width="2" fill="none"/><path d="M10 5v5l3 2" stroke="#1677ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
        {{ countdown }}
      </span>
    </div>
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
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  question: { type: String, required: true },
  options: { type: Array, required: true }, // [{ label: 'A', text: 'xxx', count: 10 }, ...]
  unselectedCount: { type: Number, required: true },
  accuracy: { type: Number, required: true }, // 0~1
  correctLabel: { type: String, required: true }, // 正确答案的label，如 'A'
  endTime: { type: [String, Number], required: false, default: null } // 结束时间戳或ISO字符串
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
    grid: { left: 25, right: 20, top: 20, bottom: 30 },
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
.question-stats-bar {
  width: 100%;
  background: #fff;
  border-radius: 14px;
  padding: 14px 16px 10px 16px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: box-shadow 0.2s;
}
.question-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
  border-bottom: 1.5px solid #e6f0ff;
  padding-bottom: 4px;
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
.timer-icon {
  margin-right: 2px;
}
.bar-chart {
  width: 100%;
  height: 180px;
  min-height: 100px;
  background: #f4f8ff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.06);
  padding: 4px 0 4px 0;
  margin-bottom: 0;
}
.stats-info {
  display: flex;
  justify-content: space-between;
  font-size: 15px;
  color: #3a4a5a;
  margin-top: 4px;
  font-weight: 500;
  letter-spacing: 0.2px;
}
.stats-info span {
  background: #eaf4ff;
  border-radius: 6px;
  padding: 2px 8px;
  box-shadow: 0 1px 2px rgba(22, 119, 255, 0.04);
}
.options-content-list {
  margin-top: 2px;
  display: flex;
  flex-direction: column;
  gap: 2px;
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
}
.option-content-item:hover {
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
</style> 