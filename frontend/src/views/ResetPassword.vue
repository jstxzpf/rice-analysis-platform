<template>
  <div class="app-container">
    <h1>设置新密码</h1>
    <el-card>
      <el-form :model="form" label-width="120px" style="max-width: 600px" @submit.prevent="handleSubmit">
        <el-form-item label="重置令牌">
          <el-input v-model="form.token" placeholder="请输入从控制台获取的令牌"></el-input>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input type="password" v-model="form.new_password" placeholder="请输入您的新密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">更新密码</el-button>
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
  token: '',
  new_password: '',
});

const message = ref('');

const handleSubmit = async () => {
  if (!form.token || !form.new_password) {
    ElMessage.error('请填写所有字段');
    return;
  }
  try {
    const response = await apiClient.post('/reset-password/', {
      token: form.token,
      new_password: form.new_password,
    });
    message.value = response.data.message;
    ElMessage.success('密码更新成功！');
  } catch (error: any) {
    message.value = error.response?.data?.detail || '密码更新失败';
    ElMessage.error(message.value);
  }
};
</script>

<style scoped>
.app-container {
    padding: 20px;
}
</style>
