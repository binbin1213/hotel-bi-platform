<template>
  <div class="settings-container">
    <div class="page-header">
      <h1>系统设置</h1>
      <p>配置系统参数和全局选项</p>
    </div>
    
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>基本设置</h2>
        </div>
      </template>
      
      <el-form :model="basicSettings" label-position="top" label-width="120px">
        <el-form-item label="系统名称">
          <el-input v-model="basicSettings.systemName" />
        </el-form-item>
        <el-form-item label="系统描述">
          <el-input v-model="basicSettings.systemDescription" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="管理员邮箱">
          <el-input v-model="basicSettings.adminEmail" />
        </el-form-item>
        <el-form-item label="系统语言">
          <el-select v-model="basicSettings.language" style="width: 100%">
            <el-option label="简体中文" value="zh-CN" />
            <el-option label="English" value="en-US" />
          </el-select>
        </el-form-item>
        <el-form-item label="时区">
          <el-select v-model="basicSettings.timezone" style="width: 100%">
            <el-option label="(GMT+08:00) 北京，上海，香港" value="Asia/Shanghai" />
            <el-option label="(GMT+00:00) 格林威治标准时间" value="GMT" />
            <el-option label="(GMT-08:00) 太平洋标准时间" value="America/Los_Angeles" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期格式">
          <el-select v-model="basicSettings.dateFormat" style="width: 100%">
            <el-option label="YYYY-MM-DD" value="YYYY-MM-DD" />
            <el-option label="DD/MM/YYYY" value="DD/MM/YYYY" />
            <el-option label="MM/DD/YYYY" value="MM/DD/YYYY" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveBasicSettings">保存基本设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>安全设置</h2>
        </div>
      </template>
      
      <el-form :model="securitySettings" label-position="top" label-width="120px">
        <el-form-item label="密码策略">
          <el-select v-model="securitySettings.passwordPolicy" style="width: 100%">
            <el-option label="低 (最少6个字符)" value="low" />
            <el-option label="中 (最少8个字符，包含数字和字母)" value="medium" />
            <el-option label="高 (最少10个字符，包含数字、大小写字母和特殊字符)" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码过期时间">
          <el-select v-model="securitySettings.passwordExpiration" style="width: 100%">
            <el-option label="从不" value="never" />
            <el-option label="30天" value="30days" />
            <el-option label="60天" value="60days" />
            <el-option label="90天" value="90days" />
          </el-select>
        </el-form-item>
        <el-form-item label="登录失败尝试次数">
          <el-input-number v-model="securitySettings.loginAttempts" :min="3" :max="10" />
        </el-form-item>
        <el-form-item label="锁定时间 (分钟)">
          <el-input-number v-model="securitySettings.lockoutTime" :min="5" :max="60" />
        </el-form-item>
        <el-form-item label="会话超时 (分钟)">
          <el-input-number v-model="securitySettings.sessionTimeout" :min="5" :max="120" />
        </el-form-item>
        <el-form-item>
          <el-switch
            v-model="securitySettings.twoFactorAuth"
            active-text="启用双因素认证"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSecuritySettings">保存安全设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>数据设置</h2>
        </div>
      </template>
      
      <el-form :model="dataSettings" label-position="top" label-width="120px">
        <el-form-item label="默认数据保留期限">
          <el-select v-model="dataSettings.dataRetention" style="width: 100%">
            <el-option label="1个月" value="1month" />
            <el-option label="3个月" value="3months" />
            <el-option label="6个月" value="6months" />
            <el-option label="1年" value="1year" />
            <el-option label="永久" value="forever" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据备份频率">
          <el-select v-model="dataSettings.backupFrequency" style="width: 100%">
            <el-option label="每天" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="备份保留数量">
          <el-input-number v-model="dataSettings.backupRetention" :min="1" :max="30" />
        </el-form-item>
        <el-form-item>
          <el-switch
            v-model="dataSettings.autoCleanup"
            active-text="启用自动清理过期数据"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveDataSettings">保存数据设置</el-button>
          <el-button type="warning" @click="backupNow">立即备份</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>系统维护</h2>
        </div>
      </template>
      
      <div class="maintenance-info">
        <div class="info-item">
          <span class="label">系统版本:</span>
          <span class="value">v1.0.0</span>
        </div>
        <div class="info-item">
          <span class="label">最后更新时间:</span>
          <span class="value">2025年06月15日 02:16:45</span>
        </div>
        <div class="info-item">
          <span class="label">数据库大小:</span>
          <span class="value">256.4 MB</span>
        </div>
        <div class="info-item">
          <span class="label">系统状态:</span>
          <el-tag type="success">正常运行</el-tag>
        </div>
      </div>
      
      <div class="maintenance-actions">
        <el-button type="primary" @click="checkUpdate">检查更新</el-button>
        <el-button type="warning" @click="cleanCache">清理缓存</el-button>
        <el-button type="danger" @click="confirmRestart">重启系统</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

// 基本设置
const basicSettings = reactive({
  systemName: '酒店业BI报告平台',
  systemDescription: '为酒店业提供全面的业务智能分析和报告工具',
  adminEmail: 'admin@hotel-bi.com',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  dateFormat: 'YYYY-MM-DD'
});

// 安全设置
const securitySettings = reactive({
  passwordPolicy: 'medium',
  passwordExpiration: '90days',
  loginAttempts: 5,
  lockoutTime: 30,
  sessionTimeout: 30,
  twoFactorAuth: false
});

// 数据设置
const dataSettings = reactive({
  dataRetention: '1year',
  backupFrequency: 'daily',
  backupRetention: 7,
  autoCleanup: true
});

// 保存基本设置
const saveBasicSettings = () => {
  ElMessage.success('基本设置保存成功');
};

// 保存安全设置
const saveSecuritySettings = () => {
  ElMessage.success('安全设置保存成功');
};

// 保存数据设置
const saveDataSettings = () => {
  ElMessage.success('数据设置保存成功');
};

// 立即备份
const backupNow = () => {
  ElMessage({
    message: '系统备份已开始，请稍后查看备份状态',
    type: 'info',
    duration: 3000
  });
};

// 检查更新
const checkUpdate = () => {
  ElMessage({
    message: '系统已是最新版本',
    type: 'success',
    duration: 3000
  });
};

// 清理缓存
const cleanCache = () => {
  ElMessage({
    message: '缓存清理成功，系统性能已优化',
    type: 'success',
    duration: 3000
  });
};

// 确认重启
const confirmRestart = () => {
  ElMessageBox.confirm(
    '确定要重启系统吗？所有用户将暂时无法访问系统。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage({
      message: '系统正在重启，请稍后...',
      type: 'warning',
      duration: 5000
    });
  }).catch(() => {});
};

onMounted(() => {
  // 加载设置
});
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-header p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.settings-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  font-size: 18px;
  margin: 0;
  color: #303133;
}

.maintenance-info {
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
}

.info-item .label {
  width: 150px;
  color: #606266;
}

.info-item .value {
  font-weight: 500;
  color: #303133;
}

.maintenance-actions {
  display: flex;
  gap: 12px;
}
</style>
