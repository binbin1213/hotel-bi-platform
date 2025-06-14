-- 创建酒店数据表
CREATE TABLE IF NOT EXISTS hotel_data (
    id SERIAL PRIMARY KEY,
    hotel_name VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    room_count INTEGER,
    occupancy_rate DECIMAL(5,2),
    revenue DECIMAL(15,2),
    adr DECIMAL(10,2),  -- Average Daily Rate
    revpar DECIMAL(10,2), -- Revenue Per Available Room
    date_recorded DATE,
    data_source VARCHAR(100), -- 数据来源
    is_validated BOOLEAN DEFAULT false, -- 数据是否已验证
    validation_errors JSONB, -- 验证错误信息
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加索引提高查询性能
CREATE INDEX IF NOT EXISTS idx_hotel_data_date ON hotel_data(date_recorded);
CREATE INDEX IF NOT EXISTS idx_hotel_data_hotel_name ON hotel_data(hotel_name);

-- 创建KPI指标表
CREATE TABLE IF NOT EXISTS kpi_metrics (
    id SERIAL PRIMARY KEY,
    hotel_id INTEGER REFERENCES hotel_data(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_type VARCHAR(50), -- 'revenue', 'occupancy', 'satisfaction'
    period_type VARCHAR(20), -- 'daily', 'weekly', 'monthly', 'yearly'
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建报告表
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    report_type VARCHAR(50), -- 'analysis', 'comparison', 'forecast'
    content_data JSONB,
    ai_insights TEXT,
    file_paths JSONB, -- PDF, PPT文件路径
    status VARCHAR(20) DEFAULT 'pending',
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 创建任务状态表
CREATE TABLE IF NOT EXISTS task_status (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    result_data JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0, -- 重试次数
    max_retries INTEGER DEFAULT 3, -- 最大重试次数
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_task_status_task_id ON task_status(task_id);
CREATE INDEX IF NOT EXISTS idx_task_status_status ON task_status(status); 