<template>
  <div class="login-container">
    <!-- 品牌Logo区域 -->
    <div class="brand-section">
      <div class="logo">
        <svg width="80" height="80" viewBox="0 0 100 100">
          <rect x="10" y="10" width="80" height="80" rx="15" fill="#4CAF50" />
          <circle cx="30" cy="30" r="8" fill="#8BC34A" />
          <circle cx="70" cy="30" r="8" fill="#8BC34A" />
          <circle cx="50" cy="70" r="12" fill="#8BC34A" />
        </svg>
      </div>
      <h1 class="platform-name">水稻分析平台</h1>
      <p class="platform-desc">江苏泰兴水稻长势智能分析系统</p>
    </div>

    <!-- 登录表单区域 -->
    <div class="login-section">
      <el-card class="login-card" shadow="always">
        <template #header>
          <div class="card-header">
            <h2>用户登录</h2>
          </div>
        </template>
        
        <el-form 
          ref="loginFormRef" 
          :model="loginForm" 
          :rules="loginRules" 
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名" 
              size="large"
              clearable
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码" 
              size="large"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <router-link to="/request-password-reset" class="forgot-password">
              忘记密码？
            </router-link>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              native-type="submit" 
              size="large" 
              :loading="loading"
              style="width: 100%;"
            >
              登录
            </el-button>
          </el-form-item>
          
          <div class="register-link">
            <span>还没有账户？</span>
            <router-link to="/register">立即注册</router-link>
          </div>
        </el-form>
      </el-card>
      
      <!-- 语言切换 -->
      <!-- 移除了语言切换功能，如果需要可重新添加 -->
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance } from 'element-plus';
import apiClient from '../api';
import { 
  User, 
  Lock, 
  ArrowDown
} from '@element-plus/icons-vue';

interface LoginForm {
  username: string;
  password: string;
}

const router = useRouter();
const loginFormRef = ref<FormInstance>();
const loading = ref(false);
const rememberMe = ref(false);

const loginForm = ref<LoginForm>({
  username: '',
  password: ''
});

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位字符', trigger: 'blur' }
  ]
};

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  const valid = await loginFormRef.value.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;

  const formData = new URLSearchParams();
  formData.append('username', loginForm.value.username);
  formData.append('password', loginForm.value.password);

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
    
    // 如果选择了"记住我"，则保存用户名
    if (rememberMe.value) {
      localStorage.setItem('saved_username', loginForm.value.username);
    } else {
      localStorage.removeItem('saved_username');
    }
    
    ElMessage.success('登录成功！');
    
    // 重定向到仪表盘
    router.push('/dashboard');

  } catch (error) {
    ElMessage.error('登录失败，请检查用户名或密码。');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 页面加载时恢复保存的用户名
onMounted(() => {
  const savedUsername = localStorage.getItem('saved_username');
  if (savedUsername) {
    loginForm.value.username = savedUsername;
    rememberMe.value = true;
  }
});
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
}

.brand-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  padding: 40px;
  background: rgba(0, 0, 0, 0.2);
}

.logo {
  margin-bottom: 30px;
}

.platform-name {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 10px;
  text-align: center;
}

.platform-desc {
  font-size: 18px;
  opacity: 0.9;
  text-align: center;
}

.login-section {
  width: 450px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: white;
  padding: 40px 20px;
  position: relative;
}

.login-card {
  width: 100%;
  max-width: 380px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-header {
  text-align: center;
  padding: 20px 0;
}

.card-header h2 {
  margin: 0;
  color: var(--primary-green-dark);
  font-weight: 600;
}

.login-form {
  padding: 0 20px 20px;
}

.forgot-password {
  float: right;
  font-size: 14px;
  color: var(--primary-green);
  text-decoration: none;
}

.forgot-password:hover {
  color: var(--primary-green-dark);
  text-decoration: underline;
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.register-link a {
  color: var(--primary-green);
  text-decoration: none;
  margin-left: 5px;
}

.register-link a:hover {
  text-decoration: underline;
}

.language-switch {
  position: absolute;
  bottom: 20px;
  right: 20px;
}

.el-dropdown-link {
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  font-size: 14px;
}

.el-dropdown-link .el-icon {
  margin-right: 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .brand-section {
    display: none;
  }
  
  .login-section {
    width: 100%;
    padding: 20px;
  }
  
  .login-card {
    max-width: none;
    margin: 0 20px;
  }
}
</style>
