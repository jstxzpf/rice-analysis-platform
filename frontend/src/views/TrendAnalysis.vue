<template>
  <div class="trend-container">
    <h1>趋势分析</h1>
    
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span>趋势分析筛选</span>
        </div>
      </template>
      <el-form :model="form" inline>
        <el-form-item label="选择田块">
          <el-select 
            v-model="form.field_id" 
            placeholder="请选择田块" 
            @change="loadData" 
            style="width: 200px;"
          >
            <el-option 
              v-for="field in fields" 
              :key="field.id" 
              :label="field.name" 
              :value="field.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="选择指标">
          <el-select 
            v-model="form.indicator" 
            placeholder="请选择指标" 
            @change="loadData" 
            style="width: 180px;"
          >
            <el-option label="平均株高" value="avg_plant_height"></el-option>
            <el-option label="覆盖度" value="coverage"></el-option>
            <el-option label="冠层颜色指数" value="canopy_color_index"></el-option>
            <el-option label="均匀度指数" value="uniformity_index"></el-option>
            <el-option label="分蘖密度" value="tiller_density_estimate"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="开始日期">
          <el-date-picker 
            v-model="form.start_date" 
            type="date" 
            placeholder="选择开始日期" 
            @change="loadData"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="结束日期">
          <el-date-picker 
            v-model="form.end_date" 
            type="date" 
            placeholder="选择结束日期" 
            @change="loadData"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="loadData" 
            :icon="Search" 
            :loading="loading"
          >加载数据</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="chartData.length > 0" class="chart-card">
      <template #header>
        <div class="chart-header">
          <span>{{ fields.find(f => f.id === form.field_id)?.name }} - {{ indicatorLabels[form.indicator] || form.indicator }} 趋势分析</span>
        </div>
      </template>
      <div ref="chart" class="chart-container"></div>
    </el-card>
    
    <el-card v-else class="no-data-card">
      <div class="no-data-content">
        <el-empty description="请选择田块和指标以查看趋势分析" />
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import apiClient from '../api';
import { ElMessage } from 'element-plus';
import { 
  GridComponent, 
  TooltipComponent, 
  LegendComponent,
  DataZoomComponent
} from 'echarts/components';
import { LineChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import { Search } from '@element-plus/icons-vue';

// 注册ECharts组件
echarts.use([
  GridComponent,
  TooltipComponent,
  LegendComponent,
  LineChart,
  CanvasRenderer,
  DataZoomComponent
]);

interface Field {
  id: number;
  name: string;
}

interface ChartDataItem {
  date: string;
  value: number;
}

interface Form {
  field_id: number | null;
  indicator: string;
  start_date: string | null;
  end_date: string | null;
}

interface AnalysisResult {
  id: number;
  coverage: number | null;
  avg_plant_height: number | null;
  canopy_color_index: number | null;
  uniformity_index: number | null;
  tiller_density_estimate: number | null;
  photo_group: {
    capture_date: string;
  };
}

const fields = ref<Field[]>([]);
const chart = ref<HTMLElement | null>(null);
const chartData = ref<ChartDataItem[]>([]);
const form = ref<Form>({
  field_id: null,
  indicator: 'avg_plant_height',
  start_date: null,
  end_date: null
});
const loading = ref(false);

const indicatorLabels: Record<string, string> = {
  'avg_plant_height': '平均株高 (cm)',
  'coverage': '覆盖度 (%)',
  'canopy_color_index': '冠层颜色指数',
  'uniformity_index': '均匀度指数',
  'tiller_density_estimate': '分蘖密度 (株/m²)'
};

const fetchFields = async () => {
  try {
    const response = await apiClient.get('/fields/');
    fields.value = response.data;
  } catch (error) {
    ElMessage.error('获取田块列表失败');
    console.error(error);
  }
};

const loadData = async () => {
  if (!form.value.field_id) {
    ElMessage.warning('请选择田块');
    return;
  }
  
  loading.value = true;

  try {
    const response = await apiClient.get(`/fields/${form.value.field_id}/results`);
    const results = response.data as AnalysisResult[];
    
    // 根据选择的指标提取数据
    chartData.value = results
      .filter(result => result[form.value.indicator as keyof AnalysisResult] !== null)
      .map(result => ({
        date: result.photo_group.capture_date,
        value: result[form.value.indicator as keyof AnalysisResult] as number
      }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()); // 按日期排序
    
    renderChart();
  } catch (error) {
    ElMessage.error('加载趋势数据失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const renderChart = () => {
  if (!chart.value) return;
  
  const myChart = echarts.init(chart.value);
  
  // 简单的趋势预测：使用线性回归预测下两个点
  let predictedData: ChartDataItem[] = [];
  if (chartData.value.length >= 2) {
    const values = chartData.value.map(item => item.value);
    const dates = chartData.value.map(item => item.date);
    
    // 简单的线性预测（仅用于演示）
    const n = values.length;
    let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
    for (let i = 0; i < n; i++) {
      sumX += i;
      sumY += values[i];
      sumXY += i * values[i];
      sumXX += i * i;
    }
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // 预测接下来的2个点
    for (let i = n; i < n + 2; i++) {
      const predictedValue = slope * i + intercept;
      // 对覆盖度预测值限制在合理范围内
      const clampedValue = form.value.indicator === 'coverage' 
        ? Math.max(0, Math.min(100, predictedValue)) 
        : Math.max(0, predictedValue);
      
      // 计算预测日期（根据实际日期间隔计算）
      if (dates.length >= 2) {
        // 计算平均日期间隔
        const lastDate = new Date(dates[dates.length - 1]);
        const prevDate = new Date(dates[dates.length - 2]);
        const diffTime = Math.abs(lastDate.getTime() - prevDate.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); // 转换为天数
        
        // 根据平均间隔推算预测日期
        const nextDate = new Date(lastDate);
        nextDate.setDate(nextDate.getDate() + diffDays * (i - n + 1));
        const nextDateStr = nextDate.toISOString().split('T')[0];
        
        predictedData.push({
          date: nextDateStr,
          value: clampedValue
        });
      } else {
        // 如果日期不足，使用固定间隔（7天）
        const lastDate = new Date(dates[dates.length - 1]);
        lastDate.setDate(lastDate.getDate() + 7 * (i - n + 1));
        const nextDate = lastDate.toISOString().split('T')[0];
        
        predictedData.push({
          date: nextDate,
          value: clampedValue
        });
      }
    }
  }

  // 准备理想范围数据（仅对覆盖度）
  let idealRangeData: number[] = [];
  if (form.value.indicator === 'coverage') {
    // 水稻覆盖度的理想范围
    for (let i = 0; i < chartData.value.length + predictedData.length; i++) {
      // 简单的理想范围：根据生长期变化
      idealRangeData.push(80); // 上限
    }
  }

  const option = {
    title: {
      text: `${fields.value.find(f => f.id === form.value.field_id)?.name} - ${indicatorLabels[form.value.indicator] || form.value.indicator} 趋势`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        let result = params[0].axisValue + '<br/>';
        params.forEach((param: any) => {
          if (param.value !== null && param.value !== undefined) {
            result += param.seriesName + ': ' + param.value.toFixed(2) + '<br/>';
          }
        });
        return result;
      }
    },
    legend: {
      data: [
        indicatorLabels[form.value.indicator] || form.value.indicator,
        ...(form.value.indicator === 'coverage' ? ['理想覆盖度上限'] : []),
        ...(predictedData.length > 0 ? ['预测值'] : [])
      ],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [...chartData.value.map(item => item.date), ...predictedData.map(item => item.date + ' (预测)')]
    },
    yAxis: {
      type: 'value',
      name: indicatorLabels[form.value.indicator] || form.value.indicator
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 100
      }
    ],
    graphic: [], // 用于高亮显示选中的点
    series: [
      {
        name: indicatorLabels[form.value.indicator] || form.value.indicator,
        type: 'line',
        data: [...chartData.value.map(item => item.value), ...predictedData.map(item => item.value)],
        lineStyle: {
          color: '#5470c6'
        },
        itemStyle: {
          color: '#5470c6'
        }
      },
      ...(form.value.indicator === 'coverage' ? [{
        name: '理想覆盖度上限',
        type: 'line',
        data: idealRangeData,
        lineStyle: {
          color: '#946fb4',
          type: 'dashed'
        },
        itemStyle: {
          color: '#946fb4'
        },
        silent: true
      }] : []),
      ...(predictedData.length > 0 ? [{
        name: '预测值',
        type: 'line',
        data: Array(chartData.value.length).fill(null).concat(predictedData.map(item => item.value)),
        lineStyle: {
          color: '#fac858',
          type: 'dashed'
        },
        itemStyle: {
          color: '#fac858'
        },
        smooth: true
      }] : [])
    ]
  };

  myChart.setOption(option);
  
  // 添加数据点点击事件
  myChart.on('click', function(params: any) {
    if (params.componentType === 'series' && params.data !== undefined) {
      // 显示点击的数据点详情
      const dataIndex = params.dataIndex;
      const seriesName = params.seriesName;
      const value = params.value;
      const date = params.axisValue;
      
      // 显示一个提示框或消息
      ElMessage.info(`日期: ${date}<br/>指标: ${seriesName}<br/>值: ${typeof value === 'number' ? value.toFixed(2) : value}`);
    }
  });
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    myChart.resize();
  });
};

onMounted(() => {
  fetchFields();
});
</script>

<style scoped>
.trend-container {
  padding: 20px;
  background-color: var(--light-gray);
  min-height: 100%;
}

.filter-card {
  background-color: var(--white);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
  color: var(--primary-green-dark);
}

.chart-card {
  background-color: var(--white);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-top: 20px;
  height: 60vh;
}

.chart-header {
  font-weight: bold;
  color: var(--primary-green-dark);
}

.chart-container {
  width: 100%;
  height: 100%;
}

.no-data-card {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  background-color: var(--white);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-top: 20px;
}

.no-data-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

:deep(.el-card__header) {
  background-color: var(--primary-green);
  color: var(--white);
  border-radius: 8px 8px 0 0;
  padding: 15px 20px !important;
}
</style>