<template>
  <div class="users-container">
    <div class="page-header">
      <h1>用户管理</h1>
      <p>管理系统用户账号和权限设置</p>
    </div>
    
    <div class="users-actions">
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>添加用户
      </el-button>
      <el-input
        v-model="searchQuery"
        placeholder="搜索用户"
        class="search-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>
    
    <el-table
      :data="filteredUsers"
      style="width: 100%"
      border
      v-loading="loading"
      element-loading-text="加载用户数据中..."
    >
      <el-table-column type="index" width="60" align="center" />
      <el-table-column prop="name" label="姓名" min-width="120">
        <template #default="scope">
          <div class="user-info">
            <el-avatar :size="30" :src="scope.row.avatar">{{ scope.row.name.substring(0, 1) }}</el-avatar>
            <span class="user-name">{{ scope.row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="role" label="角色" width="120">
        <template #default="scope">
          <el-tag :type="getRoleTagType(scope.row.role)">{{ scope.row.role }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="department" label="部门" min-width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="phone" label="电话" min-width="120" />
      <el-table-column prop="lastLogin" label="最后登录时间" min-width="180" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            :active-value="'启用'"
            :inactive-value="'禁用'"
            @change="handleStatusChange(scope.row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" @click="editUser(scope.row)">编辑</el-button>
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
    
    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="600px"
    >
      <el-form :model="userForm" label-width="100px" :rules="rules" ref="userFormRef">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="管理员" />
            <el-option label="经理" value="经理" />
            <el-option label="数据分析师" value="数据分析师" />
            <el-option label="普通用户" value="普通用户" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" placeholder="请输入部门" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="userForm.status">
            <el-radio label="启用">启用</el-radio>
            <el-radio label="禁用">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Search } from '@element-plus/icons-vue';

interface User {
  id: number;
  name: string;
  username: string;
  role: string;
  department: string;
  email: string;
  phone: string;
  lastLogin: string;
  status: string;
  avatar?: string;
}

interface UserForm {
  id: number;
  name: string;
  username: string;
  password: string;
  role: string;
  department: string;
  email: string;
  phone: string;
  status: string;
}

// 模拟数据
const users = ref<User[]>([
  {
    id: 1,
    name: '张三',
    username: 'admin',
    role: '管理员',
    department: '信息技术部',
    email: 'zhangsan@example.com',
    phone: '13800138000',
    lastLogin: '2023-06-14 15:30:22',
    status: '启用',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  },
  {
    id: 2,
    name: '李四',
    username: 'manager',
    role: '经理',
    department: '运营部',
    email: 'lisi@example.com',
    phone: '13900139000',
    lastLogin: '2023-06-13 09:15:45',
    status: '启用'
  },
  {
    id: 3,
    name: '王五',
    username: 'analyst',
    role: '数据分析师',
    department: '市场部',
    email: 'wangwu@example.com',
    phone: '13700137000',
    lastLogin: '2023-06-12 16:20:18',
    status: '启用'
  },
  {
    id: 4,
    name: '赵六',
    username: 'user',
    role: '普通用户',
    department: '财务部',
    email: 'zhaoliu@example.com',
    phone: '13600136000',
    lastLogin: '2023-06-10 11:45:30',
    status: '禁用'
  }
]);

const loading = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const totalItems = ref(users.value.length);
const dialogVisible = ref(false);
const isEdit = ref(false);
const userFormRef = ref(null);

// 表单数据
const userForm = reactive<UserForm>({
  id: 0,
  name: '',
  username: '',
  password: '',
  role: '',
  department: '',
  email: '',
  phone: '',
  status: '启用'
});

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
};

// 计算属性
const filteredUsers = computed(() => {
  if (!searchQuery.value) {
    return users.value;
  }
  return users.value.filter(user => 
    user.name.includes(searchQuery.value) ||
    user.username.includes(searchQuery.value) ||
    user.role.includes(searchQuery.value) ||
    user.department.includes(searchQuery.value) ||
    user.email.includes(searchQuery.value) ||
    user.phone.includes(searchQuery.value)
  );
});

// 方法
const showAddDialog = () => {
  isEdit.value = false;
  resetForm();
  dialogVisible.value = true;
};

const editUser = (row: User) => {
  isEdit.value = true;
  resetForm();
  userForm.id = row.id;
  userForm.name = row.name;
  userForm.username = row.username;
  userForm.role = row.role;
  userForm.department = row.department;
  userForm.email = row.email;
  userForm.phone = row.phone;
  userForm.status = row.status;
  dialogVisible.value = true;
};

const resetForm = () => {
  userForm.id = 0;
  userForm.name = '';
  userForm.username = '';
  userForm.password = '';
  userForm.role = '';
  userForm.department = '';
  userForm.email = '';
  userForm.phone = '';
  userForm.status = '启用';
};

const saveUser = () => {
  const formRef = userFormRef.value as any;
  if (formRef) {
    formRef.validate((valid: boolean) => {
      if (valid) {
        if (isEdit.value) {
          // 更新用户
          const index = users.value.findIndex(user => user.id === userForm.id);
          if (index !== -1) {
            users.value[index] = {
              ...users.value[index],
              name: userForm.name,
              username: userForm.username,
              role: userForm.role,
              department: userForm.department,
              email: userForm.email,
              phone: userForm.phone,
              status: userForm.status
            };
          }
          ElMessage.success('用户更新成功');
        } else {
          // 添加用户
          const newId = Math.max(...users.value.map(user => user.id), 0) + 1;
          users.value.push({
            id: newId,
            name: userForm.name,
            username: userForm.username,
            role: userForm.role,
            department: userForm.department,
            email: userForm.email,
            phone: userForm.phone,
            status: userForm.status,
            lastLogin: '从未登录'
          });
          ElMessage.success('用户添加成功');
        }
        dialogVisible.value = false;
      } else {
        return false;
      }
    });
  }
};

const confirmDelete = (row: User) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    users.value = users.value.filter(user => user.id !== row.id);
    ElMessage.success('删除成功');
  }).catch(() => {});
};

const handleStatusChange = (row: User) => {
  const status = row.status === '启用' ? '启用' : '禁用';
  ElMessage.success(`用户 ${row.name} 已${status}`);
};

const handleSizeChange = (val: number) => {
  pageSize.value = val;
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
};

const getRoleTagType = (role: string) => {
  const roleMap: Record<string, string> = {
    '管理员': 'danger',
    '经理': 'warning',
    '数据分析师': 'success',
    '普通用户': 'info'
  };
  return roleMap[role] || 'info';
};

onMounted(() => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 800);
});
</script>

<style scoped>
.users-container {
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

.users-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  margin-left: 10px;
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