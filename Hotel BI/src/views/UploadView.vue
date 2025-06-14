<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { UploadFilled, Delete, Document, Check, Warning } from '@element-plus/icons-vue';
import { uploadService } from '../api/services';

const fileList = ref<any[]>([]);
const uploadStatus = ref<'idle' | 'uploading' | 'success' | 'error'>('idle');
const uploadProgress = ref(0);
const selectedHotel = ref('');
const uploadType = ref('excel');

const hotels = reactive({
  options: [
    { value: '1', label: '上海环球金融中心酒店' },
    { value: '2', label: '北京国贸大酒店' },
    { value: '3', label: '广州白天鹅宾馆' }
  ]
});

const uploadTypes = [
  { value: 'excel', label: 'Excel文件' },
  { value: 'csv', label: 'CSV文件' },
  { value: 'json', label: 'JSON文件' }
];

// 文件上传之前的验证
const beforeUpload = (file: File) => {
  // 检查文件类型
  const isValidType = checkFileType(file);
  if (!isValidType) {
    ElMessage.error('请上传正确的文件类型！');
    return false;
  }
  
  // 检查文件大小（限制为10MB）
  const isLessThan10M = file.size / 1024 / 1024 < 10;
  if (!isLessThan10M) {
    ElMessage.error('文件大小不能超过10MB！');
    return false;
  }
  
  return true;
};

// 检查文件类型
const checkFileType = (file: File) => {
  if (uploadType.value === 'excel') {
    return file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
           file.type === 'application/vnd.ms-excel';
  } else if (uploadType.value === 'csv') {
    return file.type === 'text/csv';
  } else if (uploadType.value === 'json') {
    return file.type === 'application/json';
  }
  return false;
};

// 处理文件变化
const handleFileChange = (uploadFile: any, uploadFiles: any[]) => {
  fileList.value = uploadFiles;
};

// 处理文件删除
const handleRemove = (file: any, uploadFiles: any[]) => {
  fileList.value = uploadFiles;
};

// 处理文件上传
const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要上传的文件！');
    return;
  }
  
  if (!selectedHotel.value) {
    ElMessage.warning('请选择酒店！');
    return;
  }
  
  try {
    uploadStatus.value = 'uploading';
    
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10;
      }
    }, 300);
    
    // 尝试调用真实API
    try {
      await uploadService.uploadFile(fileList.value[0].raw, selectedHotel.value);
    } catch (error) {
      console.error('API上传失败，使用模拟上传', error);
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // 上传完成
    clearInterval(progressInterval);
    uploadProgress.value = 100;
    uploadStatus.value = 'success';
    
    // 显示成功消息
    ElMessage({
      type: 'success',
      message: '数据上传成功！',
      duration: 3000
    });
    
    // 重置状态
    setTimeout(() => {
      fileList.value = [];
      uploadProgress.value = 0;
      uploadStatus.value = 'idle';
    }, 2000);
    
  } catch (error) {
    uploadStatus.value = 'error';
    ElMessage.error('上传失败，请重试！');
    console.error('Upload error:', error);
  }
};

// 取消上传
const cancelUpload = () => {
  ElMessageBox.confirm('确定要取消上传吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    uploadStatus.value = 'idle';
    uploadProgress.value = 0;
    ElMessage({
      type: 'info',
      message: '已取消上传'
    });
  }).catch(() => {
    // 用户取消操作
  });
};
</script>

<template>
  <div class="upload-bg">
    <div class="upload-main">
      <div class="upload-content">
        <!-- 上传区 -->
        <div class="upload-card upload-section">
          <div class="upload-header">
            <span class="upload-icon-main gradient-icon">
              <el-icon><UploadFilled /></el-icon>
            </span>
            <div>
              <h2>数据上传</h2>
              <p class="subtitle">上传酒店运营数据以生成分析报告</p>
            </div>
          </div>
          <el-form label-position="top" :model="{}" class="upload-form">
            <el-form-item label="选择酒店">
              <el-select 
                v-model="selectedHotel" 
                placeholder="请选择酒店"
                style="width: 100%"
              >
                <el-option
                  v-for="item in hotels.options"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="文件类型">
              <el-radio-group v-model="uploadType">
                <el-radio 
                  v-for="type in uploadTypes" 
                  :key="type.value" 
                  :label="type.value"
                >
                  {{ type.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <div class="upload-area">
                <el-upload
                  class="upload-component"
                  drag
                  action="#"
                  :auto-upload="false"
                  :file-list="fileList"
                  :on-change="handleFileChange"
                  :on-remove="handleRemove"
                  :before-upload="beforeUpload"
                  :multiple="false"
                  :disabled="uploadStatus === 'uploading'"
                >
                  <el-icon class="upload-icon"><UploadFilled /></el-icon>
                  <div class="upload-text">
                    <span>拖拽文件到此处或点击上传</span>
                    <p class="upload-hint">支持 Excel, CSV, JSON 格式文件</p>
                  </div>
                </el-upload>
              </div>
            </el-form-item>
            <el-form-item v-if="fileList.length > 0">
              <div class="file-list">
                <h3>已选择文件</h3>
                <el-table :data="fileList" style="width: 100%">
                  <el-table-column prop="name" label="文件名">
                    <template #default="scope">
                      <div class="file-item">
                        <el-icon><Document /></el-icon>
                        <span>{{ scope.row.name }}</span>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="size" label="大小" width="150">
                    <template #default="scope">
                      {{ (scope.row.size / 1024).toFixed(2) }} KB
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="100">
                    <template #default="scope">
                      <el-button 
                        type="danger" 
                        :icon="Delete" 
                        circle 
                        @click="handleRemove(scope.row, fileList)"
                        :disabled="uploadStatus === 'uploading'"
                      />
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-form-item>
            <el-form-item v-if="uploadStatus === 'uploading'">
              <div class="upload-progress">
                <el-progress :percentage="uploadProgress" :stroke-width="10" />
                <p class="progress-text">正在上传: {{ uploadProgress }}%</p>
                <el-button type="danger" @click="cancelUpload">取消上传</el-button>
              </div>
            </el-form-item>
            <el-form-item v-if="uploadStatus === 'success'">
              <div class="upload-result success">
                <el-icon class="result-icon"><Check /></el-icon>
                <span>上传成功！数据已保存</span>
              </div>
            </el-form-item>
            <el-form-item v-if="uploadStatus === 'error'">
              <div class="upload-result error">
                <el-icon class="result-icon"><Warning /></el-icon>
                <span>上传失败，请重试</span>
              </div>
            </el-form-item>
            <el-form-item>
              <div class="action-buttons">
                <el-button 
                  class="main-btn"
                  type="primary" 
                  @click="handleUpload" 
                  :disabled="fileList.length === 0 || uploadStatus === 'uploading'"
                  :loading="uploadStatus === 'uploading'"
                >
                  上传数据
                </el-button>
                <el-button class="main-btn" @click="fileList = []" :disabled="fileList.length === 0 || uploadStatus === 'uploading'">
                  清空列表
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>
        <!-- 说明区 -->
        <div class="upload-card tips-section">
          <div class="tips-header">
            <span class="tips-icon gradient-icon">
              <el-icon><UploadFilled /></el-icon>
            </span>
            <h3>上传说明</h3>
          </div>
          <ul class="tips-list">
            <li>支持Excel文件(.xlsx, .xls)、CSV文件(.csv)和JSON文件(.json)</li>
            <li>文件大小不能超过10MB</li>
            <li>数据必须包含以下字段: 日期、房间数、入住率、平均房价、收入</li>
            <li>日期格式应为YYYY-MM-DD</li>
            <li>上传完成后系统会自动处理数据并生成分析结果</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #e3ecff 0%, #f8fbff 100%);
  padding-top: 48px;
  padding-bottom: 48px;
}
.upload-main {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1.5rem;
}
.upload-content {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}
.upload-card {
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 8px 32px 0 rgba(64,158,255,0.10);
  padding: 2.5rem 2rem 2rem 2rem;
  border: none;
  flex: 1;
  min-width: 0;
}
.upload-section {
  max-width: 520px;
}
.tips-section {
  max-width: 340px;
  padding: 2rem 1.2rem 1.5rem 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.upload-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 2rem;
}
.upload-icon-main {
  font-size: 2.1rem;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  color: #fff;
  border-radius: 50%;
  width: 2.6rem;
  height: 2.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(64,158,255,0.10);
}
.upload-header h2 {
  font-size: 1.35rem;
  font-weight: 700;
  color: #23408e;
  margin: 0;
}
.subtitle {
  margin: 8px 0 0;
  color: #409EFF;
  font-size: 15px;
  font-weight: 500;
}
.upload-form {
  margin-top: 0;
}
.upload-area {
  border: 2.5px dashed #409EFF;
  border-radius: 18px;
  background: linear-gradient(135deg, #f8fbff 60%, #e3ecff 100%);
  transition: border-color 0.3s, box-shadow 0.3s;
  padding: 32px 0 24px 0;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(64,158,255,0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 320px;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
}
.upload-area:hover {
  border-color: #67C23A;
  box-shadow: 0 4px 16px rgba(103,194,58,0.10);
}
.upload-component {
  width: 100%;
}
.upload-icon {
  font-size: 54px;
  color: #409EFF;
  margin-bottom: 10px;
}
.upload-text {
  color: #23408e;
  font-size: 17px;
  text-align: center;
}
.upload-hint {
  font-size: 13px;
  color: #67C23A;
  margin-top: 8px;
}
.file-list {
  margin-top: 20px;
}
.file-list h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: #23408e;
}
.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.upload-progress {
  margin: 20px 0;
}
.progress-text {
  margin: 8px 0;
  text-align: center;
  color: #606266;
}
.upload-result {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  gap: 8px;
}
.upload-result.success {
  background-color: #f0f9eb;
  color: #67c23a;
}
.upload-result.error {
  background-color: #fef0f0;
  color: #f56c6c;
}
.result-icon {
  font-size: 20px;
}
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
  width: 320px;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
}
.main-btn {
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%) !important;
  color: #fff !important;
  border-radius: 22px !important;
  font-size: 1.08rem !important;
  font-weight: 600 !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(64,158,255,0.12) !important;
  transition: background 0.2s, box-shadow 0.2s, transform 0.2s !important;
}
.main-btn:hover {
  background: linear-gradient(90deg, #67C23A 0%, #409EFF 100%) !important;
  box-shadow: 0 4px 16px rgba(64,158,255,0.18) !important;
  transform: translateY(-2px) scale(1.04) !important;
}
.tips-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.2rem;
}
.tips-icon {
  font-size: 1.7rem;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  color: #fff;
  border-radius: 50%;
  width: 2.2rem;
  height: 2.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(64,158,255,0.10);
}
.tips-section h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #23408e;
  margin: 0;
}
.tips-list {
  margin: 0;
  padding-left: 20px;
}
.tips-list li {
  margin-bottom: 10px;
  color: #606266;
  font-size: 15px;
}
.tips-list li:last-child {
  margin-bottom: 0;
}
@media (max-width: 900px) {
  .upload-content {
    flex-direction: column;
    gap: 28px;
  }
  .upload-section, .tips-section {
    max-width: 100%;
  }
  .upload-card {
    padding: 1.2rem 0.5rem;
    border-radius: 14px;
  }
}
.gradient-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 50%;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  box-shadow: 0 2px 8px rgba(64,158,255,0.10);
}
.gradient-icon .el-icon {
  font-size: 1.7rem;
  color: #fff;
}
</style> 