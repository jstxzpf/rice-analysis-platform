<template>
  <div class="pa-6">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>单田块长势追踪</span>
        </div>
      </template>
      <el-row :gutter="20" class="mb-4">
        <el-col :span="6">
          <el-select v-model="selectedField" placeholder="选择田块" @change="fetchDataAndRenderChart" filterable>
            <el-option
              v-for="field in fields"
              :key="field.id"
              :label="field.name"
              :value="field.id"
            />
          </el-select>
        </el-col>
        <el-col :span="10">
          <el-select v-model="selectedMetrics" placeholder="选择分析指标" @change="fetchDataAndRenderChart" multiple collapse-tags>
            <el-option
              v-for="item in availableMetrics"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-col>
      </el-row>
      
      <div ref="chartContainer" style="width: 100%; height: 500px;"></div>

    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick } from 'vue';
import apiClient from '../api';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';

interface Field {
  id: number;
  name: string;
}

const selectedField = ref<number | null>(null);
const selectedMetrics = ref<string[]>(['coverage']);
const fields = ref<Field[]>([]);
const chartData = ref<any>({});
const chartContainer = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const availableMetrics = ref([
  { label: '冠层覆盖度 (%)', value: 'coverage' },
  { label: '平均株高 (cm)', value: 'avg_plant_height' },
  { label: '亩穗数', value: 'panicles_per_mu' },
  { label: '估算叶龄', value: 'estimated_leaf_age' },
  { label: '估算分蘖数', value: 'estimated_tillers_per_plant' },
  { label: '冠层颜色指标', value: 'canopy_color_index' },
  { label: '株高标准差', value: 'height_std_dev' },
]);

const fetchFields = async () => {
  try {
    const response = await apiClient.get('/fields/');
    fields.value = response.data;
    if (fields.value.length > 0) {
      selectedField.value = fields.value[0].id;
      fetchDataAndRenderChart();
    }
  } catch (error) {
    console.error("获取田块列表失败", error);
    ElMessage.error('获取田块列表失败');
  }
};

const fetchDataAndRenderChart = async () => {
  if (!selectedField.value || selectedMetrics.value.length === 0) {
      // Clear chart if no field or metric is selected
      chartInstance?.clear();
      return;
  }

  try {
    const promises = selectedMetrics.value.map(metric => 
      apiClient.get(`/fields/${selectedField.value}/trends`, { params: { indicator: metric } })
    );

    const responses = await Promise.all(promises);
    
    const seriesData: any[] = [];
    const legendData: string[] = [];
    let xAxisData: string[] = [];

    responses.forEach((response, index) => {
      const metric = selectedMetrics.value[index];
      const metricLabel = availableMetrics.value.find(m => m.value === metric)?.label || metric;
      legendData.push(metricLabel);

      const data = response.data.map((item: any) => [item.date, item.value]);
      
      seriesData.push({
        name: metricLabel,
        type: 'line',
        data: data,
        smooth: true,
      });

      // Collect all unique dates for the x-axis
      response.data.forEach((item: any) => {
          if (!xAxisData.includes(item.date)) {
              xAxisData.push(item.date);
          }
      });
    });

    xAxisData.sort((a, b) => new Date(a).getTime() - new Date(b).getTime());

    renderChart(xAxisData, seriesData, legendData);

  } catch (error) {
    console.error("获取趋势数据失败", error);
    ElMessage.error('获取趋势数据失败');
  }
};

const renderChart = (xAxisData: string[], seriesData: any[], legendData: string[]) => {
  if (!chartContainer.value) return;

  const fieldName = fields.value.find(f => f.id === selectedField.value)?.name || '田块';

  const option = {
    title: {
      text: `${fieldName} - 长势追踪`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: legendData,
      bottom: 10,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData,
    },
    yAxis: {
      type: 'value'
    },
    series: seriesData,
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    toolbox: {
        feature: {
            saveAsImage: {}
        }
    }
  };

  if (!chartInstance) {
    chartInstance = echarts.init(chartContainer.value);
  }
  chartInstance.setOption(option, true); // use true to clear previous options
};

onMounted(() => {
  fetchFields();
  nextTick(() => {
      if (chartContainer.value) {
          chartInstance = echarts.init(chartContainer.value);
          window.addEventListener('resize', () => chartInstance?.resize());
      }
  });
});

</script>

<style scoped>
.mb-4 {
  margin-bottom: 1.5rem;
}
</style>