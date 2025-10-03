<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>水稻长势智能分析平台</span>
        </div>
      </template>
      <el-form @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" style="width: 100%;">登录</el-button>
        </el-form-item>
        <div style="text-align: center;">
          <router-link to="/register">还没有账户？立即注册</router-link>
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

const handleLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.error('请输入用户名和密码');
    return;
  }

  const formData = new URLSearchParams();
  formData.append('username', username.value);
  formData.append('password', password.value);

  try {
    const response = await apiClient.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const { access_token, role, username: loggedInUsername } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user_role', role);
    localStorage.setItem('username', loggedInUsername);
    ElMessage.success('登录成功！');
    
    // Redirect to a dashboard or home page after login
    router.push('/fields');

  } catch (error) {
    ElMessage.error('登录失败，请检查用户名或密码。');
    console.error(error);
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}
</style>
