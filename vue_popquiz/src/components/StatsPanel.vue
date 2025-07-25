<template>
  <div class="stats-panel-outer">
    <div class="stats-panel-header">我的数据</div>
    <div class="stats-panel-horizontal">
      <div class="stats-panel-left">
        <div class="stats-panel-top">
          <div class="stat-card score-card">
            <div class="stat-label">分数</div>
            <div class="stat-value score">{{ props.stats.score }}</div>
          </div>
          <div class="stat-card accuracy-card">
            <div class="stat-label">正确率</div>
            <div class="stat-value accuracy">{{ Math.round(props.stats.accuracy) }}%</div>
          </div>
        </div>
        <div class="stat-card rank-card">
          <div class="stat-label">分数排名</div>
          <div class="stat-value rank">{{ props.stats.rank }}</div>
        </div>
      </div>
      <div class="stat-card detail-card">
        <div class="stat-detail-row">
          <span class="stat-label">正确</span>
          <span class="stat-value correct">{{ props.stats.correct }}</span>
        </div>
        <div class="stat-detail-row">
          <span class="stat-label">错误</span>
          <span class="stat-value wrong">{{ props.stats.wrong }}</span>
        </div>
        <div class="stat-detail-row">
          <span class="stat-label">跳过</span>
          <span class="stat-value skip">{{ props.stats.skip }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      score: 0,
      accuracy: 0,
      correct: 0,
      wrong: 0,
      skip: 0,
      rank: '-'
    })
  }
});
</script>

<style scoped>
.stats-panel-outer {
  width: 100%;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: hidden;
  flex: 1 1 0%;
}
.stats-panel-header {
  font-size: 1.15em;
  font-weight: bold;
  color: #1677ff;
  padding: 12px 18px 8px 18px;
  background: #f7fbff;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  border-bottom: 1.5px solid #e6f0ff;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}
.stats-panel-horizontal {
  display: flex;
  flex-direction: row;
  gap: 16px;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  justify-content: space-between;
  align-items: stretch;
  box-sizing: border-box;
  flex: 1 1 0%;
  height: 100%;
  min-height: 0;
  background: #fff;
  padding: 16px;
}
.stats-panel-left {
  display: flex;
  flex-direction: column;
  flex: 1 1 0;
  min-width: 0;
  min-height: 0;
  gap: 12px;
}
.stats-panel-top {
  display: flex;
  flex-direction: row;
  gap: 16px;
  flex: 1 1 0;
  min-height: 0;
}
.score-card,
.accuracy-card {
  flex: 1 1 0;
  min-width: 100px;
  min-height: 0;
  padding: 12px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fafdff 0%, #e6f0ff 100%);
  border-radius: 16px;
  border: 1.5px solid #e6f0ff;
  box-shadow: 0 2px 8px 0 rgba(22, 119, 255, 0.04);
  transition: box-shadow 0.18s;
  box-sizing: border-box;
}
.rank-card {
  margin-top: 0;
  flex: 1 1 0;
  min-height: 0;
  background: linear-gradient(135deg, #fafdff 0%, #e6f0ff 100%);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 18px 28px;
  font-size: 1.2em;
  font-weight: 600;
  color: #faad14;
  box-shadow: 0 2px 8px 0 rgba(22, 119, 255, 0.04);
  border: 1.5px solid #e6f0ff;
  box-sizing: border-box;
}
.rank-card .stat-label {
  font-size: 1.1em;
  font-weight: 500;
  margin-bottom: 6px;
  margin-right: 0;
}
.rank-card .stat-value.rank {
  color: #faad14;
  font-size: 1.7em;
  font-weight: 800;
}
.detail-card {
  align-items: center;
  justify-content: space-evenly;
  display: flex;
  flex-direction: column;
  padding-left: 22px;
  padding-right: 22px;
  min-width: 130px;
  background: linear-gradient(135deg, #fafdff 0%, #e6f0ff 100%);
  border: 1.5px solid #e6f0ff;
  border-radius: 16px;
  box-shadow: 0 2px 8px 0 rgba(22, 119, 255, 0.04);
  box-sizing: border-box;
}
.stat-detail-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.stat-detail-row:last-child {
  margin-bottom: 0;
}
.stat-label {
  font-size: 1.18em;
  color: #888;
  min-width: 38px;
  white-space: nowrap;
}
.stat-value {
  font-size: 1.45em;
  font-weight: 700;
  color: #1677ff;
}
.stat-value.correct {
  color: #52c41a;
}
.stat-value.wrong {
  color: #ff4d4f;
}
.stat-value.skip {
  color: #faad14;
}
.stat-value.score {
  color: #722ed1;
}
</style> 