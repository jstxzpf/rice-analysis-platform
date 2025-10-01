<template>
  <div class="app-container">
    <h1>田块详情 (ID: {{ id }})</h1>
    <div class="toolbar">
        <router-link :to="{ name: 'TrendAnalysis', params: { id: id } }">
            <el-button type="primary">查看长势趋势</el-button>
        </router-link>
    </div>
    <el-table :data="results" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="记录ID" width="80"></el-table-column>
      <el-table-column prop="capture_date" label="拍摄日期"></el-table-column>
      <el-table-column prop="growth_stage" label="生育期"></el-table-column>
      <el-table-column prop="analysis_status" label="分析状态">
        <template #default="scope">
          <el-tag :type="statusTag(scope.row.analysis_status)">{{ scope.row.analysis_status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <router-link :to="{ name: 'AnalysisReport', params: { id: scope.row.analysis_result.id } }" v-if="scope.row.analysis_result">
            <el-button size="small">查看报告</el-button>
          </router-link>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../api';
import { ElMessage } from 'element-plus';

const route = useRoute();
const id = route.params.id;
const results = ref([]);
const loading = ref(true);

const fetchResults = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get(`/fields/${id}/results`);
    results.value = response.data;
  } catch (error) {
    ElMessage.error('获取分析记录失败');
  } finally {
    loading.value = false;
  }
};

const statusTag = (status: string) => {
  switch (status) {
    case 'COMPLETED': return 'success';
    case 'PROCESSING': return 'primary';
    case 'PENDING': return 'info';
    case 'FAILED': return 'danger';
    default: return 'info';
  }
};

onMounted(fetchResults);
</script>