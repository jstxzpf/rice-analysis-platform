<template>
  <div class="app-container" v-if="field">
    <h1>田块详情: {{ field.name }}</h1>
    <el-descriptions :column="2" border class="field-descriptions">
        <el-descriptions-item label="位置">{{ field.location }}</el-descriptions-item>
        <el-descriptions-item label="面积">{{ field.area }} 亩</el-descriptions-item>
        <el-descriptions-item label="种植日期">{{ field.planting_date }}</el-descriptions-item>
    </el-descriptions>

    <el-row :gutter="20">
        <el-col :span="12">
            <div id="map" style="height: 400px; margin-top: 20px;"></div>
        </el-col>
        <el-col :span="12">
            <div class="toolbar">
                <router-link :to="{ name: 'TrendAnalysis', params: { id: id } }">
                    <el-button type="primary">查看长势趋势</el-button>
                </router-link>
            </div>
            <el-table :data="results" style="width: 100%" v-loading="loading" class="results-table">
              <el-table-column prop="id" label="记录ID" width="80"></el-table-column>
              <el-table-column prop="capture_date" label="拍摄日期"></el-table-column>
              <el-table-column prop="analysis_status" label="分析状态">
                <template #default="scope">
                  <el-tag :type="statusTag(scope.row.analysis_status)">{{ scope.row.analysis_status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <router-link :to="{ name: 'AnalysisReport', params: { id: scope.row.analysis_result.id } }" v-if="scope.row.analysis_result">
                    <el-button size="small">查看报告</el-button>
                  </router-link>
                </template>
              </el-table-column>
            </el-table>
        </el-col>
    </el-row>

  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../api';
import { ElMessage } from 'element-plus';
import "leaflet/dist/leaflet.css";
import L from "leaflet";

const route = useRoute();
const id = route.params.id;

const field = ref<any>(null);
const results = ref([]);
const loading = ref(true);

const fetchData = async () => {
  loading.value = true;
  try {
    const [fieldResponse, resultsResponse] = await Promise.all([
      apiClient.get(`/fields/${id}`),
      apiClient.get(`/fields/${id}/results`)
    ]);
    field.value = fieldResponse.data;
    results.value = resultsResponse.data;

    await nextTick();
    initMap();

  } catch (error) {
    ElMessage.error('获取田块数据失败');
  } finally {
    loading.value = false;
  }
};

const initMap = () => {
    if (!field.value || !field.value.location) {
        ElMessage.warning('该田块没有设置位置信息');
        return;
    }

    const locationParts = field.value.location.split(',').map(Number);
    if (locationParts.length !== 2 || isNaN(locationParts[0]) || isNaN(locationParts[1])) {
        ElMessage.error('位置信息格式不正确，应为 “纬度,经度”');
        return;
    }
    const lat = locationParts[0];
    const lon = locationParts[1];

    const map = L.map('map').setView([lat, lon], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.marker([lat, lon]).addTo(map)
        .bindPopup(field.value.name)
        .openPopup();
}

const statusTag = (status: string) => {
  switch (status) {
    case 'COMPLETED': return 'success';
    case 'PROCESSING': return 'primary';
    case 'PENDING': return 'info';
    case 'FAILED': return 'danger';
    default: return 'info';
  }
};

onMounted(fetchData);
</script>

<style scoped>
.app-container {
    padding: 20px;
}
.toolbar {
    margin-bottom: 15px;
}
.field-descriptions {
    margin-bottom: 20px;
}
.results-table {
    margin-top: 20px;
}
</style>
