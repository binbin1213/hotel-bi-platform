<template>
  <div class="data-source-container">
    <div class="page-header">
      <h1>数据源管理</h1>
      <p>管理和配置系统中的各种数据源连接</p>
    </div>
    
    <div class="data-source-actions">
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>添加数据源
      </el-button>
      <el-input
        v-model="searchQuery"
        placeholder="搜索数据源"
        class="search-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>
    
    <el-table
      :data="filteredDataSources"
      style="width: 100%"
      border
      v-loading="loading"
      element-loading-text="加载数据源中..."
    >
      <el-table-column prop="name" label="数据源名称" min-width="180">
        <template #default="scope">
          <div class="data-source-name">
            <el-icon :class="getIconClass(scope.row.type)"><DataLine /></el-icon>
            <span>{{ scope.row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="120">
        <template #default="scope">
          <el-tag :type="getTagType(scope.row.type)">{{ scope.row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="host" label="主机/服务器" min-width="180" />
      <el-table-column prop="database" label="数据库名称" min-width="150" />
      <el-table-column prop="lastSync" label="最后同步时间" width="180" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === '已连接' ? 'success' : 'danger'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="testConnection(scope.row)">测试连接</el-button>
          <el-button size="small" type="primary" @click="editDataSource(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      v-if="totalItems > 0"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="totalItems"
      layout="total, sizes, prev, pager, next, jumper"
      :page-sizes="[10, 20, 50, 100]"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      class="pagination"
    />
    
    <!-- 添加/编辑数据源对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑数据源' : '添加数据源'"
      width="600px"
    >
      <el-form :model="dataSourceForm" label-width="120px" :rules="rules" ref="dataSourceFormRef">
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="数据源类型" prop="type">
          <el-select v-model="dataSourceForm.type" placeholder="请选择数据源类型" style="width: 100%">
            <el-option label="MySQL" value="MySQL" />
            <el-option label="PostgreSQL" value="PostgreSQL" />
            <el-option label="SQL Server" value="SQL Server" />
            <el-option label="Oracle" value="Oracle" />
            <el-option label="Excel文件" value="Excel" />
            <el-option label="CSV文件" value="CSV" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机/服务器" prop="host" v-if="!isFileType">
          <el-input v-model="dataSourceForm.host" placeholder="请输入主机地址" />
        </el-form-item>
        <el-form-item label="端口" prop="port" v-if="!isFileType">
          <el-input v-model.number="dataSourceForm.port" placeholder="请输入端口号" />
        </el-form-item>
        <el-form-item label="数据库名称" prop="database" v-if="!isFileType">
          <el-input v-model="dataSourceForm.database" placeholder="请输入数据库名称" />
        </el-form-item>
        <el-form-item label="用户名" prop="username" v-if="!isFileType">
          <el-input v-model="dataSourceForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isFileType">
          <el-input v-model="dataSourceForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="文件路径" prop="filePath" v-if="isFileType">
          <el-input v-model="dataSourceForm.filePath" placeholder="请选择文件">
            <template #append>
              <el-button @click="selectFile">选择文件</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input
            v-model="dataSourceForm.description"
            type="textarea"
            placeholder="请输入备注信息"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveDataSource">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Search, DataLine } from '@element-plus/icons-vue';

// 模拟数据
const dataSources = ref([
  {
    id: 1,
    name: '酒店业务数据库',
    type: 'MySQL',
    host: 'db.hotel-data.com',
    port: 3306,
    database: 'hotel_business',
    username: 'admin',
    lastSync: '2023-06-14 15:30:22',
    status: '已连接'
  },
  {
    id: 2,
    name: '客户关系管理',
    type: 'PostgreSQL',
    host: 'crm.hotel-data.com',
    port: 5432,
    database: 'hotel_crm',
    username: 'crm_user',
    lastSync: '2023-06-14 12:15:45',
    status: '已连接'
  },
  {
    id: 3,
    name: '历史数据',
    type: 'SQL Server',
    host: '192.168.1.100',
    port: 1433,
    database: 'hotel_history',
    username: 'reader',
    lastSync: '2023-06-13 23:10:18',
    status: '连接失败'
  },
  {
    id: 4,
    name: '季度财务报表',
    type: 'Excel',
    filePath: '/data/finance/Q2_2023.xlsx',
    lastSync: '2023-06-10 09:45:30',
    status: '已连接'
  }
]);

const loading = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const totalItems = ref(dataSources.value.length);
const dialogVisible = ref(false);
const isEdit = ref(false);
const dataSourceFormRef = ref(null);

// 表单数据
const dataSourceForm = reactive({
  id: 0,
  name: '',
  type: '',
  host: '',
  port: null,
  database: '',
  username: '',
  password: '',
  filePath: '',
  description: ''
});

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择数据源类型', trigger: 'change' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  database: [{ required: true, message: '请输入数据库名称', trigger: 'blur' }],
  filePath: [{ required: true, message: '请选择文件', trigger: 'blur' }]
};

// 计算属性
const filteredDataSources = computed(() => {
  if (!searchQuery.value) {
    return dataSources.value;
  }
  return dataSources.value.filter(ds => 
    ds.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    ds.type.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    ds.host?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    ds.database?.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const isFileType = computed(() => {
  return ['Excel', 'CSV'].includes(dataSourceForm.type);
});

// 方法
const showAddDialog = () => {
  isEdit.value = false;
  resetForm();
  dialogVisible.value = true;
};

const editDataSource = (row) => {
  isEdit.value = true;
  Object.assign(dataSourceForm, row);
  dialogVisible.value = true;
};

const resetForm = () => {
  dataSourceForm.id = 0;
  dataSourceForm.name = '';
  dataSourceForm.type = '';
  dataSourceForm.host = '';
  dataSourceForm.port = null;
  dataSourceForm.database = '';
  dataSourceForm.username = '';
  dataSourceForm.password = '';
  dataSourceForm.filePath = '';
  dataSourceForm.description = '';
};

const saveDataSource = () => {
  if (dataSourceFormRef.value) {
    dataSourceFormRef.value.validate((valid) => {
      if (valid) {
        if (isEdit.value) {
          // 更新数据源
          const index = dataSources.value.findIndex(ds => ds.id === dataSourceForm.id);
          if (index !== -1) {
            dataSources.value[index] = { ...dataSourceForm };
          }
          ElMessage.success('数据源更新成功');
        } else {
          // 添加数据源
          const newId = Math.max(...dataSources.value.map(ds => ds.id), 0) + 1;
          dataSources.value.push({
            ...dataSourceForm,
            id: newId,
            lastSync: '从未同步',
            status: '已连接'
          });
          ElMessage.success('数据源添加成功');
        }
        dialogVisible.value = false;
      } else {
        return false;
      }
    });
  }
};

const confirmDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除数据源 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    dataSources.value = dataSources.value.filter(ds => ds.id !== row.id);
    ElMessage.success('删除成功');
  }).catch(() => {});
};

const testConnection = (row) => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
    if (Math.random() > 0.2) {
      ElMessage.success(`连接到 ${row.name} 成功`);
      // 更新状态
      const index = dataSources.value.findIndex(ds => ds.id === row.id);
      if (index !== -1) {
        dataSources.value[index].status = '已连接';
      }
    } else {
      ElMessage.error(`连接到 ${row.name} 失败，请检查连接信息`);
      // 更新状态
      const index = dataSources.value.findIndex(ds => ds.id === row.id);
      if (index !== -1) {
        dataSources.value[index].status = '连接失败';
      }
    }
  }, 1500);
};

const selectFile = () => {
  ElMessage.info('文件选择功能将在后续版本中实现');
};

const handleSizeChange = (val) => {
  pageSize.value = val;
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
};

const getTagType = (type) => {
  const typeMap = {
    'MySQL': 'primary',
    'PostgreSQL': 'success',
    'SQL Server': 'warning',
    'Oracle': 'danger',
    'Excel': 'info',
    'CSV': 'info'
  };
  return typeMap[type] || 'info';
};

const getIconClass = (type) => {
  return 'data-source-icon';
};

onMounted(() => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 800);
});
</script>

<style scoped>
.data-source-container {
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

.data-source-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.data-source-name {
  display: flex;
  align-items: center;
}

.data-source-icon {
  margin-right: 8px;
  font-size: 18px;
  color: #409EFF;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.el-table .cell) {
  white-space: nowrap;
}
</style> 