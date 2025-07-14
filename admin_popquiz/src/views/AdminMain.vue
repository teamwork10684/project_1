<template>
  <div class="admin-main">
    <h1>管理员后台</h1>
    <section class="admin-section">
      <h2>用户信息</h2>
      <table class="admin-table">
        <thead>
          <tr>
            <th>用户ID</th>
            <th>用户名</th>
            <th>邮箱</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1</td>
            <td>张三</td>
            <td>zhangsan@example.com</td>
          </tr>
          <tr>
            <td>2</td>
            <td>李四</td>
            <td>lisi@example.com</td>
          </tr>
        </tbody>
      </table>
    </section>
    <section class="admin-section">
      <h2>演讲信息</h2>
      <table class="admin-table">
        <thead>
          <tr>
            <th>演讲ID</th>
            <th>主题</th>
            <th>发言人</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>101</td>
            <td>AI 发展趋势</td>
            <td>王五</td>
          </tr>
          <tr>
            <td>102</td>
            <td>前端技术</td>
            <td>赵六</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
</script>

<style scoped>
.admin-main {
  max-width: 900px;
  margin: 40px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #f0f1f2;
}
.admin-section {
  margin-bottom: 32px;
}
.admin-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}
.admin-table th, .admin-table td {
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  text-align: left;
}
.admin-table th {
  background: #f5f7fa;
}
</style> 