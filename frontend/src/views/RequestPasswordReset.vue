<template>
  <div class="app-container">
    <h1>重置密码</h1>
    <el-card>
      <el-form :model="form" label-width="120px" style="max-width: 600px" @submit.prevent="handleSubmit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入您的用户名"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">发送重置链接</el-button>
        </el-form-item>
      </el-form>
      <div v-if="message">{{ message }}</div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue';
import apiClient from '../api';
import { ElMessage } from 'element-plus';

const form = reactive({
  username: '',
});

const message = ref('');

const handleSubmit = async () => {
  if (!form.username) {
    ElMessage.error('请输入用户名');
    return;
  }
  try {
    const response = await apiClient.post(`/password-recovery/${form.username}`);
    message.value = response.data.message;
    ElMessage.success('请求成功，请查看服务器控制台获取重置令牌。');
  } catch (error: any) {
    message.value = error.response?.data?.detail || '请求失败';
    ElMessage.error(message.value);
  }
};
</script>

<style scoped>
.app-container {
    padding: 20px;
}
</style>
