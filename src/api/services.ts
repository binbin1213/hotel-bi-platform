import apiClient from './client';
import type { HotelData, KPIMetric, Report, TaskStatus } from '../types/models';

// 数据服务
export const dataService = {
  // 获取酒店列表
  getHotels: async () => {
    const response = await apiClient.get<HotelData[]>('/data/hotels');
    return response.data;
  },
  
  // 获取酒店详情
  getHotelById: async (hotelId: number) => {
    const response = await apiClient.get<HotelData>(`/data/hotels/${hotelId}`);
    return response.data;
  },
  
  // 获取指标数据
  getMetrics: async (params?: { hotel_id?: number, period_type?: string }) => {
    const response = await apiClient.get<KPIMetric[]>('/data/metrics', { params });
    return response.data;
  }
};

// 上传服务
export const uploadService = {
  // 上传数据文件
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
  
  // 获取上传模板
  getTemplates: async () => {
    const response = await apiClient.get('/upload/templates');
    return response.data;
  }
};

// 报告服务
export const reportService = {
  // 创建报告生成请求
  generateReport: async (reportData: {
    title: string;
    report_type: string;
    hotel_ids: number[];
    period_start?: string;
    period_end?: string;
    output_formats: string[];
  }) => {
    const response = await apiClient.post<{ task_id: string }>('/reports/generate', reportData);
    return response.data;
  },
  
  // 获取报告列表
  getReports: async () => {
    const response = await apiClient.get<Report[]>('/reports');
    return response.data;
  },
  
  // 获取报告详情
  getReportById: async (reportId: number) => {
    const response = await apiClient.get<Report>(`/reports/${reportId}`);
    return response.data;
  },
  
  // 下载报告文件
  downloadReport: async (reportId: number, format: 'pdf' | 'ppt') => {
    const response = await apiClient.get(`/reports/${reportId}/download?format=${format}`, {
      responseType: 'blob'
    });
    return response.data;
  }
};

// 任务服务
export const taskService = {
  // 获取任务列表
  getTasks: async () => {
    const response = await apiClient.get<TaskStatus[]>('/tasks');
    return response.data;
  },
  
  // 获取任务状态
  getTaskStatus: async (taskId: string) => {
    const response = await apiClient.get<TaskStatus>(`/tasks/${taskId}`);
    return response.data;
  },
  
  // 取消任务
  cancelTask: async (taskId: string) => {
    const response = await apiClient.delete(`/tasks/${taskId}`);
    return response.data;
  },
  
  // 轮询任务状态
  pollTaskStatus: (taskId: string, callback: (status: TaskStatus) => void) => {
    const intervalId = setInterval(async () => {
      try {
        const status = await taskService.getTaskStatus(taskId);
        callback(status);
        
        if (['completed', 'failed'].includes(status.status)) {
          clearInterval(intervalId);
        }
      } catch (error) {
        console.error('Failed to fetch task status:', error);
        clearInterval(intervalId);
      }
    }, 2000); // 每2秒轮询一次
    
    return () => clearInterval(intervalId); // 返回清理函数
  }
}; 