<template>
  <div class="question-publish-panel-outer">
    <div 
      class="question-publish-panel-slider"
      :class="{ 'show-detail': showDetail, 'show-settings': showSettings }"
    >
      <!-- 左侧：设置面板 -->
      <div class="panel-settings">
        <div class="settings-content">
          <div class="settings-header">
            <div class="settings-header-content">
              <span class="settings-header-title">设置</span>
              <a-button type="link" @click="closeSettings" class="back-btn">
                返回
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14">
                  <path d="M5 12H19M12 5L19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </a-button>
            </div>
          </div>
          <div class="settings-body">
            <div class="settings-content-wrapper">
              <div class="settings-section">
                <div class="setting-row">
                  <div class="setting-main">
                    <div class="setting-label">
                      <span class="label-text">自动发布间隔</span>
                    </div>
                    <div class="setting-input-group">
                      <a-input-number 
                        v-model:value="autoPublishInterval" 
                        :min="5" 
                        :max="60" 
                        size="small"
                        class="setting-input-number"
                      />
                      <span class="setting-unit">分钟</span>
                    </div>
                  </div>
                  <div class="setting-hint">5-60分钟</div>
                </div>
              </div>
              
              <div class="settings-section">
                <div class="setting-row">
                  <div class="setting-main">
                    <div class="setting-label">
                      <span class="label-text">答题限时</span>
                    </div>
                    <div class="setting-input-group">
                      <a-input-number 
                        v-model:value="answerTimeLimit" 
                        :min="60" 
                        :max="120" 
                        size="small"
                        class="setting-input-number"
                      />
                      <span class="setting-unit">秒</span>
                    </div>
                  </div>
                  <div class="setting-hint">60-120秒</div>
                </div>
              </div>
            </div>
            
            <div class="settings-actions">
              <a-button type="primary" @click="saveSettings" class="save-btn">
                保存设置
              </a-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 中间：题目列表和按钮 -->
      <div class="panel-list">
        <div class="button-area">
          <div class="settings-icon" @click="showSettings = true">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="16" height="16">
              <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M19.4 15C19.2669 15.3016 19.2272 15.6362 19.286 15.9606C19.3448 16.285 19.4995 16.5843 19.73 16.82L19.79 16.88C19.976 17.0657 20.1235 17.2863 20.2241 17.5291C20.3248 17.7719 20.3766 18.0322 20.3766 18.295C20.3766 18.5578 20.3248 18.8181 20.2241 19.0609C20.1235 19.3037 19.976 19.5243 19.79 19.71C19.6043 19.896 19.3837 20.0435 19.1409 20.1441C18.8981 20.2448 18.6378 20.2966 18.375 20.2966C18.1122 20.2966 17.8519 20.2448 17.6091 20.1441C17.3663 20.0435 17.1457 19.896 16.96 19.71L16.9 19.65C16.6643 19.4195 16.365 19.2648 16.0406 19.206C15.7162 19.1472 15.3816 19.1869 15.08 19.32C14.7842 19.4468 14.532 19.6572 14.3543 19.9255C14.1766 20.1938 14.0813 20.5082 14.08 20.83V21C14.08 21.5304 13.8693 22.0391 13.4942 22.4142C13.1191 22.7893 12.6104 23 12.08 23C11.5496 23 11.0409 22.7893 10.6658 22.4142C10.2907 22.0391 10.08 21.5304 10.08 21V20.91C10.0723 20.579 9.96512 20.257 9.77251 19.9887C9.5799 19.7204 9.31074 19.5179 9 19.41C8.69838 19.2769 8.36381 19.2372 8.03941 19.296C7.71502 19.3548 7.41568 19.4995 7.18 19.73L7.12 19.79C6.93425 19.976 6.71368 20.1235 6.47088 20.2241C6.22808 20.3248 5.96783 20.3766 5.705 20.3766C5.44217 20.3766 5.18192 20.3248 4.93912 20.2241C4.69632 20.1235 4.47575 19.976 4.29 19.79C4.10405 19.6043 3.95653 19.3837 3.85588 19.1409C3.75523 18.8981 3.70343 18.6378 3.70343 18.375C3.70343 18.1122 3.75523 17.8519 3.85588 17.6091C3.95653 17.3663 4.10405 17.1457 4.29 16.96L4.35 16.9C4.58054 16.6643 4.73519 16.365 4.794 16.0406C4.85282 15.7162 4.81312 15.3816 4.68 15.08C4.55324 14.7842 4.34276 14.532 4.07447 14.3543C3.80618 14.1766 3.49179 14.0813 3.17 14.08H3C2.46957 14.08 1.96086 13.8693 1.58579 13.4942C1.21071 13.1191 1 12.6104 1 12.08C1 11.5496 1.21071 11.0409 1.58579 10.6658C1.96086 10.2907 2.46957 10.08 3 10.08H3.09C3.42099 10.0723 3.743 9.96512 4.0113 9.77251C4.27959 9.5799 4.4821 9.31074 4.59 9C4.72312 8.69838 4.76282 8.36381 4.704 8.03941C4.64519 7.71502 4.50054 7.41568 4.27 7.18L4.21 7.12C4.02405 6.93425 3.87653 6.71368 3.77588 6.47088C3.67523 6.22808 3.62343 5.96783 3.62343 5.705C3.62343 5.44217 3.67523 5.18192 3.77588 4.93912C3.87653 4.69632 4.02405 4.47575 4.21 4.29C4.39575 4.10405 4.61632 3.95653 4.85912 3.85588C5.10192 3.75523 5.36217 3.70343 5.625 3.70343C5.88783 3.70343 6.14808 3.75523 6.39088 3.85588C6.63368 3.95653 6.85425 4.10405 7.04 4.29L7.1 4.35C7.33568 4.58054 7.63502 4.73519 7.95941 4.794C8.28381 4.85282 8.61838 4.81312 8.92 4.68H9C9.29577 4.55324 9.54802 4.34276 9.72569 4.07447C9.90337 3.80618 9.99872 3.49179 10 3.17V3C10 2.46957 10.2107 1.96086 10.5858 1.58579C10.9609 1.21071 11.4696 1 12 1C12.5304 1 13.0391 1.21071 13.4142 1.58579C13.7893 1.96086 14 2.46957 14 3V3.09C14.0013 3.41179 14.0966 3.72618 14.2743 3.99447C14.452 4.26276 14.7042 4.47324 15 4.6C15.3016 4.73312 15.6362 4.77282 15.9606 4.714C16.285 4.65519 16.5843 4.51054 16.82 4.28L16.88 4.21C17.0657 4.02405 17.2863 3.87653 17.5291 3.77588C17.7719 3.67523 18.0322 3.62343 18.295 3.62343C18.5578 3.62343 18.8181 3.67523 19.0609 3.77588C19.3037 3.87653 19.5243 4.02405 19.71 4.21C19.896 4.39575 20.0435 4.61632 20.1441 4.85912C20.2448 5.10192 20.2966 5.36217 20.2966 5.625C20.2966 5.88783 20.2448 6.14808 20.1441 6.39088C20.0435 6.63368 19.896 6.85425 19.71 7.04L19.65 7.1C19.4195 7.33568 19.2648 7.63502 19.206 7.95941C19.1472 8.28381 19.1869 8.61838 19.32 8.92V9C19.4468 9.29577 19.6572 9.54802 19.9255 9.72569C20.1938 9.90337 20.5082 9.99872 20.83 10H21C21.5304 10 22.0391 10.2107 22.4142 10.5858C22.7893 10.9609 23 11.4696 23 12C23 12.5304 22.7893 13.0391 22.4142 13.4142C22.0391 13.7893 21.5304 14 21 14H20.91C20.5882 14.0013 20.2738 14.0966 20.0055 14.2743C19.7372 14.452 19.5268 14.7042 19.4 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <a-button type="primary" class="auto-publish-btn" @click="handleAutoPublish">
            自动发布
          </a-button>
        </div>
        <div class="question-list">
          <div 
            class="question-item" 
            v-for="(question, index) in questions" 
            :key="index"
            @click="handleViewDetail(question)"
          >
            <div class="question-info">
              <div class="question-title">{{ question.question }}</div>
              <div class="question-status" :class="question.published ? 'published' : 'unpublished'">
                {{ question.published ? '已发布' : '未发布' }}
              </div>
            </div>
            <div class="question-actions">
              <a-button size="small" type="primary" @click.stop="handlePublishQuestion(question)" :disabled="question.published">
                {{ question.published ? '已发布' : '发布' }}
              </a-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：题目详情面板 -->
      <div class="panel-detail">
        <div v-if="selectedQuestion" class="detail-content">
          <div class="detail-header">
            <a-button type="link" @click="closeDetail" class="back-btn">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14">
                <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              返回
            </a-button>
          </div>
          <div class="detail-body">
            <div class="question-meta">
              <span class="meta-item" :class="selectedQuestion.published ? 'published' : 'unpublished'">
                {{ selectedQuestion.published ? '已发布' : '未发布' }}
              </span>
              <span class="meta-item">{{ formatDate(selectedQuestion.created_at) }}</span>
            </div>
            
            <div class="title-row">
              <h3 class="detail-title">{{ selectedQuestion.question }}</h3>
              <a-button type="primary" size="small" @click="handlePublishFromDetail" :disabled="selectedQuestion.published">
                {{ selectedQuestion.published ? '已发布' : '发布' }}
              </a-button>
            </div>
            
            <div class="detail-section">
              <div class="options-list">
                <div class="option-item" :class="{ 'correct': selectedQuestion.answer === 'A' }">
                  <span class="option-label">A.</span>
                  <span class="option-text">{{ selectedQuestion.option_a }}</span>
                  <span v-if="selectedQuestion.answer === 'A'" class="correct-badge">正确答案</span>
                </div>
                <div class="option-item" :class="{ 'correct': selectedQuestion.answer === 'B' }">
                  <span class="option-label">B.</span>
                  <span class="option-text">{{ selectedQuestion.option_b }}</span>
                  <span v-if="selectedQuestion.answer === 'B'" class="correct-badge">正确答案</span>
                </div>
                <div class="option-item" :class="{ 'correct': selectedQuestion.answer === 'C' }">
                  <span class="option-label">C.</span>
                  <span class="option-text">{{ selectedQuestion.option_c }}</span>
                  <span v-if="selectedQuestion.answer === 'C'" class="correct-badge">正确答案</span>
                </div>
                <div class="option-item" :class="{ 'correct': selectedQuestion.answer === 'D' }">
                  <span class="option-label">D.</span>
                  <span class="option-text">{{ selectedQuestion.option_d }}</span>
                  <span v-if="selectedQuestion.answer === 'D'" class="correct-badge">正确答案</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { message } from 'ant-design-vue';

const props = defineProps({
  questions: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['autoPublish', 'publishQuestion', 'saveSettings']);

const selectedQuestion = ref(null);
const showDetail = ref(false);
const showSettings = ref(false);

// 从本地存储加载设置值，如果没有则使用默认值
const autoPublishInterval = ref(parseInt(localStorage.getItem('autoPublishInterval')) || 5);
const answerTimeLimit = ref(parseInt(localStorage.getItem('answerTimeLimit')) || 60);

// 验证规则
const validateSettings = () => {
  const errors = [];
  
  if (autoPublishInterval.value < 5) {
    errors.push('自动发布间隔不能少于5分钟');
  }
  
  if (answerTimeLimit.value < 60) {
    errors.push('答题限时不能少于60秒');
  }
  
  if (answerTimeLimit.value > 120) {
    errors.push('答题限时不能超过120秒');
  }
  
  return errors;
};

const handleViewDetail = (question) => {
  selectedQuestion.value = question;
  showDetail.value = true;
};

const closeDetail = () => {
  showDetail.value = false;
  // 动画结束后清空选中的题目
  setTimeout(() => {
    selectedQuestion.value = null;
  }, 350);
};

const handleAutoPublish = () => {
  emit('autoPublish');
};

const closeSettings = () => {
  showSettings.value = false;
};

const saveSettings = () => {
  // 验证设置
  const errors = validateSettings();
  if (errors.length > 0) {
    // 显示错误信息
    message.error('设置验证失败: ' + errors.join(', '));
    return;
  }
  
  // 保存到本地存储
  localStorage.setItem('autoPublishInterval', autoPublishInterval.value.toString());
  localStorage.setItem('answerTimeLimit', answerTimeLimit.value.toString());
  
  // 触发事件通知父组件
  emit('saveSettings', {
    autoPublishInterval: autoPublishInterval.value,
    answerTimeLimit: answerTimeLimit.value
  });
  
  // 显示成功提示
  message.success('设置保存成功！');
  
  showSettings.value = false;
};

const handlePublishQuestion = (question) => {
  emit('publishQuestion', question);
};

const handlePublishFromDetail = () => {
  if (selectedQuestion.value) {
    emit('publishQuestion', selectedQuestion.value);
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
.question-publish-panel-outer {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
  background: #fafafa;
  border-radius: 8px;
}

.question-publish-panel-slider {
  display: flex;
  width: 300%;
  height: 100%;
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
  transform: translateX(-33.33%);
}

.question-publish-panel-slider.show-detail {
  transform: translateX(-66.66%);
}

.question-publish-panel-slider.show-settings {
  transform: translateX(0);
}

.panel-list,
.panel-detail,
.panel-settings {
  width: 33.33%;
  min-width: 0;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.panel-list {
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.panel-detail {
  background: #fff;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.panel-settings {
  background: #fff;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.button-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px 4px 12px;
  background: transparent;
  z-index: 2;
  flex-shrink: 0;
}

.settings-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: rgba(22, 119, 255, 0.1);
  color: #1677ff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.settings-icon:hover {
  background: rgba(22, 119, 255, 0.2);
  transform: scale(1.05);
}

.question-list {
  flex: 1;
  min-height: 0;
  max-height: 100%;
  overflow-y: auto;
  padding: 8px 12px 8px 12px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 6px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.question-list::-webkit-scrollbar {
  display: none;
}

.question-item {
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

.question-item:hover {
  border-color: #1677ff;
  transform: translateY(-1px);
}

.question-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-right: 8px;
}

.question-title {
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

.question-status {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
  align-self: flex-start;
}

.question-status.published {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.question-status.unpublished {
  background: #fff7e6;
  color: #faad14;
  border: 1px solid #ffd591;
}

.question-actions {
  display: flex;
  gap: 5px;
}

.auto-publish-btn {
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  border: none;
  border-radius: 8px;
  color: #fff;
}

.auto-publish-btn:hover {
  background: linear-gradient(90deg, #0958d9 0%, #1677ff 100%);
}

.publish-settings-btn {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  background: #fff;
  color: #666;
}

.publish-settings-btn:hover {
  border-color: #1677ff;
  color: #1677ff;
}

/* 详情面板样式 */
.detail-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.detail-header {
  padding: 10px 20px 4px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
  flex-shrink: 0;
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
}

.back-btn:hover svg {
  transform: translateX(-2px);
}

.settings-header .back-btn:hover svg {
  transform: translateX(2px);
}

.detail-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.detail-body::-webkit-scrollbar {
  display: none;
}

.question-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 6px;
}

.meta-item {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
  color: #666;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
}

.meta-item.published {
  background: #f6ffed;
  color: #52c41a;
  border-color: #b7eb8f;
}

.meta-item.unpublished {
  background: #fff7e6;
  color: #faad14;
  border-color: #ffd591;
}

.title-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.detail-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
  line-height: 1.4;
  flex: 1;
}

.detail-description {
  flex: 1;
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #f0f0f0;
}

/* 详情面板新样式 */
.detail-section {
  margin-bottom: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-content-box {
  background: #fafafa;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #f0f0f0;
}

.detail-content-box p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #666;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;
  position: relative;
}

.option-item.correct {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.option-label {
  font-weight: 600;
  color: #1677ff;
  min-width: 20px;
  font-size: 14px;
}

.option-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.correct-badge {
  font-size: 11px;
  color: #52c41a;
  background: #f6ffed;
  padding: 2px 6px;
  border-radius: 10px;
  border: 1px solid #b7eb8f;
  font-weight: 500;
  white-space: nowrap;
}





/* 设置面板样式 */
.settings-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.settings-header {
  padding: 10px 20px 4px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
  flex-shrink: 0;
}

.settings-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-header-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.settings-body {
  flex: 1;
  padding: 10px 0px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.settings-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.settings-section {
  background: #fafafa;
  border-radius: 8px;
  padding: 8px;
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;
}

.settings-section:hover {
  border-color: #1677ff;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.1);
}

.setting-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.setting-label {
  display: flex;
  flex-direction: column;
  gap: 0px;
  flex: 1;
}

.label-text {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  line-height: 1.2;
}

.setting-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.setting-input-number {
  width: 60px;
}

.setting-input-number :deep(.ant-input-number-input) {
  height: 26px;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

.setting-hint {
  font-size: 11px;
  color: #999;
  line-height: 1.2;
  padding-left: 4px;
}

.setting-unit {
  font-size: 13px;
  color: #666;
  font-weight: 500;
  white-space: nowrap;
}

.settings-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.save-btn {
  height: 36px;
  padding: 0 24px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #1677ff 0%, #69b1ff 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.2);
  transition: all 0.2s ease;
}

.save-btn:hover {
  background: linear-gradient(135deg, #0958d9 0%, #1677ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .detail-body {
    padding: 16px 12px;
  }
  
  .detail-header {
    padding: 12px 12px 8px 12px;
  }
  
  .detail-title {
    font-size: 16px;
  }
  
  .settings-body {
    padding: 16px 12px;
  }
}
</style> 