<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { dataService } from '../api/services';
import type { HotelData, KPIMetric } from '../types/models';

// 状态
const isLoading = ref(true);
const hotels = ref<HotelData[]>([]);
const selectedHotel = ref<number | null>(null);
const kpiMetrics = ref<KPIMetric[]>([]);
const dateRange = ref({
  start: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0], // 一个月前
  end: new Date().toISOString().split('T')[0] // 今天
});

// 加载数据
onMounted(async () => {
  try {
    // 加载酒店列表
    hotels.value = await dataService.getHotels();
    
    // 如果有酒店，选择第一个
    if (hotels.value.length > 0) {
      selectedHotel.value = hotels.value[0].id;
      await loadKPIData();
    }
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
  } finally {
    isLoading.value = false;
  }
});

// 加载KPI数据
const loadKPIData = async () => {
  if (!selectedHotel.value) return;
  
  try {
    isLoading.value = true;
    kpiMetrics.value = await dataService.getMetrics({
      hotel_id: selectedHotel.value,
      period_type: 'daily'
    });
  } catch (error) {
    console.error('Failed to load KPI metrics:', error);
  } finally {
    isLoading.value = false;
  }
};

// 处理酒店选择变化
const handleHotelChange = async () => {
  await loadKPIData();
};

// 处理日期范围变化
const handleDateRangeChange = async () => {
  await loadKPIData();
};

// 计算KPI摘要数据
const kpiSummary = computed(() => {
  if (kpiMetrics.value.length === 0) return null;
  
  // 按指标名称分组
  const groupedMetrics: Record<string, KPIMetric[]> = {};
  kpiMetrics.value.forEach(metric => {
    if (!groupedMetrics[metric.metric_name]) {
      groupedMetrics[metric.metric_name] = [];
    }
    groupedMetrics[metric.metric_name].push(metric);
  });
  
  // 计算平均值
  const summary: Record<string, number> = {};
  Object.entries(groupedMetrics).forEach(([name, metrics]) => {
    const sum = metrics.reduce((acc, metric) => acc + (metric.metric_value || 0), 0);
    summary[name] = sum / metrics.length;
  });
  
  return summary;
});
</script>

<template>
  <div class="dashboard-container">
    <h1>酒店业绩仪表盘</h1>
    
    <div class="filters">
      <div class="filter-group">
        <label for="hotel-select">选择酒店</label>
        <select 
          id="hotel-select" 
          v-model="selectedHotel"
          @change="handleHotelChange"
        >
          <option v-for="hotel in hotels" :key="hotel.id" :value="hotel.id">
            {{ hotel.hotel_name }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="date-start">开始日期</label>
        <input 
          id="date-start" 
          type="date" 
          v-model="dateRange.start"
          @change="handleDateRangeChange"
        />
      </div>
      
      <div class="filter-group">
        <label for="date-end">结束日期</label>
        <input 
          id="date-end" 
          type="date" 
          v-model="dateRange.end"
          @change="handleDateRangeChange"
        />
      </div>
    </div>
    
    <div v-if="isLoading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="hotels.length === 0" class="no-data">
      <p>暂无酒店数据，请先上传数据。</p>
      <router-link to="/upload" class="upload-link">上传数据</router-link>
    </div>
    
    <div v-else>
      <!-- KPI摘要卡片 -->
      <div class="kpi-cards">
        <div class="kpi-card" v-if="kpiSummary?.occupancy_rate !== undefined">
          <h3>入住率</h3>
          <div class="kpi-value">{{ (kpiSummary.occupancy_rate * 100).toFixed(2) }}%</div>
        </div>
        
        <div class="kpi-card" v-if="kpiSummary?.adr !== undefined">
          <h3>平均房价</h3>
          <div class="kpi-value">¥{{ kpiSummary.adr.toFixed(2) }}</div>
        </div>
        
        <div class="kpi-card" v-if="kpiSummary?.revpar !== undefined">
          <h3>每可用房收入</h3>
          <div class="kpi-value">¥{{ kpiSummary.revpar.toFixed(2) }}</div>
        </div>
        
        <div class="kpi-card" v-if="kpiSummary?.revenue !== undefined">
          <h3>总收入</h3>
          <div class="kpi-value">¥{{ (kpiSummary.revenue / 10000).toFixed(2) }}万</div>
        </div>
      </div>
      
      <!-- 图表占位符 -->
      <div class="charts-container">
        <div class="chart">
          <h3>入住率趋势</h3>
          <div class="chart-placeholder">
            <p>这里将显示入住率趋势图表</p>
            <p class="chart-note">（需要集成ECharts或其他图表库）</p>
          </div>
        </div>
        
        <div class="chart">
          <h3>收入趋势</h3>
          <div class="chart-placeholder">
            <p>这里将显示收入趋势图表</p>
            <p class="chart-note">（需要集成ECharts或其他图表库）</p>
          </div>
        </div>
      </div>
      
      <!-- 生成报告按钮 -->
      <div class="report-actions">
        <router-link to="/reports" class="report-button">生成分析报告</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.filters {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.no-data {
  text-align: center;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.upload-link {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background-color: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

.kpi-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.kpi-card h3 {
  margin: 0;
  color: #666;
  font-size: 1rem;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 600;
  margin-top: 1rem;
  color: #333;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart h3 {
  margin-top: 0;
  color: #333;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  border-radius: 4px;
  color: #666;
}

.chart-note {
  font-size: 0.8rem;
  color: #999;
}

.report-actions {
  text-align: center;
  margin-top: 2rem;
}

.report-button {
  display: inline-block;
  padding: 0.75rem 2rem;
  background-color: #2196F3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 500;
}
</style> 