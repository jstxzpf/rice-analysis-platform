<template>
  <div class="app-container">
    <h1>数据上传</h1>
    <el-card>
      <el-form :model="form" label-width="120px" style="max-width: 600px">
        <el-form-item label="选择田块">
          <el-select v-model="form.field_id" placeholder="请选择田块">
            <el-option v-for="field in fields" :key="field.id" :label="field.name" :value="field.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="拍摄日期">
          <el-date-picker v-model="form.capture_date" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <el-form-item label="水稻品种">
          <el-select v-model="form.rice_variety" placeholder="请选择水稻品种">
            <el-option v-for="item in riceVarieties" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="无人机俯拍图">
          <el-upload action="#" :auto-upload="false" :on-change="(file) => handleFileChange(file, 'drone_photo')">
            <el-button type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="0.5米侧拍图">
          <el-upload action="#" :auto-upload="false" :on-change="(file) => handleFileChange(file, 'side_photo_05m')">
            <el-button type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="3米侧拍图">
          <el-upload action="#" :auto-upload="false" :on-change="(file) => handleFileChange(file, 'side_photo_3m')">
            <el-button type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="handleSubmit">提交分析</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive } from 'vue';
import apiClient from '../api';
import { ElMessage } from 'element-plus';
import type { UploadFile } from 'element-plus';

interface Field {
  id: number;
  name: string;
}

const fields = ref<Field[]>([]);
const riceVarieties = ref([
  '南粳5055',
  '南粳9108',
  '泰优808',
  '武运粳27号',
  '镇稻18号',
  '扬稻6号',
  '其他',
]);

const form = reactive({
  field_id: '' as (number | string),
  capture_date: '' as (Date | string),
  rice_variety: '' as string,
  drone_photo: null as (File | null),
  side_photo_05m: null as (File | null),
  side_photo_3m: null as (File | null),
});

const fetchFields = async () => {
  try {
    const response = await apiClient.get('/fields/');
    fields.value = response.data;
  } catch (error) {
    ElMessage.error('获取田块列表失败');
  }
};

onMounted(fetchFields);

const handleFileChange = (file: UploadFile, type: keyof typeof form) => {
  form[type] = file.raw as File;
};

const handleSubmit = async () => {
  const formData = new FormData();
  if (form.field_id) formData.append('field_id', String(form.field_id));
  if (form.capture_date) formData.append('capture_date', new Date(form.capture_date).toISOString().split('T')[0]);
  if (form.rice_variety) formData.append('rice_variety', form.rice_variety);
  if (form.drone_photo) formData.append('drone_photo', form.drone_photo);
  if (form.side_photo_05m) formData.append('side_photo_05m', form.side_photo_05m);
  if (form.side_photo_3m) formData.append('side_photo_3m', form.side_photo_3m);

  try {
    const response = await apiClient.post('/photogroups/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    ElMessage.success('上传成功，已开始分析！');

    // Poll for task status
    const taskId = response.data.celery_task_id;
    if (taskId) {
        pollTaskStatus(taskId);
    }

  } catch (error) {
    ElMessage.error('上传失败');
    console.error(error);
  }
};

const pollTaskStatus = (taskId: string) => {
    const intervalId = setInterval(async () => {
        try {
            const response = await apiClient.get(`/photogroups/status/${taskId}`);
            const status = response.data.status;
            if (status === 'SUCCESS' || status === 'FAILURE') {
                clearInterval(intervalId);
                if (status === 'SUCCESS') {
                    ElMessage.success(`任务 ${taskId} 分析完成！`);
                } else {
                    ElMessage.error(`任务 ${taskId} 分析失败。`);
                }
            }
        } catch (error) {
            clearInterval(intervalId);
            ElMessage.error('查询任务状态失败。');
        }
    }, 3000); // Poll every 3 seconds
};
</script>

<style scoped>
.app-container {
    padding: 20px;
}
</style>
