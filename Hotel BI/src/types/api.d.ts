declare module '../api/services' {
  import type { HotelData, KPIMetric, Report, TaskStatus, ApiResponse } from '../types/models';
  
  export const dataService: {
    getHotels: () => Promise<HotelData[]>;
    getHotelById: (hotelId: number) => Promise<HotelData>;
    getMetrics: (params?: { 
      hotel_id?: number, 
      period_type?: string,
      start_date?: string,
      end_date?: string
    }) => Promise<KPIMetric[]>;
  };
  
  export const uploadService: {
    uploadFile: (file: File, hotelId: string) => Promise<{ task_id: string }>;
    getTemplates: () => Promise<{ name: string; url: string }[]>;
  };
  
  export const reportService: {
    generateReport: (reportData: {
      title: string;
      report_type: string;
      hotel_ids: number[];
      period_start?: string;
      period_end?: string;
      output_formats: string[];
    }) => Promise<{ task_id: string }>;
    getReports: () => Promise<Report[]>;
    getReportById: (reportId: number) => Promise<Report>;
    downloadReport: (reportId: number, format: 'pdf' | 'ppt') => Promise<Blob>;
  };
  
  export const taskService: {
    getTasks: () => Promise<TaskStatus[]>;
    getTaskStatus: (taskId: string) => Promise<TaskStatus>;
    cancelTask: (taskId: string) => Promise<{ success: boolean }>;
    pollTaskStatus: (taskId: string, callback: (status: TaskStatus) => void) => () => void;
  };
  
  export const authService: {
    login: (username: string, password: string) => Promise<{ token: string; user: { id: number; username: string; role: string } }>;
    logout: () => Promise<{ success: boolean }>;
  };
} 