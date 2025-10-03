<template>
  <div class="dashboard-container">
    <!-- 顶部导航和统计概览 -->
    <div class="top-section">
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎回来，{{ username }}</h1>
        <p class="welcome-subtitle">今天是 {{ currentDate }}，让我们一起关注水稻生长状况</p>
      </div>
      
      <div class="stats-overview">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon bg-green">
                  <el-icon><Grid /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ stats.totalFields }}</div>
                  <div class="stat-label">田块总数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon bg-blue">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ stats.pendingTasks }}</div>
                  <div class="stat-label">待分析任务</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon bg-orange">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ stats.alerts }}</div>
                  <div class="stat-label">预警数量</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon bg-purple">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ stats.monthlyAnalyses }}</div>
                  <div class="stat-label">本月分析次数</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：田块地图和快速操作 -->
      <el-col :span="16">
        <el-card class="map-card">
          <template #header>
            <div class="card-header">
              <span>田块分布地图</span>
              <div class="card-actions">
                <el-button link @click="refreshMap">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
                <el-button type="primary" @click="goToFields">
                  <el-icon><Plus /></el-icon>
                  管理田块
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="map-container">
            <div class="map-placeholder">
              <el-empty description="田块地图展示区域" />
            </div>
          </div>
        </el-card>
        
        <el-card class="quick-actions-card">
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          
          <div class="quick-actions">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="action-card" shadow="hover" @click="goToUpload">
                  <div class="action-content">
                    <div class="action-icon">
                      <el-icon><Upload /></el-icon>
                    </div>
                    <h3>上传图像</h3>
                    <p>上传四张配套照片</p>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="action-card" shadow="hover" @click="goToAnalysis">
                  <div class="action-content">
                    <div class="action-icon">
                      <el-icon><DataAnalysis /></el-icon>
                    </div>
                    <h3>数据分析</h3>
                    <p>查看分析结果</p>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="action-card" shadow="hover" @click="goToReports">
                  <div class="action-content">
                    <div class="action-icon">
                      <el-icon><Document /></el-icon>
                    </div>
                    <h3>查看报告</h3>
                    <p>生成分析报告</p>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：最近活动和预警 -->
      <el-col :span="8">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
              <el-button link @click="viewAllActivities">查看全部</el-button>
            </div>
          </template>
          
          <div class="activity-list">
            <el-scrollbar height="300px">
              <el-timeline>
                <el-timeline-item
                  v-for="(activity, index) in recentActivities"
                  :key="index"
                  :timestamp="activity.time"
                  placement="top"
                >
                  <el-card>
                    <h4>{{ activity.title }}</h4>
                    <p>{{ activity.description }}</p>
                    <div class="activity-actions" v-if="activity.actions">
                      <el-button 
                        v-for="(action, actionIndex) in activity.actions" 
                        :key="actionIndex"
                        :type="action.type"
                        size="small"
                        @click="handleActivityAction(action)"
                      >
                        {{ action.text }}
                      </el-button>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-scrollbar>
          </div>
        </el-card>
        
        <el-card class="alerts-card">
          <template #header>
            <div class="card-header">
              <span>预警信息</span>
              <el-tag type="danger">{{ alerts.length }} 条</el-tag>
            </div>
          </template>
          
          <div class="alerts-list">
            <el-scrollbar height="250px">
              <div 
                v-for="(alert, index) in alerts" 
                :key="index" 
                class="alert-item"
                @click="handleAlertClick(alert)"
              >
                <div class="alert-header">
                  <el-tag :type="getAlertLevelType(alert.level)" size="small">
                    {{ getAlertLevelText(alert.level) }}
                  </el-tag>
                  <span class="alert-time">{{ alert.time }}</span>
                </div>
                <h4 class="alert-title">{{ alert.title }}</h4>
                <p class="alert-description">{{ alert.description }}</p>
              </div>
            </el-scrollbar>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表分析区域 -->
    <el-row :gutter="20" class="analysis-section">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>生长指标趋势</span>
              <div class="chart-controls">
                <el-select v-model="trendMetric" size="small">
                  <el-option label="平均株高" value="height" />
                  <el-option label="冠层覆盖度" value="coverage" />
                  <el-option label="分蘖密度" value="tiller" />
                </el-select>
                <el-date-picker
                  v-model="trendDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  size="small"
                  value-format="YYYY-MM-DD"
                />
              </div>
            </div>
          </template>
          
          <div class="chart-container">
            <div ref="trendChartRef" style="width: 100%; height: 300px;"></div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>田块对比分析</span>
              <div class="chart-controls">
                <el-select v-model="compareMetric" size="small">
                  <el-option label="平均株高" value="height" />
                  <el-option label="冠层覆盖度" value="coverage" />
                  <el-option label="亩基本苗数" value="seedlings" />
                </el-select>
              </div>
            </div>
          </template>
          
          <div class="chart-container">
            <div ref="compareChartRef" style="width: 100%; height: 300px;"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import apiClient from '../api';
import { 
  Grid, 
  Document, 
  Warning, 
  TrendCharts,
  Refresh,
  Plus,
  Upload,
  DataAnalysis,
  ArrowUp,
  ArrowDown
} from '@element-plus/icons-vue';

interface Stats {
  totalFields: number;
  pendingTasks: number;
  alerts: number;
  monthlyAnalyses: number;
}

interface Activity {
  title: string;
  description: string;
  time: string;
  actions?: ActivityAction[];
}

interface ActivityAction {
  text: string;
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  action: () => void;
}

interface Alert {
  id: number;
  title: string;
  description: string;
  time: string;
  level: 'high' | 'medium' | 'low';
  fieldId?: number;
}

const router = useRouter();
const username = ref('管理员');
const currentDate = computed(() => {
  const now = new Date();
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`;
});

const stats = ref<Stats>({
  totalFields: 8,
  pendingTasks: 3,
  alerts: 2,
  monthlyAnalyses: 24
});

const recentActivities = ref<Activity[]>([
  {
    title: '田块A完成分析',
    description: '田块A的图像分析已完成，平均株高为45.2cm',
    time: '2025-10-03 14:30',
    actions: [
      {
        text: '查看详情',
        type: 'primary',
        action: () => router.push('/fields/1')
      }
    ]
  },
  {
    title: '新田块添加',
    description: '成功添加田块B，位于江苏省泰兴市',
    time: '2025-10-02 09:15'
  },
  {
    title: '图像上传完成',
    description: '田块C的四张图像已成功上传，等待分析',
    time: '2025-10-01 16:45',
    actions: [
      {
        text: '启动分析',
        type: 'success',
        action: () => ElMessage.info('启动分析功能将在后续版本中实现')
      }
    ]
  }
]);

const alerts = ref<Alert[]>([
  {
    id: 1,
    title: '田块A株高偏低',
    description: '检测到田块A平均株高低于正常值15%，建议加强水肥管理',
    time: '2025-10-03 14:30',
    level: 'high',
    fieldId: 1
  },
  {
    id: 2,
    title: '田块B覆盖度下降',
    description: '田块B最近两次测量覆盖度下降8%，可能存在病虫害风险',
    time: '2025-10-02 09:15',
    level: 'medium',
    fieldId: 2
  }
]);

const trendMetric = ref('height');
const compareMetric = ref('height');
const trendDateRange = ref<[string, string] | null>(null);

const trendChartRef = ref<HTMLDivElement | null>(null);
const compareChartRef = ref<HTMLDivElement | null>(null);
let trendChart: echarts.ECharts | null = null;
let compareChart: echarts.ECharts | null = null;

const refreshMap = () => {
  ElMessage.info('地图刷新功能将在后续版本中实现');
};

const goToFields = () => {
  router.push('/fields');
};

const goToUpload = () => {
  router.push('/upload');
};

const goToAnalysis = () => {
  router.push('/visual-analysis/home');
};

const goToReports = () => {
  router.push('/visual-analysis/home');
};

const viewAllActivities = () => {
  ElMessage.info('查看全部活动功能将在后续版本中实现');
};

const handleActivityAction = (action: ActivityAction) => {
  action.action();
};

const handleAlertClick = (alert: Alert) => {
  if (alert.fieldId) {
    router.push(`/fields/${alert.fieldId}`);
  } else {
    ElMessage.info('查看详情功能将在后续版本中实现');
  }
};

const getAlertLevelType = (level: string) => {
  switch (level) {
    case 'high': return 'danger';
    case 'medium': return 'warning';
    case 'low': return 'info';
    default: return 'info';
  }
};

const getAlertLevelText = (level: string) => {
  switch (level) {
    case 'high': return '严重';
    case 'medium': return '中等';
    case 'low': return '轻微';
    default: return '一般';
  }
};

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value);
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['9/15', '9/22', '9/29', '10/6', '10/13']
      },
      yAxis: {
        type: 'value',
        name: '株高 (cm)'
      },
      series: [{
        data: [42, 43.5, 44.2, 44.8, 45.2],
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#4CAF50'
        }
      }]
    };
    trendChart.setOption(option);
  }
  
  if (compareChartRef.value) {
    compareChart = echarts.init(compareChartRef.value);
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['田块A', '田块B', '田块C', '田块D', '田块E']
      },
      yAxis: {
        type: 'value',
        name: '平均株高 (cm)'
      },
      series: [{
        data: [45.2, 47.8, 43.5, 46.1, 44.9],
        type: 'bar',
        itemStyle: {
          color: '#2196F3'
        }
      }]
    };
    compareChart.setOption(option);
  }
};

onMounted(() => {
  initCharts();
  
  // 获取真实用户名
  username.value = localStorage.getItem('username') || '管理员';
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    if (trendChart) trendChart.resize();
    if (compareChart) compareChart.resize();
  });
});
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: var(--light-gray);
  min-height: 100%;
}

.top-section {
  margin-bottom: 20px;
}

.welcome-section {
  margin-bottom: 20px;
}

.welcome-title {
  margin: 0 0 10px 0;
  color: var(--primary-green-dark);
  font-size: 28px;
  font-weight: 600;
}

.welcome-subtitle {
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0;
}

.stats-overview {
  margin-top: 20px;
}

.stat-card {
  border-radius: 8px;
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  font-size: 24px;
  margin-right: 15px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--white);
}

.bg-green {
  background-color: var(--primary-green);
}

.bg-blue {
  background-color: #2196F3;
}

.bg-orange {
  background-color: #FF9800;
}

.bg-purple {
  background-color: #9C27B0;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: var(--primary-green-dark);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.main-content {
  margin-bottom: 20px;
}

.map-card, .quick-actions-card, .activity-card, .alerts-card, .chart-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: var(--primary-green-dark);
  font-size: 18px;
}

.map-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--white);
  border-radius: 4px;
}

.quick-actions {
  padding: 20px 0;
}

.action-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border-radius: 8px;
  height: 150px;
}

.action-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.action-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.action-icon {
  font-size: 32px;
  color: var(--primary-green);
  margin-bottom: 15px;
}

.action-content h3 {
  margin: 0 0 10px 0;
  color: var(--primary-green-dark);
  font-size: 18px;
}

.action-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.activity-list, .alerts-list {
  max-height: 300px;
  overflow-y: auto;
}

.activity-actions {
  margin-top: 10px;
}

.alert-item {
  padding: 15px 0;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.2s;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-item:hover {
  background-color: var(--light-gray);
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.alert-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.alert-title {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: var(--text-primary);
}

.alert-description {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.analysis-section {
  margin-bottom: 20px;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.chart-controls .el-select, .chart-controls .el-date-picker {
  width: 120px;
}

.chart-container {
  margin-top: 20px;
}

:deep(.el-card__header) {
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
  border-radius: 8px 8px 0 0;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>