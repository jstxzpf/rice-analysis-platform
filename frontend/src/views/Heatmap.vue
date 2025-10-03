<template>
  <div class="app-container">
    <h1>生长热力图分析</h1>
    
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
    
    <el-card v-if="chartData.length > 0" class="chart-card">
      <div ref="chartRef" class="chart-container"></div>
    </el-card>
    
    <el-card v-else class="no-data-card">
      <div class="no-data-content">
        <el-empty description="请选择田块和指标以查看热力图" />
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick, watch } from 'vue';
import apiClient from '../api';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts/core';
import { 
  GridComponent, 
  TooltipComponent, 
  VisualMapComponent,
  DataZoomComponent
} from 'echarts/components';
import { HeatmapChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import type { ComposeOption } from 'echarts/core';
import type { 
  GridComponentOption, 
  TooltipComponentOption, 
  VisualMapComponentOption,
  DataZoomComponentOption 
} from 'echarts/components';
import type { HeatmapSeriesOption } from 'echarts/charts';
import type { CanvasRendererOption } from 'echarts/renderers';

// Register ECharts components
echarts.use([
  Grid3DComponent,
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
  HeatmapChart,
  CanvasRenderer,
  DataZoomComponent
]);

type EChartsOption = ComposeOption<
  | GridComponentOption
  | TooltipComponentOption
  | VisualMapComponentOption
  | DataZoomComponentOption
  | HeatmapSeriesOption
  | CanvasRendererOption
>;

interface Field {
  id: number;
  name: string;
}

interface Form {
  field_id: number | null;
  indicator: string;
  start_date: string | null;
  end_date: string | null;
}

const fields = ref<Field[]>([]);
const chartRef = ref<HTMLDivElement>();
let chart: echarts.ECharts | null = null;
const chartData = ref<any[]>([]);
const form = ref<Form>({
  field_id: null,
  indicator: 'avg_plant_height',
  start_date: null,
  end_date: null
});

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
    
    const response = await apiClient.get(`/analysis/growth-heatmap/${form.value.field_id}`, {
      params
    });
    
    chartData.value = response.data.heatmap_data;
    renderChart();
  } catch (error) {
    ElMessage.error('加载热力图数据失败');
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
  
  // Prepare heatmap data
  // Format: [[x, y, value, date], ...]
  const processedData = chartData.value.map(item => [item[0], item[1], item[2]]); // x, y, value
  
  // Create option for heatmap
  const option: EChartsOption = {
    title: {
      text: `${fields.value.find(f => f.id === form.value.field_id)?.name} - ${indicatorLabels[form.value.indicator] || form.value.indicator} 热力图`,
      left: 'center'
    },
    tooltip: {
      position: 'top',
      formatter: function(params: any) {
        const data = params.data as [number, number, number];
        return `坐标: (${data[0].toFixed(2)}, ${data[1].toFixed(2)})<br/>数值: ${data[2].toFixed(2)}`;
      }
    },
    grid: {
      height: '70%',
      top: '10%'
    },
    xAxis: {
      type: 'value',
      splitArea: {
        show: true
      },
      name: 'X坐标 (米)',
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      splitArea: {
        show: true
      },
      name: 'Y坐标 (米)',
      nameLocation: 'middle',
      nameGap: 30
    },
    visualMap: {
      min: 0,
      max: Math.max(...processedData.map(item => item[2]), 1),
      calculable: true,
      orient: 'vertical',
      left: 'right',
      top: 'center',
      text: ['高', '低'],  // 文本，默认为数值文本
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffcc', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      }
    },
    series: [{
      type: 'heatmap',
      data: processedData,
      label: {
        show: false
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
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
onUnmounted(() => {
  if (chart) {
    chart.dispose();
  }
});

// Watch for changes in chart data to re-render
watch(chartData, () => {
  if (chartData.value.length > 0) {
    nextTick(() => {
      renderChart();
    });
  }
});

// Component unmount cleanup
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

.chart-card {
  height: 70vh;
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
}

.no-data-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>