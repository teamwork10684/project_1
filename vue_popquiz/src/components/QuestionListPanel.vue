<template>
  <div class="question-list-panel-outer">
    <div class="question-list-header">已发布题目</div>
    <div class="question-list-panel-list">
      <div 
        class="question-list-item" 
        v-for="(item, index) in props.questions" 
        :key="index"
        @click="$emit('select', item)"
      >
        <div class="question-info">
          <div class="question-title">{{ item.question }}</div>
          <div class="question-status" :class="item.status === 0 ? 'ongoing' : 'ended'">
            {{ item.status === 0 ? '进行中' : '已结束' }}
          </div>
        </div>
      </div>
      <div v-if="!props.questions.length" class="question-list-empty">暂无题目</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  questions: Array
});
defineEmits(['select']);
</script>

<style scoped>
.question-list-panel-outer {
  width: 100%;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: hidden;
}
.question-list-header {
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
.question-list-panel-list {
  flex: 1 1 0%;
  min-height: 0;
  max-height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 2px 2px 2px 2px;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}
.question-list-panel-list::-webkit-scrollbar {
  display: none;
}
.question-list-item {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.06);
  border: 1px solid #f0f0f0;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 44px;
  max-height: 44px;
  cursor: pointer;
  transition: box-shadow 0.18s, border-color 0.18s;
}
.question-list-item:hover {
  border-color: #1677ff;
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.10);
}
.question-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  min-width: 0;
  max-width: 100%;
}
.question-title {
  flex: 1;
  color: #223354;
  font-size: 1.08em;
  font-weight: 500;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  max-width: 100%;
  word-break: break-all;
}
.question-status {
  font-size: 0.95em;
  padding: 2px 10px;
  border-radius: 10px;
  font-weight: 500;
  margin-left: 8px;
  background: #f0f0f0;
  color: #999;
  border: 1px solid #f0f0f0;
}
.question-status.ongoing {
  background: #eaffea;
  color: #52c41a;
  border: 1px solid #b7eb8f;
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
</style> 