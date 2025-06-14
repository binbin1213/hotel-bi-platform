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
  <div class="reports-bg">
    <div class="reports-container">
      <div class="content-wrapper">
        <div class="report-form">
          <div class="form-header">
            <span class="form-icon">📄</span>
            <h2>生成新报告</h2>
          </div>
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
          <div class="list-header">
            <span class="list-bar"></span>
            <h2>报告列表</h2>
          </div>
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
    </div>
  </div>
</template>

<style scoped>
.reports-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #e3ecff 0%, #f8fbff 100%);
  padding-top: 48px;
  padding-bottom: 48px;
}
.reports-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 1.5rem;
}
.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 40px;
}
.report-form {
  background: linear-gradient(90deg, #f8fbff 60%, #e3ecff 100%);
  border-radius: 24px;
  padding: 2.5rem 2rem 2rem 2rem;
  box-shadow: 0 8px 32px 0 rgba(64,158,255,0.10);
  border: none;
  margin-bottom: 0;
}
.form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 2rem;
}
.form-icon {
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
.report-form h2 {
  font-size: 1.35rem;
  font-weight: 700;
  color: #23408e;
  margin: 0;
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #23408e;
}
.form-group input[type="text"],
.form-group select {
  width: 100%;
  padding: 0.85rem;
  border: 1.5px solid #b3c6e0;
  border-radius: 14px;
  font-size: 1rem;
  background: #f8fbff;
  transition: border 0.2s;
}
.form-group input[type="text"]:focus,
.form-group select:focus {
  border: 1.5px solid #409EFF;
  outline: none;
}
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
}
.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 500;
  color: #23408e;
  font-size: 1rem;
}
.checkbox-label input {
  margin-right: 0.5rem;
  accent-color: #409EFF;
}
.generate-button {
  padding: 1rem 2.8rem;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  color: #fff;
  border: none;
  border-radius: 28px;
  font-size: 1.15rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(64,158,255,0.12);
  transition: background 0.2s, box-shadow 0.2s, transform 0.2s;
}
.generate-button:hover {
  background: linear-gradient(90deg, #67C23A 0%, #409EFF 100%);
  box-shadow: 0 4px 16px rgba(64,158,255,0.18);
  transform: translateY(-2px) scale(1.04);
}
.generate-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}
.reports-list {
  background: #fff;
  border-radius: 24px;
  padding: 2.5rem 2rem 2rem 2rem;
  box-shadow: 0 8px 32px 0 rgba(64,158,255,0.10);
  border: none;
}
.list-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 2rem;
}
.list-bar {
  width: 6px;
  height: 1.6rem;
  border-radius: 4px;
  background: linear-gradient(180deg, #409EFF 0%, #67C23A 100%);
  box-shadow: 0 2px 8px rgba(64,158,255,0.10);
}
.reports-list h2 {
  font-size: 1.35rem;
  font-weight: 700;
  color: #23408e;
  margin: 0;
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
  border-collapse: separate;
  border-spacing: 0;
  background: #f8fbff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(64,158,255,0.08);
}
th, td {
  padding: 1.1rem 0.85rem;
  text-align: left;
  border-bottom: 1px solid #e3ecff;
}
th {
  background: linear-gradient(90deg, #409EFF 0%, #e3ecff 100%);
  color: #23408e;
  font-weight: 700;
  font-size: 1.05rem;
  border-bottom: 2px solid #b3c6e0;
}
.status {
  padding: 0.35rem 0.8rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 1px;
}
.status.pending {
  background: #fff3cd;
  color: #b8860b;
}
.status.processing {
  background: #cce5ff;
  color: #23408e;
}
.status.completed {
  background: #d4edda;
  color: #409EFF;
}
.status.failed {
  background: #f8d7da;
  color: #F56C6C;
}
.actions {
  display: flex;
  gap: 0.7rem;
}
.download-button {
  padding: 0.55rem 1.3rem;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  color: #fff;
  border: none;
  border-radius: 22px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(64,158,255,0.10);
  transition: background 0.2s, box-shadow 0.2s, transform 0.2s;
}
.download-button:hover {
  background: linear-gradient(90deg, #67C23A 0%, #409EFF 100%);
  box-shadow: 0 2px 8px rgba(64,158,255,0.18);
  transform: translateY(-2px) scale(1.04);
}
@media (max-width: 900px) {
  .reports-container {
    padding: 0 0.2rem;
  }
  .content-wrapper {
    gap: 24px;
  }
  .report-form, .reports-list {
    padding: 1.2rem 0.5rem;
    border-radius: 12px;
  }
  th, td {
    padding: 0.5rem;
  }
  .download-button {
    padding: 0.35rem 0.7rem;
    font-size: 0.9rem;
    border-radius: 12px;
  }
}
</style> 