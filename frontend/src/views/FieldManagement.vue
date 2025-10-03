<template>
  <div class="fields-container">
    <!-- 页面标题和搜索栏 -->
    <div class="page-header">
      <h1>田块管理</h1>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索田块..."
          class="search-input"
          clearable
          style="width: 300px; margin-right: 15px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="showAddFieldDialog">
          <el-icon><Plus /></el-icon>
          添加新田块
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="种植品种">
          <el-select v-model="filterForm.variety" placeholder="请选择品种" clearable>
            <el-option label="南粳5055" value="南粳5055" />
            <el-option label="南粳9108" value="南粳9108" />
            <el-option label="泰优808" value="泰优808" />
            <el-option label="武运粳27号" value="武运粳27号" />
            <el-option label="镇稻18号" value="镇稻18号" />
            <el-option label="扬稻6号" value="扬稻6号" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="种植日期">
          <el-date-picker
            v-model="filterForm.plantingDate"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilters">应用筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 田块列表卡片 -->
    <el-row :gutter="20" class="fields-grid">
      <el-col 
        v-for="field in filteredFields" 
        :key="field.id" 
        :span="8"
        class="field-col"
      >
        <el-card class="field-card" shadow="hover">
          <template #header>
            <div class="field-header">
              <span class="field-name">{{ field.name }}</span>
              <el-tag :type="getFieldStatusType(field)" size="small">
                {{ getFieldStatusText(field) }}
              </el-tag>
            </div>
          </template>
          
          <div class="field-content">
            <div class="field-info">
              <div class="info-item">
                <el-icon><Location /></el-icon>
                <span>{{ field.location || '未指定位置' }}</span>
              </div>
              <div class="info-item">
                <el-icon><ScaleToOriginal /></el-icon>
                <span>{{ field.area ? `${field.area} 亩` : '未指定面积' }}</span>
              </div>
              <div class="info-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ field.planting_date || '未指定种植日期' }}</span>
              </div>
              <div class="info-item">
                <el-icon><Flag /></el-icon>
                <span>{{ field.rice_variety || '未指定品种' }}</span>
              </div>
            </div>
            
            <div class="field-stats">
              <div class="stat-item">
                <div class="stat-label">分析次数</div>
                <div class="stat-value">{{ field.analysis_count || 0 }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">最近分析</div>
                <div class="stat-value">{{ field.last_analysis_date || '无' }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">平均株高</div>
                <div class="stat-value">{{ field.avg_height ? `${field.avg_height} cm` : '无数据' }}</div>
              </div>
            </div>
          </div>
          
          <div class="field-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="viewFieldDetails(field.id)"
            >
              查看详情
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="uploadImages(field.id)"
            >
              上传图像
            </el-button>
            <el-dropdown @command="handleFieldAction">
              <el-button size="small">
                更多操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{action: 'edit', field: field}">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-dropdown-item>
                  <el-dropdown-item :command="{action: 'delete', field: field}" divided>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <el-empty 
      v-if="filteredFields.length === 0" 
      description="暂无田块数据" 
      class="empty-state"
    />

    <!-- 添加/编辑田块对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑田块' : '添加新田块'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="fieldFormRef"
        :model="currentField"
        :rules="fieldRules"
        label-width="100px"
      >
        <el-form-item label="田块名称" prop="name">
          <el-input v-model="currentField.name" placeholder="请输入田块名称" />
        </el-form-item>
        
        <el-form-item label="位置" prop="location">
          <el-input v-model="currentField.location" placeholder="请输入田块位置" />
        </el-form-item>
        
        <el-form-item label="面积(亩)" prop="area">
          <el-input-number 
            v-model="currentField.area" 
            :min="0" 
            :precision="2" 
            placeholder="请输入面积"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="种植日期" prop="planting_date">
          <el-date-picker
            v-model="currentField.planting_date"
            type="date"
            placeholder="请选择种植日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="水稻品种" prop="rice_variety">
          <el-select v-model="currentField.rice_variety" placeholder="请选择水稻品种" style="width: 100%">
            <el-option label="南粳5055" value="南粳5055" />
            <el-option label="南粳9108" value="南粳9108" />
            <el-option label="泰优808" value="泰优808" />
            <el-option label="武运粳27号" value="武运粳27号" />
            <el-option label="镇稻18号" value="镇稻18号" />
            <el-option label="扬稻6号" value="扬稻6号" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveField">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import apiClient from '../api';
import { 
  Search, 
  Plus, 
  Location, 
  ScaleToOriginal, 
  Calendar, 
  Flag,
  Edit,
  Delete,
  ArrowDown
} from '@element-plus/icons-vue';

interface Field {
  id: number;
  name: string;
  location?: string;
  area?: number;
  planting_date?: string;
  rice_variety?: string;
  status?: 'normal' | 'attention' | 'warning';
  analysis_count?: number;
  last_analysis_date?: string;
  avg_height?: number;
}

interface FilterForm {
  variety: string;
  plantingDate: [string, string] | null;
}

const router = useRouter();
const fieldFormRef = ref<FormInstance>();
const searchQuery = ref('');
const dialogVisible = ref(false);
const isEditMode = ref(false);
const loading = ref(false);

const fields = ref<Field[]>([]);
const filteredFields = computed(() => {
  let result = fields.value;
  
  // 应用搜索过滤
  if (searchQuery.value) {
    result = result.filter(field => 
      field.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (field.location && field.location.toLowerCase().includes(searchQuery.value.toLowerCase()))
    );
  }
  
  return result;
});

const filterForm = ref<FilterForm>({
  variety: '',
  plantingDate: null
});

const currentField = ref<Field>({
  id: 0,
  name: '',
  location: '',
  area: undefined,
  planting_date: undefined,
  rice_variety: ''
});

const fieldRules = {
  name: [
    { required: true, message: '请输入田块名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  area: [
    { type: 'number', min: 0, message: '面积必须大于等于0', trigger: 'blur' }
  ]
};

const fetchFields = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/fields/');
    fields.value = response.data.map((field: any) => ({
      ...field,
      status: 'normal', // 实际应用中应该从API获取状态
      analysis_count: Math.floor(Math.random() * 10), // 模拟分析次数
      last_analysis_date: '2025-09-15', // 模拟最近分析日期
      avg_height: 45 + Math.random() * 10 // 模拟平均株高
    }));
  } catch (error) {
    ElMessage.error('获取田块列表失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const showAddFieldDialog = () => {
  isEditMode.value = false;
  currentField.value = {
    id: 0,
    name: '',
    location: '',
    area: undefined,
    planting_date: undefined,
    rice_variety: ''
  };
  dialogVisible.value = true;
};

const viewFieldDetails = (fieldId: number) => {
  router.push(`/fields/${fieldId}`);
};

const uploadImages = (fieldId: number) => {
  router.push(`/upload?field_id=${fieldId}`);
};

const handleFieldAction = (command: { action: string; field: Field }) => {
  const { action, field } = command;
  
  switch (action) {
    case 'edit':
      isEditMode.value = true;
      currentField.value = { ...field };
      dialogVisible.value = true;
      break;
    case 'delete':
      ElMessageBox.confirm(
        `确定要删除田块 "${field.name}" 吗？此操作不可撤销。`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(async () => {
        try {
          await apiClient.delete(`/fields/${field.id}`);
          ElMessage.success('删除成功');
          fetchFields(); // 重新加载列表
        } catch (error) {
          ElMessage.error('删除失败');
          console.error(error);
        }
      });
      break;
  }
};

const saveField = async () => {
  if (!fieldFormRef.value) return;
  
  const valid = await fieldFormRef.value.validate().catch(() => false);
  if (!valid) return;

  try {
    if (isEditMode.value) {
      await apiClient.put(`/fields/${currentField.value.id}`, currentField.value);
      ElMessage.success('更新成功');
    } else {
      await apiClient.post('/fields/', currentField.value);
      ElMessage.success('添加成功');
    }
    dialogVisible.value = false;
    fetchFields(); // 重新加载列表
  } catch (error: any) {
    console.error("Detailed error response:", error.response?.data);
    const errorMsg = error.response?.data?.detail?.[0]?.msg || '未知错误';
    ElMessage.error((isEditMode.value ? '更新' : '添加') + '失败: ' + errorMsg);
  }
};

const applyFilters = () => {
  // 实际应用中应该发送API请求应用筛选条件
  ElMessage.info('筛选功能将在后续版本中实现');
};

const resetFilters = () => {
  filterForm.value = {
    variety: '',
    plantingDate: null
  };
  ElMessage.info('筛选条件已重置');
};

const getFieldStatusType = (field: Field) => {
  switch (field.status) {
    case 'normal': return 'success';
    case 'attention': return 'warning';
    case 'warning': return 'danger';
    default: return 'info';
  }
};

const getFieldStatusText = (field: Field) => {
  switch (field.status) {
    case 'normal': return '正常';
    case 'attention': return '需关注';
    case 'warning': return '异常';
    default: return '未知';
  }
};

onMounted(fetchFields);
</script>

<style scoped>
.fields-container {
  padding: 20px;
  background-color: var(--light-gray);
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: var(--primary-green-dark);
}

.header-actions {
  display: flex;
  align-items: center;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.fields-grid {
  margin-top: 20px;
}

.field-col {
  margin-bottom: 20px;
}

.field-card {
  height: 100%;
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.field-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.field-name {
  font-weight: bold;
  font-size: 16px;
  color: var(--primary-green-dark);
}

.field-content {
  padding: 15px 0;
}

.field-info {
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.info-item .el-icon {
  margin-right: 8px;
  color: var(--primary-green);
}

.field-stats {
  display: flex;
  justify-content: space-between;
  background-color: var(--light-gray);
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-weight: bold;
  color: var(--primary-green-dark);
}

.field-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  padding-top: 15px;
}

.field-actions .el-button {
  margin: 0 5px;
}

.empty-state {
  margin-top: 50px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-card__header) {
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>