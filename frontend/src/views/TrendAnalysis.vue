<template>
  <div class="app-container">
    <h1>趋势分析</h1>
    <div ref="chart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';

const chart = ref<HTMLElement | null>(null);

onMounted(() => {
  if (chart.value) {
    const myChart = echarts.init(chart.value);
    const option = {
      title: {
        text: '冠层覆盖度趋势'
      },
      tooltip: {},
      xAxis: {
        data: ['2024-07-01', '2024-07-08', '2024-07-15', '2024-07-22', '2024-07-29']
      },
      yAxis: {},
      series: [{
        name: '覆盖度',
        type: 'line',
        data: [45, 55, 62, 78, 85]
      }]
    };
    myChart.setOption(option);
  }
});
</script>
