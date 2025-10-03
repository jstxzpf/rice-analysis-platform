<template>
  <div class="upload-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>图像上传与分析</h1>
      <p class="page-description">请上传四张配套照片进行水稻生长分析</p>
    </div>

    <!-- 上传流程步骤 -->
    <el-steps :active="currentStep" finish-status="success" simple class="upload-steps">
      <el-step title="选择田块" icon="Grid" />
      <el-step title="上传照片" icon="Picture" />
      <el-step title="启动分析" icon="DataAnalysis" />
      <el-step title="查看结果" icon="Document" />
    </el-steps>

    <!-- 步骤内容 -->
    <el-card class="upload-card" shadow="never">
      <div v-if="currentStep === 0" class="step-content">
        <h2>第一步：选择田块</h2>
        <el-form 
          ref="stepOneFormRef" 
          :model="stepOneForm" 
          :rules="stepOneRules" 
          label-width="120px"
          class="step-form"
        >
          <el-form-item label="选择田块" prop="field_id">
            <el-select 
              v-model="stepOneForm.field_id" 
              placeholder="请选择田块"
              style="width: 100%"
              @change="nextStep"
            >
              <el-option 
                v-for="field in fields" 
                :key="field.id" 
                :label="field.name" 
                :value="field.id"
              >
                <span style="float: left">{{ field.name }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">
                  {{ field.area ? `${field.area}亩` : '面积未知' }}
                </span>
              </el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="拍摄日期" prop="capture_date">
            <el-date-picker 
              v-model="stepOneForm.capture_date" 
              type="date" 
              placeholder="选择拍摄日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
          
          <el-form-item label="水稻品种">
            <el-select 
              v-model="stepOneForm.rice_variety" 
              placeholder="请选择水稻品种"
              style="width: 100%"
            >
              <el-option label="南粳5055" value="南粳5055" />
              <el-option label="南粳9108" value="南粳9108" />
              <el-option label="泰优808" value="泰优808" />
              <el-option label="武运粳27号" value="武运粳27号" />
              <el-option label="镇稻18号" value="镇稻18号" />
              <el-option label="扬稻6号" value="扬稻6号" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          
          <div class="step-actions">
            <el-button @click="resetForm">重置</el-button>
            <el-button 
              type="primary" 
              @click="validateStepOne"
              :disabled="!stepOneForm.field_id || !stepOneForm.capture_date"
            >
              下一步
            </el-button>
          </div>
        </el-form>
      </div>

      <div v-else-if="currentStep === 1" class="step-content">
        <h2>第二步：上传四张配套照片</h2>
        <p class="step-description">
          请按指定角度拍摄并上传四张照片，用于全方位分析水稻生长状况
        </p>
        
        <el-row :gutter="20" class="upload-grid">
          <!-- 无人机俯拍图 -->
          <el-col :span="12">
            <el-card class="photo-upload-card" shadow="hover">
              <template #header>
                <div class="photo-header">
                  <span class="photo-title">无人机俯拍图</span>
                  <el-tag type="success">必需</el-tag>
                </div>
                <p class="photo-description">整体视角，展示田块全貌</p>
              </template>
              
              <el-upload
                class="photo-uploader"
                action="#"
                :auto-upload="false"
                list-type="picture-card"
                :limit="1"
                :on-exceed="handleExceed"
                :on-change="(file, fileList) => handleFileChange(file, fileList, 'drone_photo')"
                :on-preview="handlePictureCardPreview"
                :on-remove="() => handleRemove('drone_photo')"
                accept="image/jpeg,image/png"
              >
                <el-icon><Plus /></el-icon>
                <div class="upload-text">点击上传</div>
              </el-upload>
            </el-card>
          </el-col>
          
          <!-- 0.5米侧拍图 -->
          <el-col :span="12">
            <el-card class="photo-upload-card" shadow="hover">
              <template #header>
                <div class="photo-header">
                  <span class="photo-title">0.5米侧拍图</span>
                  <el-tag type="success">必需</el-tag>
                </div>
                <p class="photo-description">近距离细节，用于精确定量分析</p>
              </template>
              
              <el-upload
                class="photo-uploader"
                action="#"
                :auto-upload="false"
                list-type="picture-card"
                :limit="1"
                :on-exceed="handleExceed"
                :on-change="(file, fileList) => handleFileChange(file, fileList, 'side_photo_05m')"
                :on-preview="handlePictureCardPreview"
                :on-remove="() => handleRemove('side_photo_05m')"
                accept="image/jpeg,image/png"
              >
                <el-icon><Plus /></el-icon>
                <div class="upload-text">点击上传</div>
              </el-upload>
            </el-card>
          </el-col>
          
          <!-- 3米横向侧拍图 -->
          <el-col :span="12">
            <el-card class="photo-upload-card" shadow="hover">
              <template #header>
                <div class="photo-header">
                  <span class="photo-title">3米横向侧拍图</span>
                  <el-tag type="success">必需</el-tag>
                </div>
                <p class="photo-description">水平方向排列，用于行间距测量</p>
              </template>
              
              <el-upload
                class="photo-uploader"
                action="#"
                :auto-upload="false"
                list-type="picture-card"
                :limit="1"
                :on-exceed="handleExceed"
                :on-change="(file, fileList) => handleFileChange(file, fileList, 'side_photo_3m_horizontal')"
                :on-preview="handlePictureCardPreview"
                :on-remove="() => handleRemove('side_photo_3m_horizontal')"
                accept="image/jpeg,image/png"
              >
                <el-icon><Plus /></el-icon>
                <div class="upload-text">点击上传</div>
              </el-upload>
            </el-card>
          </el-col>
          
          <!-- 3米纵向侧拍图 -->
          <el-col :span="12">
            <el-card class="photo-upload-card" shadow="hover">
              <template #header>
                <div class="photo-header">
                  <span class="photo-title">3米纵向侧拍图</span>
                  <el-tag type="success">必需</el-tag>
                </div>
                <p class="photo-description">垂直方向排列，用于株间距测量</p>
              </template>
              
              <el-upload
                class="photo-uploader"
                action="#"
                :auto-upload="false"
                list-type="picture-card"
                :limit="1"
                :on-exceed="handleExceed"
                :on-change="(file, fileList) => handleFileChange(file, fileList, 'side_photo_3m_vertical')"
                :on-preview="handlePictureCardPreview"
                :on-remove="() => handleRemove('side_photo_3m_vertical')"
                accept="image/jpeg,image/png"
              >
                <el-icon><Plus /></el-icon>
                <div class="upload-text">点击上传</div>
              </el-upload>
            </el-card>
          </el-col>
        </el-row>
        
        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button 
            type="primary" 
            @click="nextStep"
            :disabled="!areAllPhotosUploaded"
          >
            下一步
          </el-button>
        </div>
      </div>

      <div v-else-if="currentStep === 2" class="step-content">
        <h2>第三步：启动分析</h2>
        <p class="step-description">
          确认上传信息无误后，点击下方按钮启动图像分析任务
        </p>
        
        <el-card class="summary-card">
          <template #header>
            <div class="summary-header">
              <span>上传信息汇总</span>
            </div>
          </template>
          
          <div class="summary-content">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="田块名称">
                {{ selectedField?.name }}
              </el-descriptions-item>
              <el-descriptions-item label="拍摄日期">
                {{ stepOneForm.capture_date }}
              </el-descriptions-item>
              <el-descriptions-item label="水稻品种">
                {{ stepOneForm.rice_variety || '未指定' }}
              </el-descriptions-item>
              <el-descriptions-item label="上传时间">
                {{ currentTime }}
              </el-descriptions-item>
            </el-descriptions>
            
            <div class="photo-preview-grid">
              <div 
                v-for="(photo, key) in photoPreviews" 
                :key="key" 
                class="photo-preview-item"
              >
                <div class="photo-label">{{ getPhotoLabel(key) }}</div>
                <el-image 
                  :src="photo" 
                  class="photo-preview"
                  fit="cover"
                  :preview-src-list="[photo]"
                />
              </div>
            </div>
          </div>
        </el-card>
        
        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button 
            type="primary" 
            @click="startAnalysis"
            :loading="isSubmitting"
          >
            启动分析
          </el-button>
        </div>
      </div>

      <div v-else class="step-content">
        <h2>第四步：查看分析结果</h2>
        <el-result 
          v-if="analysisSuccess" 
          icon="success" 
          title="分析任务已启动" 
          subTitle="您的图像正在后台分析中，请稍后在田块详情页查看结果"
        >
          <template #extra>
            <el-button type="primary" @click="goToFieldDetail">查看田块详情</el-button>
            <el-button @click="resetAll">上传新图像</el-button>
          </template>
        </el-result>
        
        <el-result 
          v-else 
          icon="error" 
          title="分析启动失败" 
          subTitle="请检查网络连接或稍后重试"
        >
          <template #extra>
            <el-button type="primary" @click="resetAll">重新上传</el-button>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="dialogVisible" title="图片预览" width="50%">
      <img :src="dialogImageUrl" alt="Preview Image" style="width: 100%;" />
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import apiClient from '../api';
import { 
  Plus, 
  Grid, 
  Picture, 
  DataAnalysis, 
  Document 
} from '@element-plus/icons-vue';

interface Field {
  id: number;
  name: string;
  area?: number;
}

interface StepOneForm {
  field_id: number | string;
  capture_date: string;
  rice_variety: string;
}

interface UploadedPhotos {
  drone_photo: File | null;
  side_photo_05m: File | null;
  side_photo_3m_horizontal: File | null;
  side_photo_3m_vertical: File | null;
}

const router = useRouter();
const stepOneFormRef = ref<FormInstance>();
const currentStep = ref(0);
const isSubmitting = ref(false);
const analysisSuccess = ref(false);
const dialogVisible = ref(false);
const dialogImageUrl = ref('');

const fields = ref<Field[]>([]);
const selectedField = computed(() => {
  return fields.value.find(field => field.id === Number(stepOneForm.value.field_id));
});

const currentTime = computed(() => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
});

const stepOneForm = ref<StepOneForm>({
  field_id: '',
  capture_date: '',
  rice_variety: ''
});

const stepOneRules = {
  field_id: [
    { required: true, message: '请选择田块', trigger: 'change' }
  ],
  capture_date: [
    { required: true, message: '请选择拍摄日期', trigger: 'change' }
  ]
};

const uploadedPhotos = ref<UploadedPhotos>({
  drone_photo: null,
  side_photo_05m: null,
  side_photo_3m_horizontal: null,
  side_photo_3m_vertical: null
});

const photoPreviews = computed(() => {
  const previews: Record<string, string> = {};
  Object.keys(uploadedPhotos.value).forEach(key => {
    const file = uploadedPhotos.value[key as keyof UploadedPhotos];
    if (file) {
      previews[key] = URL.createObjectURL(file);
    }
  });
  return previews;
});

const areAllPhotosUploaded = computed(() => {
  return Object.values(uploadedPhotos.value).every(photo => photo !== null);
});

const fetchFields = async () => {
  try {
    const response = await apiClient.get('/fields/');
    fields.value = response.data;
  } catch (error) {
    ElMessage.error('获取田块列表失败');
  }
};

const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++;
  }
};

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

const validateStepOne = async () => {
  if (!stepOneFormRef.value) return;
  
  const valid = await stepOneFormRef.value.validate().catch(() => false);
  if (valid) {
    nextStep();
  }
};

const resetForm = () => {
  stepOneForm.value = {
    field_id: '',
    capture_date: '',
    rice_variety: ''
  };
  currentStep.value = 0;
};

const resetAll = () => {
  // 重置所有表单和上传状态
  resetForm();
  uploadedPhotos.value = {
    drone_photo: null,
    side_photo_05m: null,
    side_photo_3m_horizontal: null,
    side_photo_3m_vertical: null
  };
  isSubmitting.value = false;
  analysisSuccess.value = false;
};

const handleFileChange = (uploadFile: any, uploadFiles: any, type: keyof UploadedPhotos) => {
  uploadedPhotos.value[type] = uploadFile.raw as File;
};

const handleRemove = (type: keyof UploadedPhotos) => {
  uploadedPhotos.value[type] = null;
};

const handlePictureCardPreview = (uploadFile: any) => {
  dialogImageUrl.value = uploadFile.url!;
  dialogVisible.value = true;
};

const handleExceed = () => {
  ElMessage.warning('每个类别只能上传一张图片');
};

const getPhotoLabel = (key: string) => {
  const labels: Record<string, string> = {
    drone_photo: '无人机俯拍图',
    side_photo_05m: '0.5米侧拍图',
    side_photo_3m_horizontal: '3米横向侧拍图',
    side_photo_3m_vertical: '3米纵向侧拍图'
  };
  return labels[key] || key;
};

const startAnalysis = async () => {
  if (!stepOneForm.value.field_id) {
    ElMessage.error('请选择田块');
    return;
  }

  isSubmitting.value = true;

  const formData = new FormData();
  formData.append('field_id', String(stepOneForm.value.field_id));
  if (stepOneForm.value.capture_date) formData.append('capture_date', stepOneForm.value.capture_date);
  if (stepOneForm.value.rice_variety) formData.append('rice_variety', stepOneForm.value.rice_variety);
  if (uploadedPhotos.value.drone_photo) formData.append('drone_photo', uploadedPhotos.value.drone_photo);
  if (uploadedPhotos.value.side_photo_05m) formData.append('side_photo_05m', uploadedPhotos.value.side_photo_05m);
  if (uploadedPhotos.value.side_photo_3m_horizontal) formData.append('side_photo_3m_horizontal', uploadedPhotos.value.side_photo_3m_horizontal);
  if (uploadedPhotos.value.side_photo_3m_vertical) formData.append('side_photo_3m_vertical', uploadedPhotos.value.side_photo_3m_vertical);

  try {
    const response = await apiClient.post('/photogroups/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    ElMessage.success('上传成功，已开始分析！');
    analysisSuccess.value = true;
    nextStep();
    
    // 释放预览URL对象以避免内存泄漏
    Object.values(photoPreviews.value).forEach(url => URL.revokeObjectURL(url));
    
  } catch (error) {
    ElMessage.error('上传失败');
    analysisSuccess.value = false;
    console.error(error);
  } finally {
    isSubmitting.value = false;
  }
};

const goToFieldDetail = () => {
  if (selectedField.value) {
    router.push(`/fields/${selectedField.value.id}`);
  }
};

onMounted(fetchFields);

// 监听路由参数变化，如果从其他页面带参数跳转过来，则自动填充
watch(() => router.currentRoute.value.query.field_id, (newFieldId) => {
  if (newFieldId) {
    stepOneForm.value.field_id = Number(newFieldId);
  }
});
</script>

<style scoped>
.upload-container {
  padding: 20px;
  background-color: var(--light-gray);
  min-height: 100%;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  color: var(--primary-green-dark);
  font-size: 28px;
  font-weight: 600;
}

.page-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0;
}

.upload-steps {
  margin-bottom: 20px;
  background-color: var(--white);
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.upload-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.step-content {
  padding: 20px;
}

.step-content h2 {
  margin: 0 0 15px 0;
  color: var(--primary-green-dark);
  font-size: 24px;
  font-weight: 600;
}

.step-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 20px;
}

.step-form {
  max-width: 500px;
  margin: 0 auto;
}

.upload-grid {
  margin: 20px 0;
}

.photo-upload-card {
  height: 100%;
  border-radius: 8px;
}

.photo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.photo-title {
  font-weight: bold;
  font-size: 16px;
  color: var(--primary-green-dark);
}

.photo-description {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.photo-uploader {
  width: 100%;
  text-align: center;
}

:deep(.el-upload--picture-card) {
  background-color: var(--light-gray);
  border: 2px dashed var(--medium-gray);
  border-radius: 8px;
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

:deep(.el-upload--picture-card:hover) {
  border-color: var(--primary-green);
  color: var(--primary-green);
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100%;
  height: 200px;
}

.upload-text {
  margin-top: 10px;
  color: var(--text-secondary);
  font-size: 14px;
}

.summary-card {
  margin: 20px 0;
  border-radius: 8px;
}

.summary-header {
  font-weight: bold;
  color: var(--primary-green-dark);
  font-size: 18px;
}

.photo-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.photo-preview-item {
  text-align: center;
}

.photo-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.photo-preview {
  width: 100%;
  height: 120px;
  border-radius: 4px;
  object-fit: cover;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

:deep(.el-result) {
  padding: 40px 0;
}

:deep(.el-result .el-result__title) {
  margin-bottom: 10px;
}

:deep(.el-result .el-result__subtitle) {
  margin-bottom: 30px;
}
</style>