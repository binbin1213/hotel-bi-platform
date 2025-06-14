// 酒店数据模型
export interface HotelData {
  id: number;
  hotel_name: string;
  location?: string;
  room_count?: number;
  rooms_occupied?: number;
  occupancy_rate?: number;
  revenue?: number;
  adr?: number;  // Average Daily Rate (平均房价)
  revpar?: number;  // Revenue Per Available Room (每可用房收入)
  date_recorded?: string;  // YYYY-MM-DD
  created_at: string;  // ISO日期时间
  updated_at: string;  // ISO日期时间
}

// KPI指标模型
export interface KPIMetric {
  id: number;
  hotel_id: number;
  metric_name: string;
  metric_value?: number;
  metric_type?: string;
  period_type?: string;  // 'daily', 'weekly', 'monthly', 'yearly'
  period_start?: string;  // YYYY-MM-DD
  period_end?: string;  // YYYY-MM-DD
}

// 报告模型
export interface Report {
  id: number;
  title: string;
  report_type: string;  // 'analysis', 'comparison', 'forecast'
  status: string;  // 'pending', 'processing', 'completed', 'failed'
  created_at: string;  // ISO日期时间
  completed_at?: string;  // ISO日期时间
  file_paths?: {
    pdf?: string;
    ppt?: string;
  };
}

// 任务状态模型
export interface TaskStatus {
  id: number;
  task_id: string;  // Celery任务ID
  task_type: string;
  status: string;  // 'pending', 'running', 'completed', 'failed'
  progress: number;  // 0-100
  started_at?: string;  // ISO日期时间
  completed_at?: string;  // ISO日期时间
  error_message?: string;
} 