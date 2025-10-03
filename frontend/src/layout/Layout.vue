<template>
  <el-container class="main-container">
    <el-aside width="250px">
      <div class="logo-container">
        <h2 class="logo-text">水稻分析平台</h2>
      </div>
      <el-menu
        class="side-menu"
        :default-active="$route.path"
        :default-openeds="['1']"
        router
        :collapse="isCollapse"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>主面板</span>
        </el-menu-item>
        <el-menu-item index="/fields">
          <el-icon><Grid /></el-icon>
          <span>田块管理</span>
        </el-menu-item>
        <el-menu-item index="/upload">
          <el-icon><UploadFilled /></el-icon>
          <span>数据上传</span>
        </el-menu-item>
        
        <el-sub-menu index="visual-analysis">
          <template #title>
            <el-icon><Histogram /></el-icon>
            <span>可视化分析</span>
          </template>
          <el-menu-item index="/visual-analysis/home">
            <el-icon><DataAnalysis /></el-icon>
            <span>分析概览</span>
          </el-menu-item>
          <el-menu-item index="/visual-analysis/heatmap">
            <el-icon><HotWater /></el-icon>
            <span>生长热力图</span>
          </el-menu-item>
          <el-menu-item index="/visual-analysis/regional-differences">
            <el-icon><DataLine /></el-icon>
            <span>区域差异分析</span>
          </el-menu-item>
          <el-menu-item index="/visual-analysis/inter-field">
            <el-icon><PieChart /></el-icon>
            <span>田块对比分析</span>
          </el-menu-item>
          <el-menu-item index="/visual-analysis/intra-field">
            <el-icon><TrendCharts /></el-icon>
            <span>田块内部对比</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item v-if="isAdmin" index="/user-management">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <el-button class="menu-toggle" @click="toggleCollapse">
            <el-icon><Menu /></el-icon>
          </el-button>
          <div class="user-info">
            <el-dropdown>
              <span class="user-name">
                {{ username || '用户' }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElNotification } from 'element-plus';
import { 
  House, 
  Grid, 
  UploadFilled, 
  Histogram, 
  HotWater, 
  DataLine, 
  PieChart, 
  TrendCharts, 
  User, 
  Menu, 
  ArrowDown,
  DataAnalysis
} from '@element-plus/icons-vue';

const router = useRouter();
const username = ref('');
const isAdmin = ref(false);
const isCollapse = ref(false);

onMounted(() => {
  username.value = localStorage.getItem('username') || '';
  isAdmin.value = localStorage.getItem('user_role') === 'admin';
});

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');
  localStorage.removeItem('username');
  router.push('/login');
  ElMessage.success('您已成功退出登录');
};
</script>

<style scoped>
.main-container {
  height: 100vh;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-green-dark);
  color: white;
  border-bottom: 1px solid var(--medium-gray);
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
  text-align: center;
}

.side-menu {
  height: calc(100vh - 60px);
  border-right: 1px solid var(--medium-gray);
}

.header {
  padding: 0 !important;
  background-color: var(--white);
  border-bottom: 1px solid var(--medium-gray);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.menu-toggle {
  background-color: var(--primary-green);
  color: white;
  border: none;
  border-radius: 4px;
}

.menu-toggle:hover {
  background-color: var(--primary-green-dark);
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  cursor: pointer;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  font-weight: 500;
}

.main-content {
  background-color: var(--light-gray);
  padding: 0 !important;
}

:deep(.el-aside) {
  background-color: var(--white);
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
}

:deep(.el-menu) {
  border-right: none;
  background-color: transparent;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 4px;
  color: var(--text-primary);
}

:deep(.el-menu-item.is-active) {
  background-color: var(--primary-green-light) !important;
  color: white !important;
  border-radius: 4px;
}

:deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 4px;
  color: var(--text-primary);
}

:deep(.el-sub-menu__title:hover) {
  background-color: var(--light-gray);
  color: var(--primary-green-dark);
}

:deep(.el-sub-menu .el-menu-item) {
  margin: 0 8px 4px 8px;
  height: 44px;
  line-height: 44px;
}
</style>
