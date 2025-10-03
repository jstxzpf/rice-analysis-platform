<template>
  <div class="app-container">
    <h1>用户管理</h1>
    <el-table :data="users" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="username" label="用户名"></el-table-column>
      <el-table-column prop="role" label="角色"></el-table-column>
      <el-table-column prop="created_at" label="注册时间"></el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';
import { ElMessage } from 'element-plus';

interface User {
  id: number;
  username: string;
  role: string;
  created_at: string;
}

const users = ref<User[]>([]);
const loading = ref(true);

const fetchUsers = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/users/');
    users.value = response.data;
  } catch (error) {
    ElMessage.error('获取用户列表失败，请确保您有管理员权限。');
  } finally {
    loading.value = false;
  }
};

onMounted(fetchUsers);
</script>

<style scoped>
.app-container {
    padding: 20px;
}
</style>
