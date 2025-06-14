<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { reportService } from '../api/services';
import type { Report } from '../types/models';

const reports = ref<Report[]>([]);
const isLoading = ref(true);
const isGenerating = ref(false);
const selectedHotelIds = ref<number[]>([]);
const reportTitle = ref('');
const reportType = ref('analysis');
const outputFormats = ref<string[]>(['pdf']);

// 加载报告列表
onMounted(async () => {
  try {
    reports.value = await reportService.getReports();
  } catch (error) {
    console.error('Failed to load reports:', error);
  } finally {
    isLoading.value = false;
  }
});

// 生成报告
const generateReport = async () => {
  if (!reportTitle.value || selectedHotelIds.value.length === 0 || outputFormats.value.length === 0) {
    alert('请填写报告标题、选择酒店和输出格式');
    return;
  }
  
  try {
    isGenerating.value = true;
    
    const result = await reportService.generateReport({
      title: reportTitle.value,
      report_type: reportType.value,
      hotel_ids: selectedHotelIds.value,
      period_start: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0],
      period_end: new Date().toISOString().split('T')[0],
      output_formats: outputFormats.value
    });
    
    alert('报告生成请求已提交，任务ID: ' + result.task_id);
    
    // 重新加载报告列表
    setTimeout(async () => {
      reports.value = await reportService.getReports();
    }, 2000);
    
  } catch (error: any) {
    alert('报告生成失败: ' + (error.message || '未知错误'));
  } finally {
    isGenerating.value = false;
  }
};

// 下载报告
const downloadReport = async (reportId: number, format: 'pdf' | 'ppt') => {
  try {
    const blob = await reportService.downloadReport(reportId, format);
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report_${reportId}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert('报告下载失败');
    console.error('Failed to download report:', error);
  }
};
</script>

<template>
  <div class="reports-container">
    <h1>报告管理</h1>
    
    <div class="report-form">
      <h2>生成新报告</h2>
      
      <div class="form-group">
        <label for="report-title">报告标题</label>
        <input 
          id="report-title" 
          type="text" 
          v-model="reportTitle" 
          placeholder="请输入报告标题"
        />
      </div>
      
      <div class="form-group">
        <label for="report-type">报告类型</label>
        <select id="report-type" v-model="reportType">
          <option value="analysis">分析报告</option>
          <option value="comparison">比较报告</option>
          <option value="forecast">预测报告</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>选择酒店</label>
        <div class="checkbox-group">
          <!-- 实际项目中应该从API获取酒店列表 -->
          <label class="checkbox-label">
            <input type="checkbox" value="1" v-model="selectedHotelIds" />
            示例酒店1
          </label>
          <label class="checkbox-label">
            <input type="checkbox" value="2" v-model="selectedHotelIds" />
            示例酒店2
          </label>
        </div>
      </div>
      
      <div class="form-group">
        <label>输出格式</label>
        <div class="checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" value="pdf" v-model="outputFormats" />
            PDF
          </label>
          <label class="checkbox-label">
            <input type="checkbox" value="ppt" v-model="outputFormats" />
            PPT
          </label>
        </div>
      </div>
      
      <button 
        class="generate-button" 
        @click="generateReport" 
        :disabled="isGenerating"
      >
        {{ isGenerating ? '生成中...' : '生成报告' }}
      </button>
    </div>
    
    <div class="reports-list">
      <h2>报告列表</h2>
      
      <div v-if="isLoading" class="loading">
        加载中...
      </div>
      
      <div v-else-if="reports.length === 0" class="no-reports">
        <p>暂无报告，请生成新报告</p>
      </div>
      
      <div v-else class="reports-table">
        <table>
          <thead>
            <tr>
              <th>标题</th>
              <th>类型</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="report in reports" :key="report.id">
              <td>{{ report.title }}</td>
              <td>{{ report.report_type }}</td>
              <td>
                <span class="status" :class="report.status">{{ report.status }}</span>
              </td>
              <td>{{ new Date(report.created_at).toLocaleString() }}</td>
              <td>
                <div class="actions">
                  <button 
                    v-if="report.status === 'completed' && report.file_paths?.pdf" 
                    @click="downloadReport(report.id, 'pdf')"
                    class="download-button"
                  >
                    下载PDF
                  </button>
                  <button 
                    v-if="report.status === 'completed' && report.file_paths?.ppt" 
                    @click="downloadReport(report.id, 'ppt')"
                    class="download-button"
                  >
                    下载PPT
                  </button>
                  <span v-if="report.status === 'pending' || report.status === 'processing'">
                    处理中...
                  </span>
                  <span v-if="report.status === 'failed'">
                    生成失败
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reports-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.report-form {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-label input {
  margin-right: 0.5rem;
}

.generate-button {
  padding: 0.75rem 2rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.generate-button:hover {
  background-color: #45a049;
}

.generate-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.reports-list {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading, .no-reports {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.reports-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
  font-weight: 500;
}

.status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status.processing {
  background-color: #cce5ff;
  color: #004085;
}

.status.completed {
  background-color: #d4edda;
  color: #155724;
}

.status.failed {
  background-color: #f8d7da;
  color: #721c24;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.download-button {
  padding: 0.25rem 0.5rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}
</style> 