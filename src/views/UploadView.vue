<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { uploadService, taskService } from '../api/services';
import type { TaskStatus } from '../types/models';

const file = ref<File | null>(null);
const isUploading = ref(false);
const uploadProgress = ref(0);
const uploadResult = ref<{ success: boolean; message: string; task_id?: string } | null>(null);
const taskStatus = ref<TaskStatus | null>(null);
const templates = ref<{ name: string; url: string }[]>([]);

// 获取上传模板
onMounted(async () => {
  try {
    templates.value = await uploadService.getTemplates();
  } catch (error) {
    console.error('Failed to fetch templates:', error);
  }
});

// 处理文件选择
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    file.value = target.files[0];
  }
};

// 处理文件拖放
const handleDrop = (event: DragEvent) => {
  event.preventDefault();
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    file.value = event.dataTransfer.files[0];
  }
};

// 处理拖放区域事件
const handleDragOver = (event: DragEvent) => {
  event.preventDefault();
};

// 下载模板
const downloadTemplate = (templateUrl: string, templateName: string) => {
  const link = document.createElement('a');
  link.href = templateUrl;
  link.download = templateName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 上传文件
const uploadFile = async () => {
  if (!file.value) {
    alert('请先选择文件');
    return;
  }
  
  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10;
      }
    }, 300);
    
    // 上传文件
    const result = await uploadService.uploadFile(file.value);
    clearInterval(progressInterval);
    uploadProgress.value = 100;
    
    uploadResult.value = {
      success: result.success,
      message: result.success ? '文件上传成功！' : '文件上传失败：' + result.error,
      task_id: result.task_id
    };
    
    // 如果上传成功并返回了任务ID，开始轮询任务状态
    if (result.success && result.task_id) {
      taskService.pollTaskStatus(result.task_id, (status) => {
        taskStatus.value = status;
      });
    }
  } catch (error: any) {
    uploadResult.value = {
      success: false,
      message: '上传失败：' + (error.message || '未知错误')
    };
  } finally {
    isUploading.value = false;
  }
};
</script>

<template>
  <div class="upload-container">
    <h1>数据上传</h1>
    
    <div class="upload-section">
      <div 
        class="drop-zone" 
        @dragover="handleDragOver" 
        @drop="handleDrop"
        :class="{ 'has-file': file }"
      >
        <div v-if="!file">
          <i class="upload-icon">📁</i>
          <p>拖放文件到此处，或点击选择文件</p>
          <input 
            type="file" 
            id="file-input" 
            @change="handleFileChange" 
            accept=".xlsx,.xls,.csv"
          />
          <label for="file-input" class="file-input-label">选择文件</label>
        </div>
        <div v-else>
          <p class="selected-file">已选择文件: {{ file.name }}</p>
          <button class="upload-button" @click="uploadFile" :disabled="isUploading">
            {{ isUploading ? '上传中...' : '开始上传' }}
          </button>
          <button class="cancel-button" @click="file = null" :disabled="isUploading">
            取消
          </button>
        </div>
      </div>
      
      <div v-if="isUploading" class="progress-container">
        <div class="progress-bar">
          <div class="progress" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <p>上传进度: {{ uploadProgress }}%</p>
      </div>
      
      <div v-if="uploadResult" class="upload-result" :class="{ 'success': uploadResult.success }">
        <p>{{ uploadResult.message }}</p>
      </div>
      
      <div v-if="taskStatus" class="task-status">
        <h3>数据处理状态</h3>
        <p>状态: {{ taskStatus.status }}</p>
        <p>进度: {{ taskStatus.progress }}%</p>
        <div class="progress-bar">
          <div class="progress" :style="{ width: taskStatus.progress + '%' }"></div>
        </div>
        <p v-if="taskStatus.error_message" class="error-message">
          错误: {{ taskStatus.error_message }}
        </p>
      </div>
    </div>
    
    <div class="templates-section">
      <h2>下载模板</h2>
      <p>请使用以下模板格式上传数据</p>
      
      <div class="templates-list">
        <div v-if="templates.length === 0" class="no-templates">
          <p>暂无可用模板</p>
        </div>
        <div v-else class="template-item" v-for="template in templates" :key="template.name">
          <span>{{ template.name }}</span>
          <button @click="downloadTemplate(template.url, template.name)">下载</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.upload-section {
  margin-bottom: 2rem;
}

.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  background-color: #f9f9f9;
  transition: all 0.3s;
}

.drop-zone:hover {
  border-color: #4CAF50;
  background-color: #f0f0f0;
}

.drop-zone.has-file {
  border-color: #4CAF50;
  background-color: #f0f9f0;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

#file-input {
  display: none;
}

.file-input-label {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  background-color: #4CAF50;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.selected-file {
  margin-bottom: 1rem;
  font-weight: 500;
}

.upload-button, .cancel-button {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 0.5rem;
}

.upload-button {
  background-color: #4CAF50;
  color: white;
}

.cancel-button {
  background-color: #f44336;
  color: white;
}

.progress-container {
  margin-top: 1.5rem;
}

.progress-bar {
  height: 10px;
  background-color: #e0e0e0;
  border-radius: 5px;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.3s;
}

.upload-result {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 4px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.upload-result.success {
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.task-status {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 4px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
}

.error-message {
  color: #721c24;
}

.templates-section {
  margin-top: 3rem;
}

.templates-list {
  margin-top: 1rem;
}

.template-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.template-item button {
  padding: 0.25rem 0.75rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.no-templates {
  padding: 1rem;
  text-align: center;
  color: #666;
}
</style> 