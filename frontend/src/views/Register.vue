<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <span>注册新用户</span>
        </div>
      </template>
      <el-form @submit.prevent="handleRegister">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" style="width: 100%;">注册</el-button>
        </el-form-item>
        <div style="text-align: center;">
          <router-link to="/login">已有账户？返回登录</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api';
import { ElMessage } from 'element-plus';

const username = ref('');
const password = ref('');
const router = useRouter();

const handleRegister = async () => {
  if (!username.value || !password.value) {
    ElMessage.error('请输入用户名和密码');
    return;
  }

  try {
    await apiClient.post('/users/', {
      username: username.value,
      password: password.value,
    });
    
    ElMessage.success('注册成功！将跳转到登录页面。');
    router.push('/login');

  } catch (error: any) {
    if (error.response && error.response.data.detail) {
        ElMessage.error(`注册失败: ${error.response.data.detail}`);
    } else {
        ElMessage.error('注册失败，请稍后再试。');
    }
    console.error(error);
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.register-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}
</style>
