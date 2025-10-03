<template>
  <div style="padding: 32px; max-width: 700px; margin: 0 auto;">
    <el-card>
      <template #header>
        <span style="font-size: 20px; font-weight: bold;">可视化分析中心</span>
      </template>
      <div style="margin-bottom: 16px;">请选择您要使用的分析功能：</div>
      <el-row gutter="20">
        <el-col :span="24">
          <el-link type="primary" :underline="false" style="font-size: 18px; display: flex; align-items: center; margin-bottom: 12px;" :to="{ path: '/visual-analysis/inter-field' }" router>
            <el-icon style="margin-right: 12px;"><i class="el-icon-data-analysis" /></el-icon>
            <div>
              <div style="font-weight: 500;">跨田块长势对比</div>
              <div style="font-size: 12px; color: #888;">同时期内，不同田块的各项指标对比</div>
            </div>
          </el-link>
        </el-col>
        <el-col :span="24">
          <el-link type="primary" :underline="false" style="font-size: 18px; display: flex; align-items: center;" :to="{ path: '/visual-analysis/intra-field' }" router>
            <el-icon style="margin-right: 12px;"><i class="el-icon-trend-charts" /></el-icon>
            <div>
              <div style="font-weight: 500;">单田块长势追踪</div>
              <div style="font-size: 12px; color: #888;">同一田块，不同时期各项指标的变化趋势</div>
            </div>
          </el-link>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'VisualAnalysis',
});
</script>
