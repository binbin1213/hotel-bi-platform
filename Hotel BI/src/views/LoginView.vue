<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Lock, User } from '@element-plus/icons-vue';
import { authService } from '../api/services';

const router = useRouter();
const loading = ref(false);

const loginForm = reactive({
  username: '',
  password: '',
});

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

const formRef = ref();

const login = async (formEl: any) => {
  if (!formEl) return;
  
  await formEl.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true;
      
      try {
        // 尝试调用真实的登录API
        try {
          const result = await authService.login(loginForm.username, loginForm.password);
          
          // 保存token
          localStorage.setItem('token', result.token);
          
          ElMessage({
            message: '登录成功',
            type: 'success',
          });
          
          router.push('/dashboard');
        } catch (error: any) {
          console.error('API登录失败，使用模拟登录', error);
          
          // 模拟登录 - 仅用于开发测试
          if (loginForm.username === 'admin' && loginForm.password === 'admin') {
            localStorage.setItem('token', 'mock-jwt-token');
            
            ElMessage({
              message: '模拟登录成功',
              type: 'success',
            });
            
            router.push('/dashboard');
          } else {
            ElMessage.error('用户名或密码错误');
          }
        }
      } catch (error: any) {
        ElMessage.error(error.message || '登录失败，请检查用户名和密码');
        console.error('Login error:', error);
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<template>
  <div class="login-container">
    <div class="login-background">
      <div class="login-shape shape-1"></div>
      <div class="login-shape shape-2"></div>
      <div class="login-shape shape-3"></div>
    </div>
    
    <el-card class="login-card">
      <div class="login-header">
        <img src="../assets/logo.svg" alt="Logo" class="login-logo" />
        <h1 class="login-title">酒店业BI报告平台</h1>
        <p class="login-subtitle">专业的酒店数据分析与报告生成平台</p>
      </div>
      
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        label-position="top"
        class="login-form"
        @keyup.enter="login(formRef)"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            clearable
            class="login-input"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            class="login-input"
          />
        </el-form-item>
        
        <div class="login-options">
          <el-checkbox class="remember-me">记住我</el-checkbox>
          <a href="#" class="forgot-password">忘记密码？</a>
        </div>
        
        <el-button
          type="primary"
          :loading="loading"
          class="login-button"
          @click="login(formRef)"
        >
          登录
        </el-button>
      </el-form>
      
      <div class="login-footer">
        <p>© {{ new Date().getFullYear() }} 酒店业BI报告平台 | 技术支持: 数据分析团队</p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100vw;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #e3ecff 0%, #f8fbff 100%);
  padding: 0;
  margin: 0;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.login-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
  opacity: 0.5;
}

.shape-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.4) 0%, rgba(103, 194, 58, 0.2) 100%);
  top: -100px;
  right: -100px;
  animation: float 15s ease-in-out infinite alternate;
}

.shape-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.3) 0%, rgba(64, 158, 255, 0.2) 100%);
  bottom: -50px;
  left: -50px;
  animation: float 20s ease-in-out infinite alternate-reverse;
}

.shape-3 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2) 0%, rgba(64, 158, 255, 0.3) 100%);
  top: 40%;
  left: 30%;
  animation: float 25s ease-in-out infinite alternate;
}

@keyframes float {
  0% {
    transform: translate(0, 0) rotate(0deg);
  }
  100% {
    transform: translate(50px, 30px) rotate(10deg);
  }
}

.login-card {
  width: 100%;
  max-width: 520px;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1), 0 10px 30px rgba(64, 158, 255, 0.1);
  overflow: hidden;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 50px;
  transform: translateY(0);
  transition: all 0.3s ease;
  z-index: 10;
  position: relative;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 65px rgba(0, 0, 0, 0.12), 0 15px 35px rgba(64, 158, 255, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-logo {
  width: 90px;
  height: 90px;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 12px rgba(64, 158, 255, 0.2));
  animation: pulse 2s infinite alternate;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.05);
  }
}

.login-title {
  margin: 0;
  font-size: 28px;
  color: #23408e;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.login-subtitle {
  margin-top: 12px;
  color: #5a6a8a;
  font-size: 16px;
  font-weight: 400;
}

.login-form {
  margin-bottom: 30px;
}

.login-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 15px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #e6eaf3;
  transition: all 0.3s ease;
}

.login-input :deep(.el-input__wrapper:hover),
.login-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 5px 15px rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.login-input :deep(.el-input__prefix) {
  margin-right: 10px;
  color: #5a6a8a;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.remember-me :deep(.el-checkbox__label) {
  color: #5a6a8a;
}

.remember-me :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #409EFF;
  border-color: #409EFF;
}

.forgot-password {
  color: #409EFF;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;
}

.forgot-password:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.login-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: 12px;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  height: 50px;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(64, 158, 255, 0.2);
  background: linear-gradient(90deg, #66b1ff 0%, #85ce61 100%);
}

.login-button:active {
  transform: translateY(0);
}

.login-footer {
  text-align: center;
  margin-top: 40px;
  color: #909399;
  font-size: 13px;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .login-card {
    max-width: 90%;
    padding: 30px 20px;
    margin: 0 15px;
  }
  
  .login-logo {
    width: 70px;
    height: 70px;
  }
  
  .login-title {
    font-size: 24px;
  }
  
  .login-subtitle {
    font-size: 14px;
  }
}
</style> 