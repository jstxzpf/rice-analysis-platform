<template>
  <div class="visual-analysis-container">
    <!-- 页面标题和导航 -->
    <div class="page-header">
      <div class="header-content">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>首页</el-breadcrumb-item>
            <el-breadcrumb-item>数据可视化</el-breadcrumb-item>
            <el-breadcrumb-item>分析中心</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1 class="page-title">数据可视化分析中心</h1>
        <p class="page-description">通过多种可视化方式深入分析水稻生长数据</p>
      </div>
      
      <div class="header-actions">
        <el-select 
          v-model="selectedField" 
          placeholder="选择田块" 
          class="field-selector"
          clearable
        >
          <el-option 
            v-for="field in fields" 
            :key="field.id" 
            :label="field.name" 
            :value="field.id"
          />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="date-range-picker"
        />
        
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 快速访问卡片 -->
    <el-row :gutter="20" class="quick-access-cards">
      <el-col :span="6">
        <el-card class="quick-card" shadow="hover" @click="goToHeatmap">
          <div class="card-content">
            <div class="card-icon bg-green">
              <el-icon><HotWater /></el-icon>
            </div>
            <div class="card-info">
              <h3>生长热力图</h3>
              <p>空间分布可视化</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="quick-card" shadow="hover" @click="goToRegionalDifferences">
          <div class="card-content">
            <div class="card-icon bg-blue">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="card-info">
              <h3>区域差异分析</h3>
              <p>田块内对比</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="quick-card" shadow="hover" @click="goToInterField">
          <div class="card-content">
            <div class="card-icon bg-purple">
              <el-icon><PieChart /></el-icon>
            </div>
            <div class="card-info">
              <h3>田块对比分析</h3>
              <p>跨田块对比</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="quick-card" shadow="hover" @click="goToIntraField">
          <div class="card-content">
            <div class="card-icon bg-orange">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="card-info">
              <h3>趋势分析</h3>
              <p>时间序列分析</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 综合仪表盘 -->
    <el-row :gutter="20" class="dashboard-section">
      <el-col :span="16">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>关键指标概览</span>
              <el-button link @click="goToDetailedAnalysis">
                <el-icon><DataAnalysis /></el-icon>
                详细分析
              </el-button>
            </div>
          </template>
          
          <div class="dashboard-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="metric-card">
                  <div class="metric-value">{{ stats.avgHeight }}<span class="unit">cm</span></div>
                  <div class="metric-label">平均株高</div>
                  <div class="metric-trend positive">
                    <el-icon><ArrowUp /></el-icon>
                    +2.3%
                  </div>
                </div>
              </el-col>
              
              <el-col :span="8">
                <div class="metric-card">
                  <div class="metric-value">{{ stats.coverage }}<span class="unit">%</span></div>
                  <div class="metric-label">冠层覆盖度</div>
                  <div class="metric-trend positive">
                    <el-icon><ArrowUp /></el-icon>
                    +1.7%
                  </div>
                </div>
              </el-col>
              
              <el-col :span="8">
                <div class="metric-card">
                  <div class="metric-value">{{ stats.seedlingsPerMu }}<span class="unit">株/亩</span></div>
                  <div class="metric-label">亩基本苗数</div>
                  <div class="metric-trend negative">
                    <el-icon><ArrowDown /></el-icon>
                    -0.5%
                  </div>
                </div>
              </el-col>
            </el-row>
            
            <div class="chart-container">
              <div ref="trendChartRef" style="width: 100%; height: 300px;"></div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="alert-card">
          <template #header>
            <div class="card-header">
              <span>预警信息</span>
              <el-tag type="danger">{{ alerts.length }} 条</el-tag>
            </div>
          </template>
          
          <div class="alert-content">
            <el-scrollbar height="380px">
              <el-timeline>
                <el-timeline-item
                  v-for="(alert, index) in alerts"
                  :key="index"
                  :timestamp="alert.time"
                  placement="top"
                  :type="getAlertType(alert.level)"
                >
                  <el-card>
                    <h4>{{ alert.title }}</h4>
                    <p>{{ alert.description }}</p>
                    <div class="alert-actions">
                      <el-button 
                        size="small" 
                        :type="getAlertButtonType(alert.level)"
                        @click="handleAlertAction(alert)"
                      >
                        {{ alert.action }}
                      </el-button>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-scrollbar>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表展示区 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>生长指标分布</span>
              <div class="chart-controls">
                <el-select v-model="distributionMetric" size="small">
                  <el-option label="株高分布" value="height" />
                  <el-option label="覆盖度分布" value="coverage" />
                  <el-option label="分蘖密度分布" value="tiller" />
                </el-select>
              </div>
            </div>
          </template>
          
          <div class="chart-container">
            <div ref="distributionChartRef" style="width: 100%; height: 350px;"></div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>指标相关性分析</span>
              <div class="chart-controls">
                <el-select v-model="correlationMetricX" size="small">
                  <el-option label="株高" value="height" />
                  <el-option label="覆盖度" value="coverage" />
                </el-select>
                <el-select v-model="correlationMetricY" size="small">
                  <el-option label="分蘖密度" value="tiller" />
                  <el-option label="颜色指数" value="color" />
                </el-select>
              </div>
            </div>
          </template>
          
          <div class="chart-container">
            <div ref="correlationChartRef" style="width: 100%; height: 350px;"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import apiClient from '../api';
import { 
  HotWater, 
  DataLine, 
  PieChart, 
  TrendCharts,
  DataAnalysis,
  Refresh,
  ArrowUp,
  ArrowDown
} from '@element-plus/icons-vue';

interface Field {
  id: number;
  name: string;
}

interface Alert {
  id: number;
  title: string;
  description: string;
  time: string;
  level: 'high' | 'medium' | 'low';
  action: string;
  fieldId?: number;
}

interface Stats {
  avgHeight: number;
  coverage: number;
  seedlingsPerMu: number;
}

const router = useRouter();
const fields = ref<Field[]>([]);
const selectedField = ref<number | null>(null);
const dateRange = ref<[string, string] | null>(null);
const distributionMetric = ref('height');
const correlationMetricX = ref('height');
const correlationMetricY = ref('tiller');

const stats = ref<Stats>({
  avgHeight: 45.2,
  coverage: 72.5,
  seedlingsPerMu: 18500
});

const alerts = ref<Alert[]>([
  {
    id: 1,
    title: '田块A株高偏低',
    description: '检测到田块A平均株高低于正常值15%，建议加强水肥管理',
    time: '2025-10-03 14:30',
    level: 'high',
    action: '查看详情',
    fieldId: 1
  },
  {
    id: 2,
    title: '田块B覆盖度下降',
    description: '田块B最近两次测量覆盖度下降8%，可能存在病虫害风险',
    time: '2025-10-02 09:15',
    level: 'medium',
    action: '查看分析',
    fieldId: 2
  },
  {
    id: 3,
    title: '田块C图像质量不佳',
    description: '田块C最新上传的3米侧拍图清晰度不足，影响分析精度',
    time: '2025-10-01 16:45',
    level: 'low',
    action: '重新上传',
    fieldId: 3
  }
]);

const trendChartRef = ref<HTMLDivElement | null>(null);
const distributionChartRef = ref<HTMLDivElement | null>(null);
const correlationChartRef = ref<HTMLDivElement | null>(null);
let trendChart: echarts.ECharts | null = null;
let distributionChart: echarts.ECharts | null = null;
let correlationChart: echarts.ECharts | null = null;

const fetchFields = async () => {
  try {
    const response = await apiClient.get('/fields/');
    fields.value = response.data;
  } catch (error) {
    ElMessage.error('获取田块列表失败');
    console.error(error);
  }
};

const refreshData = () => {
  ElMessage.info('数据刷新功能将在后续版本中实现');
};

const goToHeatmap = () => {
  router.push('/visual-analysis/heatmap');
};

const goToRegionalDifferences = () => {
  router.push('/visual-analysis/regional-differences');
};

const goToInterField = () => {
  router.push('/visual-analysis/inter-field');
};

const goToIntraField = () => {
  router.push('/visual-analysis/intra-field');
};

const goToDetailedAnalysis = () => {
  if (selectedField.value) {
    router.push(`/fields/${selectedField.value}/trends`);
  } else {
    ElMessage.warning('请先选择一个田块');
  }
};

const handleAlertAction = (alert: Alert) => {
  if (alert.fieldId) {
    router.push(`/fields/${alert.fieldId}`);
  } else {
    ElMessage.info('查看详情功能将在后续版本中实现');
  }
};

const getAlertType = (level: string) => {
  switch (level) {
    case 'high': return 'danger';
    case 'medium': return 'warning';
    case 'low': return 'info';
    default: return 'info';
  }
};

const getAlertButtonType = (level: string) => {
  switch (level) {
    case 'high': return 'danger';
    case 'medium': return 'warning';
    case 'low': return 'info';
    default: return 'primary';
  }
};

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value);
    const option = {
      title: {
        text: '株高变化趋势'
      },
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
  
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value);
    const option = {
      title: {
        text: '株高分布直方图'
      },
      tooltip: {},
      xAxis: {
        type: 'category',
        data: ['35-40', '40-45', '45-50', '50-55', '55-60']
      },
      yAxis: {
        type: 'value',
        name: '频次'
      },
      series: [{
        data: [12, 28, 35, 18, 7],
        type: 'bar',
        itemStyle: {
          color: '#2196F3'
        }
      }]
    };
    distributionChart.setOption(option);
  }
  
  if (correlationChartRef.value) {
    correlationChart = echarts.init(correlationChartRef.value);
    const option = {
      title: {
        text: '株高与覆盖度相关性'
      },
      tooltip: {
        position: 'top'
      },
      xAxis: {
        type: 'value',
        name: '株高 (cm)'
      },
      yAxis: {
        type: 'value',
        name: '覆盖度 (%)'
      },
      series: [{
        data: [
          [42, 68], [43, 70], [44, 72], [45, 74], [46, 75],
          [43.5, 69], [44.5, 73], [45.5, 76], [46.5, 78], [47, 80]
        ],
        type: 'scatter',
        symbolSize: 20,
        itemStyle: {
          color: '#FF9800'
        }
      }]
    };
    correlationChart.setOption(option);
  }
};

onMounted(() => {
  fetchFields();
  initCharts();
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    if (trendChart) trendChart.resize();
    if (distributionChart) distributionChart.resize();
    if (correlationChart) correlationChart.resize();
  });
});

// 监听指标变化，更新图表
watch([distributionMetric, correlationMetricX, correlationMetricY], () => {
  ElMessage.info('图表更新功能将在后续版本中实现');
});
</script>

<style scoped>
.visual-analysis-container {
  padding: 20px;
  background-color: var(--light-gray);
  min-height: 100%;
}

.page-header {
  background-color: var(--white);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-content {
  margin-bottom: 20px;
}

.breadcrumb {
  margin-bottom: 10px;
}

.page-title {
  margin: 0 0 10px 0;
  color: var(--primary-green-dark);
  font-size: 28px;
  font-weight: 600;
}

.page-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.field-selector {
  width: 200px;
}

.date-range-picker {
  width: 300px;
}

.quick-access-cards {
  margin-bottom: 20px;
}

.quick-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border-radius: 8px;
}

.quick-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.card-content {
  display: flex;
  align-items: center;
  padding: 20px;
}

.card-icon {
  font-size: 24px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-right: 15px;
  color: var(--white);
}

.bg-green {
  background-color: var(--primary-green);
}

.bg-blue {
  background-color: #2196F3;
}

.bg-purple {
  background-color: #9C27B0;
}

.bg-orange {
  background-color: #FF9800;
}

.card-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: var(--text-primary);
}

.card-info p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.dashboard-section {
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

.dashboard-card, .alert-card, .chart-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.metric-card {
  text-align: center;
  padding: 20px;
  background-color: var(--light-gray);
  border-radius: 8px;
  margin-bottom: 20px;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--primary-green-dark);
}

.unit {
  font-size: 16px;
  margin-left: 5px;
}

.metric-label {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 10px 0;
}

.metric-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.positive {
  color: #4CAF50;
}

.negative {
  color: #F44336;
}

.chart-container {
  margin-top: 20px;
}

.charts-section {
  margin-bottom: 20px;
}

.alert-content {
  max-height: 400px;
  overflow-y: auto;
}

.alert-actions {
  margin-top: 10px;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.chart-controls .el-select {
  width: 120px;
}

:deep(.el-card__header) {
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-timeline-item__tail) {
  border-left: 2px solid var(--border-color);
}

:deep(.el-timeline-item__node) {
  width: 12px;
  height: 12px;
}
</style>