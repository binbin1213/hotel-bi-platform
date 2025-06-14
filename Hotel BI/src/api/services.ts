import apiClient from './client';
import type { HotelData, KPIMetric, Report, TaskStatus, ApiResponse } from '../types/models';

// 数据服务
export const dataService = {
  // 获取酒店列表
  getHotels: async () => {
    try {
      const response = await apiClient.get<ApiResponse<HotelData[]>>('/hotels');
      return response.data.data;
    } catch (error) {
      console.error('获取酒店列表失败:', error);
      return [];
    }
  },
  
  // 获取酒店详情
  getHotelById: async (hotelId: number) => {
    const response = await apiClient.get<ApiResponse<HotelData>>(`/hotels/${hotelId}`);
    return response.data.data;
  },
  
  // 获取指标数据
  getMetrics: async (params?: { 
    hotel_id?: number, 
    period_type?: string,
    start_date?: string,
    end_date?: string
  }) => {
    try {
      const response = await apiClient.get<ApiResponse<KPIMetric[]>>('/metrics', { params });
      return response.data.data;
    } catch (error) {
      console.error('获取指标数据失败:', error);
      return [];
    }
  }
};

// 上传服务
export const uploadService = {
  // 上传数据文件
  uploadFile: async (file: File, hotelId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('hotel_id', hotelId);
    
    const response = await apiClient.post<ApiResponse<{ task_id: string }>>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data.data;
  },
  
  // 获取上传模板
  getTemplates: async () => {
    const response = await apiClient.get<ApiResponse<{ name: string; url: string }[]>>('/templates');
    return response.data.data;
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
    const response = await apiClient.post<ApiResponse<{ task_id: string }>>('/reports/generate', reportData);
    return response.data.data;
  },
  
  // 获取报告列表
  getReports: async () => {
    try {
      const response = await apiClient.get<ApiResponse<Report[]>>('/reports');
      return response.data.data;
    } catch (error) {
      console.error('获取报告列表失败:', error);
      return [];
    }
  },
  
  // 获取报告详情
  getReportById: async (reportId: number) => {
    const response = await apiClient.get<ApiResponse<Report>>(`/reports/${reportId}`);
    return response.data.data;
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
    try {
      const response = await apiClient.get<ApiResponse<TaskStatus[]>>('/tasks');
      return response.data.data;
    } catch (error) {
      console.error('获取任务列表失败:', error);
      return [];
    }
  },
  
  // 获取任务状态
  getTaskStatus: async (taskId: string) => {
    const response = await apiClient.get<ApiResponse<TaskStatus>>(`/tasks/${taskId}`);
    return response.data.data;
  },
  
  // 取消任务
  cancelTask: async (taskId: string) => {
    const response = await apiClient.delete<ApiResponse<{ success: boolean }>>(`/tasks/${taskId}`);
    return response.data.data;
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
        console.error('轮询任务状态失败:', error);
        clearInterval(intervalId);
      }
    }, 2000); // 每2秒轮询一次
    
    return () => clearInterval(intervalId); // 返回清理函数
  }
};

// 用户认证服务
export const authService = {
  // 用户登录
  login: async (username: string, password: string) => {
    const response = await apiClient.post<ApiResponse<{ token: string; user: { id: number; username: string; role: string } }>>('/auth/login', {
      username,
      password
    });
    return response.data.data;
  },
  
  // 退出登录
  logout: async () => {
    const response = await apiClient.post<ApiResponse<{ success: boolean }>>('/auth/logout');
    localStorage.removeItem('token');
    return response.data.data;
  }
}; 