<template>
  <div class="student-profile">
    <div class="avatar-section">
      <img class="avatar" :src="avatarUrl" alt="头像" />
    </div>
    <div class="info-section">
      <div class="info-item"><span class="label">姓名：</span>{{ name }}</div>
      <div class="info-item"><span class="label">学号：</span>{{ studentId }}</div>
      <div class="info-item"><span class="label">班级：</span>{{ className }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const avatarUrl = ref('https://avatars.githubusercontent.com/u/1?v=4');
const name = ref('学生姓名');
const studentId = ref('20240001');
const className = ref('软件工程1班');
</script>

<style scoped>
.student-profile {
  max-width: 320px;
  margin: 40px auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px #f0f1f2;
  padding: 32px 24px;
  text-align: center;
}
.avatar-section {
  margin-bottom: 24px;
}
.avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  border: 2px solid #1677ff;
}
.info-section {
  margin-top: 16px;
}
.info-item {
  font-size: 1.1rem;
  margin: 12px 0;
}
.label {
  color: #888;
  margin-right: 8px;
}
</style> 