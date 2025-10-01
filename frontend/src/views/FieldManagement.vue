<template>
  <div class="app-container">
    <div class="toolbar">
        <el-button type="primary" @click="handleCreate">新增田块</el-button>
    </div>

    <el-table :data="fields" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="名称"></el-table-column>
      <el-table-column prop="location" label="位置"></el-table-column>
      <el-table-column prop="area" label="面积 (亩)"></el-table-column>
      <el-table-column prop="planting_date" label="种植日期"></el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <router-link :to="{ name: 'FieldDetail', params: { id: scope.row.id } }">
            <el-button size="small">查看详情</el-button>
          </router-link>
          <el-button size="small" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="dialogTitle" v-model="dialogVisible">
      <el-form :model="currentField" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="currentField.name"></el-input>
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="currentField.location"></el-input>
        </el-form-item>
        <el-form-item label="面积 (亩)">
          <el-input-number v-model="currentField.area" :precision="2"></el-input-number>
        </el-form-item>
        <el-form-item label="种植日期">
          <el-date-picker v-model="currentField.planting_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD"></el-date-picker>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitField">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';

interface Field {
  id?: number;
  name: string;
  location?: string;
  area?: number;
  planting_date?: string;
}

const fields = ref<Field[]>([]);
const loading = ref(true);
const dialogVisible = ref(false);
const dialogTitle = ref('');
const isEdit = ref(false);
const currentField = ref<Field>({ name: '' });

const fetchFields = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/fields/');
    fields.value = response.data;
  } catch (error) {
    ElMessage.error('获取田块列表失败');
  } finally {
    loading.value = false;
  }
};

onMounted(fetchFields);

const handleCreate = () => {
  isEdit.value = false;
  dialogTitle.value = '新增田块';
  currentField.value = { 
    name: '',
    location: '',
    area: null,
    planting_date: null
  };
  dialogVisible.value = true;
};

const handleUpdate = (field: Field) => {
  isEdit.value = true;
  dialogTitle.value = '编辑田块';
  currentField.value = { ...field };
  dialogVisible.value = true;
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除这个田块吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await apiClient.delete(`/fields/${id}`);
      ElMessage.success('删除成功');
      fetchFields(); // Refresh list
    } catch (error) {
      ElMessage.error('删除失败');
    }
  });
};

const submitField = async () => {
  try {
    if (isEdit.value) {
      await apiClient.put(`/fields/${currentField.value.id}`!, currentField.value);
      ElMessage.success('更新成功');
    } else {
      await apiClient.post('/fields/', currentField.value);
      ElMessage.success('新增成功');
    }
    dialogVisible.value = false;
    fetchFields(); // Refresh list
  } catch (error: any) {
    console.error("Detailed error response:", error.response?.data);
    const errorMsg = error.response?.data?.detail?.[0]?.msg || '未知错误';
    ElMessage.error((isEdit.value ? '更新' : '新增') + '失败: ' + errorMsg);
  }
};
</script>

<style scoped>
.app-container {
    padding: 20px;
}
.toolbar {
    margin-bottom: 20px;
}
</style>