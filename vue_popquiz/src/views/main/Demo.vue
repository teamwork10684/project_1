<template>
  <div class="demo-content">
    <h2>AI 题目生成 Demo</h2>
    <a-form layout="vertical" class="form-card" @submit.prevent="handleSubmit">
      <a-form-item label="题目描述">
        <a-textarea
          v-model:value="originalPrompt"
          :rows="3"
          placeholder="请输入题目描述，如：请根据以下内容出一道选择题：太阳从哪边升起？"
          allow-clear
        />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" :loading="loading" @click="handleSubmit">生成题目</a-button>
      </a-form-item>
    </a-form>
    <a-alert v-if="errorMsg" :message="errorMsg" type="error" show-icon class="error-alert" />
    <div v-if="questionResult" class="result-card">
      <h3>生成结果</h3>
      <p class="question">{{ questionResult.question }}</p>
      <ul class="options">
        <li v-for="(opt, idx) in questionResult.options" :key="idx">
          <span class="option-label">{{ String.fromCharCode(65 + idx) }}.</span> {{ opt }}
        </li>
      </ul>
      <div v-if="questionResult.answer" class="answer">
        <span>正确答案：</span>
        <span class="answer-text">{{ questionResult.answer }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance } from 'vue'
import { message } from 'ant-design-vue'

const originalPrompt = ref('')
const loading = ref(false)
const questionResult = ref(null)
const errorMsg = ref('')

const { appContext } = getCurrentInstance()
const axios = appContext.config.globalProperties.$axios

const handleSubmit = async () => {
  if (!originalPrompt.value.trim()) {
    errorMsg.value = '请输入题目描述';
    return;
  }
  errorMsg.value = ''
  loading.value = true
  questionResult.value = null
  try {
    const res = await axios.post('/getQuestionByTextOllamaDemo', {
      original_prompt: originalPrompt.value
    }, {
      timeout: 15000 // 设置最大延迟为15秒
    })
    const data = res.data
    if (data.question && Array.isArray(data.options)&&data.answer) {

      questionResult.value = data
    } else {
      errorMsg.value = data.message || '生成失败，请重试';
    }
  } catch (e) {
    if(e.response.data.message){
      errorMsg.value = e.response.data.message
    }else{
      errorMsg.value = '网络错误或服务未启动';
    }

    console.log(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.demo-content {
  max-width: 500px;
  margin: 40px auto;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 #e6f0ff;
  padding: 32px 24px 24px 24px;
}
h2 {
  color: #1677ff;
  margin-bottom: 1.5rem;
  font-weight: 700;
  letter-spacing: 1px;
}
.form-card {
  margin-bottom: 24px;
}
.result-card {
  background: #f6faff;
  border-radius: 10px;
  padding: 18px 20px 10px 20px;
  margin-top: 18px;
  box-shadow: 0 2px 8px #e6f0ff;
}
.result-card h3 {
  color: #1677ff;
  margin-bottom: 10px;
}
.question {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 10px;
}
.options {
  list-style: none;
  padding: 0;
  margin: 0;
}
.options li {
  padding: 6px 0;
  font-size: 1rem;
  text-align: left;
}
.option-label {
  font-weight: bold;
  color: #1677ff;
  margin-right: 6px;
}
.error-alert {
  margin-top: 18px;
}
.answer {
  margin-top: 16px;
  font-size: 1.1rem;
  color: #52c41a;
  font-weight: 600;
}
.answer-text {
  color: #1677ff;
  font-weight: bold;
  margin-left: 8px;
}
</style>
