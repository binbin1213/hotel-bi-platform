<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { 
  Menu as IconMenu, 
  House as IconHouse, 
  Document as IconDocument, 
  Upload as IconUpload, 
  Setting as IconSetting,
  User as IconUser,
  Lock as IconLock,
  Switch as IconSwitch
} from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const isCollapse = ref(false);

// 添加currentPath计算属性
const currentPath = computed(() => {
  const pathMap: { [key: string]: string } = {
    '/dashboard': '仪表盘',
    '/reports': '报表管理',
    '/upload': '上传数据',
    '/data': '数据源',
    '/users': '用户管理',
    '/settings': '系统设置'
  }
  return pathMap[route.path] || '首页'
});

// 将activeMenu从计算属性改为ref，以便可以手动设置
const activeMenu = ref(route.path);

// 计算当前是否在登录页面
const isLoginPage = computed(() => {
  return route.path === '/login';
});

onMounted(() => {
  // 根据当前路由设置活动菜单项
  activeMenu.value = route.path;
});

const handleMenuSelect = (key: string) => {
  router.push(key);
};

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};
</script>

<template>
  <!-- 登录页面不显示布局 -->
  <router-view v-if="isLoginPage" />
  
  <!-- 其他页面显示带侧边栏的布局 -->
  <el-container class="layout-container" v-else>
    <el-aside :width="isCollapse ? '64px' : '200px'" class="main-aside">
      <div class="logo-container">
        <div class="logo-content">
          <img v-if="!isCollapse" src="./assets/logo.svg" class="logo-img" alt="酒店BI平台" />
          <img v-else src="./assets/logo-small.svg" class="logo-small" alt="酒店BI平台" />
          <div class="logo-text" v-show="!isCollapse">酒店BI平台</div>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        :collapse="isCollapse"
        background-color="#001529"
        text-color="#fff"
        active-text-color="#409EFF"
        :collapse-transition="false"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><Document /></el-icon>
          <span>报表管理</span>
        </el-menu-item>
        <el-menu-item index="/upload">
          <el-icon><Upload /></el-icon>
          <span>上传数据</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <el-icon><DataLine /></el-icon>
          <span>数据源</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon v-if="isCollapse"><Expand /></el-icon>
        <el-icon v-else><Fold /></el-icon>
      </div>
    </el-aside>
    
    <el-container class="content-container">
      <el-header class="main-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPath }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown trigger="click">
            <div class="avatar-container">
              <div class="admin-avatar">
                <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="40" cy="40" r="40" fill="url(#adminGradient)"/>
                  <path d="M40 20C35.58 20 32 23.58 32 28C32 32.42 35.58 36 40 36C44.42 36 48 32.42 48 28C48 23.58 44.42 20 40 20ZM40 38C33.32 38 20 41.34 20 48V52C20 53.1 20.9 54 22 54H58C59.1 54 60 53.1 60 52V48C60 41.34 46.68 38 40 38Z" fill="white"/>
                  <defs>
                    <linearGradient id="adminGradient" x1="0" y1="0" x2="80" y2="80" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stop-color="#4776E6"/>
                      <stop offset="100%" stop-color="#8E54E9"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <div class="user-info">
                <span class="username">管理员</span>
                <span class="role">系统管理员</span>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <div class="menu-item-content">
                    <div class="menu-icon-wrapper">
                      <div class="menu-icon user-icon"></div>
                    </div>
                    <span>个人信息</span>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item>
                  <div class="menu-item-content">
                    <div class="menu-icon-wrapper">
                      <div class="menu-icon password-icon"></div>
                    </div>
                    <span>修改密码</span>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item divided>
                  <div class="menu-item-content">
                    <div class="menu-icon-wrapper">
                      <div class="menu-icon logout-icon"></div>
                    </div>
                    <span>退出登录</span>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
      
      <el-footer class="footer">
        © {{ new Date().toLocaleDateString('zh-CN', {year: 'numeric', month: 'long', day: 'numeric'}) }} 酒店业BI报告平台 | 版本 v1.0.0
      </el-footer>
    </el-container>
  </el-container>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: linear-gradient(135deg, #e3ecff 0%, #f8fbff 100%);
}

.main-aside {
  background: linear-gradient(180deg, #e3ecff 0%, #409EFF 60%, #67C23A 100%);
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  border-top-left-radius: 28px;
  border-bottom-left-radius: 28px;
  border-top-right-radius: 18px;
  border-bottom-right-radius: 18px;
  box-shadow: 4px 0 24px 0 rgba(64,158,255,0.10);
  min-width: 0;
}

.logo-container {
  height: 90px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.05);
  border-radius: 0;
  margin: 0 0 20px 0;
  transition: all 0.3s;
}

.logo-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
}

.logo-img {
  height: 40px;
  filter: brightness(1.1) drop-shadow(0 2px 6px rgba(0, 0, 0, 0.15));
  transition: all 0.3s;
  margin-bottom: 10px;
}

.logo-small {
  height: 40px;
  width: 40px;
  filter: brightness(1.1) drop-shadow(0 2px 6px rgba(0, 0, 0, 0.15));
  transition: all 0.3s;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
  opacity: 0.95;
}

/* 折叠状态下Logo区变圆形icon */
.main-aside[style*='width: 64px'] .logo-container {
  width: 64px;
  height: 64px;
  min-width: 64px;
  min-height: 64px;
  border-radius: 0;
  margin: 0 0 20px 0;
  padding: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.05);
  justify-content: center;
  align-items: center;
}

.el-menu-vertical {
  border-right: none;
  background-color: transparent;
  margin-top: 18px;
  padding: 0 10px;
}

.el-menu-vertical :deep(.el-menu-item) {
  color: #23408e;
  border-radius: 16px;
  margin: 12px 0;
  font-size: 18px;
  font-weight: 600;
  height: 52px;
  display: flex;
  align-items: center;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s, transform 0.2s;
  padding-left: 18px !important;
}

.el-menu-vertical :deep(.el-menu-item .el-icon) {
  font-size: 26px !important;
  margin-right: 14px;
  transition: all 0.2s;
}

/* 折叠状态下菜单项样式优化 */
.main-aside[style*='width: 64px'] .el-menu-vertical {
  padding: 0;
  width: 64px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-aside[style*='width: 64px'] .el-menu-vertical :deep(.el-menu-item) {
  padding: 0 !important;
  margin: 8px auto;
  height: 48px;
  width: 48px;
  min-width: 48px;
  border-radius: 50%;
  background: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-aside[style*='width: 64px'] .el-menu-vertical :deep(.el-tooltip) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.main-aside[style*='width: 64px'] .el-menu-vertical :deep(.el-menu-item .el-icon) {
  margin: 0 !important;
  font-size: 22px !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-aside[style*='width: 64px'] .el-menu-vertical :deep(.el-menu-item.is-active),
.main-aside[style*='width: 64px'] .el-menu-vertical :deep(.el-menu-item:hover) {
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  box-shadow: 0 2px 8px rgba(64,158,255,0.12);
  transform: scale(1.08);
}

.main-aside[style*='width: 64px'] .el-menu-vertical :deep(.el-menu-item.is-active .el-icon),
.main-aside[style*='width: 64px'] .el-menu-vertical :deep(.el-menu-item:hover .el-icon) {
  color: #fff !important;
  transform: scale(1.18);
}

/* 折叠时隐藏菜单文字 */
.main-aside[style*='width: 64px'] .el-menu-vertical :deep(.el-menu-item__title) {
  display: none !important;
}

/* 确保tooltip正常显示 */
:deep(.el-popper.is-light) {
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.el-menu-vertical :deep(.el-menu-item.is-active) {
  color: #fff;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  box-shadow: 0 4px 16px rgba(64,158,255,0.15);
}

.el-menu-vertical :deep(.el-menu-item:hover) {
  color: #fff;
  background: linear-gradient(90deg, #67C23A 0%, #409EFF 100%);
  box-shadow: 0 2px 8px rgba(64,158,255,0.10);
}

.collapse-btn {
  color: #409EFF;
  border-radius: 50%;
  background: rgba(64,158,255,0.08);
  transition: background 0.2s, color 0.2s;
  position: absolute;
  bottom: 18px;
  right: 18px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px !important;
}

.collapse-btn:hover {
  color: #fff;
  background: #409EFF;
}

.main-header {
  background: linear-gradient(90deg, #fff 60%, #e3ecff 100%);
  border-bottom: 1px solid #e6eaf3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  box-shadow: 0 2px 8px rgba(64,158,255,0.06);
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.avatar-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.avatar-container:hover {
  background: rgba(0, 0, 0, 0.04);
}

.admin-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
}

.admin-avatar svg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  line-height: 1.2;
}

.role {
  font-size: 12px;
  color: #67C23A;
  line-height: 1.2;
}

.main-content {
  background: #f8fbff;
  padding: 0;
  overflow-y: auto;
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  border-bottom-left-radius: 18px;
  border-bottom-right-radius: 18px;
}

.footer {
  height: 40px;
  line-height: 40px;
  text-align: center;
  font-size: 12px;
  color: #909399;
  background: #f4f8ff;
  border-top: 1px solid #e6eaf3;
  border-bottom-left-radius: 18px;
  border-bottom-right-radius: 18px;
}

@media (max-width: 900px) {
  .main-aside {
    position: fixed;
    z-index: 1000;
    height: 100%;
    border-radius: 0 12px 12px 0;
    min-width: 0;
  }
  .header-title {
    font-size: 16px;
  }
  .username {
    display: none;
  }
}

.content-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  width: 100%;
}

/* 优化tooltip样式 */
:deep(.el-tooltip__popper) {
  font-size: 14px !important;
  padding: 6px 12px !important;
  border-radius: 4px !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.menu-item-content {
  display: flex;
  align-items: center;
  width: 100%;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f0f7ff;
}

.menu-icon-wrapper {
  width: 20px;
  height: 20px;
  margin-right: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

:deep(.el-dropdown-menu__item:hover) .menu-icon-wrapper {
  transform: scale(1.1);
}

.menu-icon {
  width: 16px;
  height: 16px;
  background-position: center;
  background-repeat: no-repeat;
  background-size: contain;
}

.user-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%234d8bf9"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>');
}

.password-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%234d8bf9"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>');
}

.logout-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%234d8bf9"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>');
}

:deep(.el-dropdown-menu) {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  padding: 4px 0;
  border: 1px solid #e6eaf3;
  min-width: 120px;
}

:deep(.el-dropdown-menu__item.is-divided) {
  position: relative;
  margin-top: 6px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-dropdown-menu__item.is-divided)::before {
  content: '';
  height: 1px;
  display: block;
  margin: 0 -16px;
  background-color: #ebeef5;
  position: absolute;
  top: -4px;
  left: 0;
  right: 0;
}
</style>
