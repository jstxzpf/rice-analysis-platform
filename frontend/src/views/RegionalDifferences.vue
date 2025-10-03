<template>
  <div class="app-container">
    <h1>区域差异分析</h1>
    
    <el-card class="filter-card">
      <el-form :model="form" inline>
        <el-form-item label="选择田块">
          <el-select v-model="form.field_id" placeholder="请选择田块" @change="loadFieldData">
            <el-option v-for="field in fields" :key="field.id" :label="field.name" :value="field.id"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="选择指标">
          <el-select v-model="form.indicator" placeholder="请选择指标" @change="loadData">
            <el-option label="平均株高" value="avg_plant_height"></el-option>
            <el-option label="覆盖度" value="coverage"></el-option>
            <el-option label="冠层颜色指数" value="canopy_color_index"></el-option>
            <el-option label="均匀度指数" value="uniformity_index"></el-option>
            <el-option label="分蘖密度" value="tiller_density_estimate"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.start_date" type="date" placeholder="选择开始日期" @change="loadData"></el-date-picker>
        </el-form-item>
        
        <el-form-item label="结束日期">
          <el-date-picker v-model="form.end_date" type="date" placeholder="选择结束日期" @change="loadData"></el-date-picker>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadData">加载数据</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="regionalStats && Object.keys(regionalStats).length > 0" class="analysis-card">
      <template #header>
        <div class="card-header">
          <span>{{ fields.find(f => f.id === form.field_id)?.name }} - {{ indicatorLabels[form.indicator] || form.indicator }} 区域差异分析</span>
        </div>
      </template>
      
      <!-- 显示整体统计与区域统计的对比 -->
      <div class="comparison-section">
        <h3>整体田块统计</h3>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="平均值">{{ overallStats.average }}</el-descriptions-item>
          <el-descriptions-item label="最小值">{{ overallStats.min }}</el-descriptions-item>
          <el-descriptions-item label="最大值">{{ overallStats.max }}</el-descriptions-item>
          <el-descriptions-item label="标准差">{{ overallStats.std_dev }}</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <div class="regional-section">
        <h3>各区域统计对比</h3>
        <el-table :data="regionalTableData" style="width: 100%" border>
          <el-table-column prop="region" label="区域" width="150" />
          <el-table-column prop="average" label="平均值" width="120" />
          <el-table-column prop="min" label="最小值" width="120" />
          <el-table-column prop="max" label="最大值" width="120" />
          <el-table-column prop="stdDev" label="标准差" width="120" />
          <el-table-column prop="count" label="样本数" width="120" />
        </el-table>
      </div>
      
      <!-- 可视化图表 -->
      <div class="chart-section">
        <h3>区域对比图表</h3>
        <div ref="chartRef" class="chart-container"></div>
      </div>
    </el-card>
    
    <el-card v-else class="no-data-card">
      <div class="no-data-content">
        <el-empty description="请选择田块和指标以查看区域差异分析" />
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts/core';
import { 
  GridComponent, 
  TooltipComponent, 
  LegendComponent
} from 'echarts/components';
import { BarChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import type { ComposeOption } from 'echarts/core';
import type { 
  GridComponentOption, 
  TooltipComponentOption, 
  LegendComponentOption
} from 'echarts/components';
import type { BarSeriesOption } from 'echarts/charts';
import type { CanvasRendererOption } from 'echarts/renderers';

// Register ECharts components
echarts.use([
  GridComponent,
  TooltipComponent,
  LegendComponent,
  BarChart,
  CanvasRenderer
]);

type EChartsOption = ComposeOption<
  | GridComponentOption
  | TooltipComponentOption
  | LegendComponentOption
  | BarSeriesOption
  | CanvasRendererOption
>;

interface Field {
  id: number;
  name: string;
}

interface RegionalStat {
  average: number;
  min: number;
  max: number;
  std_dev: number;
  count: number;
}

interface Form {
  field_id: number | null;
  indicator: string;
  start_date: string | null;
  end_date: string | null;
}

interface RegionalTableItem {
  region: string;
  average: number;
  min: number;
  max: number;
  stdDev: number;
  count: number;
}

const fields = ref<Field[]>([]);
const chartRef = ref<HTMLDivElement>();
let chart: echarts.ECharts | null = null;
const form = ref<Form>({
  field_id: null,
  indicator: 'avg_plant_height',
  start_date: null,
  end_date: null
});
const regionalStats = ref<Record<string, RegionalStat>>({});
const overallStats = ref<RegionalStat>({
  average: 0,
  min: 0,
  max: 0,
  std_dev: 0,
  count: 0
});
const regionalTableData = ref<RegionalTableItem[]>([]);

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

  try {
    const params: Record<string, any> = {
      indicator: form.value.indicator
    };
    
    if (form.value.start_date) params.start_date = form.value.start_date;
    if (form.value.end_date) params.end_date = form.value.end_date;
    
    const response = await apiClient.get(`/analysis/regional-differences/${form.value.field_id}`, {
      params
    });
    
    regionalStats.value = response.data.regional_stats;
    overallStats.value = response.data.overall_stats;
    
    // Prepare data for the table
    regionalTableData.value = Object.entries(response.data.regional_stats).map(([region, stats]) => ({
      region: region.charAt(0).toUpperCase() + region.slice(1), // Capitalize region name
      average: stats.average,
      min: stats.min,
      max: stats.max,
      stdDev: stats.std_dev,
      count: stats.count
    }));
    
    // Render chart after data is loaded
    setTimeout(renderChart, 100); // Small delay to ensure DOM is updated
  } catch (error) {
    ElMessage.error('加载区域差异数据失败');
    console.error(error);
  }
};

const loadFieldData = () => {
  if (form.value.field_id) {
    loadData();
  }
};

const renderChart = () => {
  if (!chartRef.value) return;
  
  // Dispose existing chart if present
  if (chart) {
    chart.dispose();
  }
  
  // Initialize chart
  chart = echarts.init(chartRef.value);
  
  // Prepare chart data
  const regions = Object.keys(regionalStats.value);
  const averages = regions.map(region => regionalStats.value[region].average);
  
  // Create option for bar chart
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params: any) {
        const param = params[0];
        const region = param.name;
        const value = param.value;
        return `${region}<br/>平均值: ${value}`;
      }
    },
    legend: {
      data: ['平均值']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: regions.map(region => region.charAt(0).toUpperCase() + region.slice(1)), // Capitalize region names
      name: '区域',
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      name: indicatorLabels[form.value.indicator] || form.value.indicator,
      nameLocation: 'middle',
      nameGap: 50
    },
    series: [{
      name: '平均值',
      type: 'bar',
      data: averages,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      },
      emphasis: {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#2378f7' },
            { offset: 0.7, color: '#2378f7' },
            { offset: 1, color: '#83bff6' }
          ])
        }
      }
    }]
  };
  
  // Apply option and render chart
  chart.setOption(option);
  
  // Handle window resize
  window.addEventListener('resize', () => {
    if (chart) {
      chart.resize();
    }
  });
};

// Initialize component
onMounted(() => {
  fetchFields();
});

// Cleanup on component unmount
const onUnmounted = () => {
  if (chart) {
    chart.dispose();
    chart = null;
  }
};
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.analysis-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comparison-section {
  margin-bottom: 30px;
}

.regional-section {
  margin-bottom: 30px;
}

.chart-section {
  margin-top: 30px;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.no-data-card {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.no-data-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

h3 {
  margin-bottom: 15px;
  color: #303133;
}
</style>