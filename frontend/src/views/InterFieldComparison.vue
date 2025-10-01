<template>
  <div class="pa-6">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>跨田块长势对比</span>
        </div>
      </template>
      <el-row :gutter="20" class="mb-4">
        <el-col :span="6">
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择对比时期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="fetchData"
          />
        </el-col>
        <el-col :span="6">
          <el-select v-model="selectedMetric" placeholder="选择分析指标" @change="renderChart">
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
import { ref, onMounted, watch, nextTick } from 'vue';
import apiClient from '../api';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';

const selectedDate = ref(new Date().toISOString().split('T')[0]);
const selectedMetric = ref('coverage');
const analysisData = ref<any[]>([]);
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

const fetchData = async () => {
  if (!selectedDate.value) return;
  try {
    const response = await apiClient.get('/analysis/inter-field-comparison/', {
      params: { period_date: selectedDate.value },
    });
    analysisData.value = response.data;
    renderChart();
  } catch (error) {
    console.error("获取对比数据失败", error);
    ElMessage.error('获取对比数据失败');
  }
};

const renderChart = () => {
  if (!chartContainer.value || analysisData.value.length === 0) return;

  const metricLabel = availableMetrics.value.find(m => m.value === selectedMetric.value)?.label || '指标';

  // Process data to get the latest result per field for the selected metric
  const latestResults = new Map<string, any>();
  analysisData.value.forEach(item => {
    const fieldName = item.photo_group.field.name;
    if (!latestResults.has(fieldName) || new Date(item.photo_group.capture_date) > new Date(latestResults.get(fieldName).photo_group.capture_date)) {
      latestResults.set(fieldName, item);
    }
  });

  const chartData = Array.from(latestResults.values());

  const option = {
    title: {
      text: `不同田块【${metricLabel}】对比`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    xAxis: {
      type: 'category',
      data: chartData.map(item => item.photo_group.field.name),
      axisLabel: { interval: 0, rotate: 30 }
    },
    yAxis: {
      type: 'value',
      name: metricLabel
    },
    series: [
      {
        name: metricLabel,
        type: 'bar',
        data: chartData.map(item => item[selectedMetric.value]),
        barWidth: '60%'
      }
    ],
    grid: {
      bottom: 100
    }
  };

  if (!chartInstance) {
    chartInstance = echarts.init(chartContainer.value);
  }
  chartInstance.setOption(option);
};

onMounted(() => {
  fetchData();
  nextTick(() => {
      if (chartContainer.value) {
          chartInstance = echarts.init(chartContainer.value);
          window.addEventListener('resize', () => chartInstance?.resize());
      }
  });
});

watch([selectedMetric], renderChart);

</script>

<style scoped>
.mb-4 {
  margin-bottom: 1.5rem;
}
</style>