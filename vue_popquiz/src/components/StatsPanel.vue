<template>
  <div class="stats-panel-outer">
    <div class="stats-panel-header">我的数据</div>
    <div class="stats-panel-horizontal">
      <div class="stat-card score-card">
        <div class="stat-label">分数</div>
        <div class="stat-value score">{{ props.stats.score }}</div>
      </div>
      <div class="stat-card accuracy-card">
        <div class="stat-label">正确率</div>
        <div class="stat-value accuracy">{{ props.stats.accuracy }}%</div>
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
  stats: Object
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
.stat-card {
  background: linear-gradient(135deg, #fafdff 0%, #e6f0ff 100%);
  border-radius: 16px;
  box-shadow: none;
  border: none;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
  flex: 1 1 0;
  justify-content: center;
  transition: box-shadow 0.18s;
  box-sizing: border-box;
}
.score-card .stat-value {
  color: #722ed1;
  font-size: 2.3em;
  font-weight: 800;
  margin-top: 8px;
}
.accuracy-card .stat-value {
  color: #1677ff;
  font-size: 2.3em;
  font-weight: 800;
  margin-top: 8px;
}
.detail-card {
  align-items: flex-start;
  padding-left: 22px;
  padding-right: 22px;
  min-width: 130px;
  background: linear-gradient(135deg, #f8fff8 0%, #eaffea 100%);
  border: 1.5px solid #b7eb8f;
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