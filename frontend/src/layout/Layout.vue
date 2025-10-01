<template>
  <el-container style="height: 100vh;">
    <el-aside width="200px" style="background-color: #545c64;">
      <el-menu
        active-text-color="#ffd04b"
        background-color="#545c64"
        class="el-menu-vertical-demo"
        default-active="/fields"
        text-color="#fff"
        router
      >
        <el-menu-item index="/dashboard">
          <span>主面板</span>
        </el-menu-item>
        <el-menu-item index="/fields">
          <span>田块管理</span>
        </el-menu-item>
         <el-menu-item index="/upload">
          <span>数据上传</span>
        </el-menu-item>
        <el-menu-item index="/visual-analysis/home">
          <span>可视化分析</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="text-align: right; font-size: 14px">
        <div class="toolbar">
          <el-dropdown>
            <span class="el-dropdown-link">
              {{ currentUser.username || '用户' }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api';
import { ElMessage } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter();
const currentUser = ref({ username: '' });

const fetchCurrentUser = async () => {
    try {
        const response = await apiClient.get('/users/me');
        currentUser.value = response.data;
    } catch (error) {
        console.error("获取当前用户信息失败", error);
        // May redirect to login if token is invalid
        localStorage.removeItem('access_token');
        router.push('/login');
    }
};

onMounted(fetchCurrentUser);

const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/login');
    ElMessage.success('您已成功退出登录');
};
</script>

<style scoped>
.el-header {
  background-color: #b3c0d1;
  color: var(--el-text-color-primary);
  line-height: 60px;
}
.el-aside {
    color: var(--el-text-color-primary);
}
.el-menu {
    border-right: none;
}
.el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
</style>
