# 🏨 酒店业BI报告平台 | Hotel BI Platform

![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Element Plus](https://img.shields.io/badge/Element_Plus-409EFF?style=for-the-badge&logo=element&logoColor=white)
![ECharts](https://img.shields.io/badge/ECharts-AA344D?style=for-the-badge&logo=apache-echarts&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)

一个现代化的酒店业务智能分析平台，帮助酒店管理者实时监控关键业绩指标、分析经营数据并生成专业报告。

## 📸 项目截图

> *这里将放置项目截图*

## ✨ 主要功能

- 📊 **实时仪表盘** - 监控入住率、平均房价、收入等关键指标
- 📝 **报表管理** - 创建、查看和导出专业分析报告
- 📤 **数据上传** - 便捷的Excel数据导入功能
- 🔄 **数据源管理** - 灵活配置和管理多种数据来源
- 👥 **用户管理** - 基于角色的权限控制系统
- ⚙️ **系统设置** - 自定义平台配置选项

## 🛠️ 技术栈

- **前端框架**: Vue 3 (Composition API)
- **类型系统**: TypeScript
- **UI组件库**: Element Plus
- **数据可视化**: ECharts
- **路由管理**: Vue Router
- **HTTP客户端**: Axios
- **构建工具**: Vite

## 🚀 快速开始

### 前提条件

- Node.js (v16+)
- npm 或 yarn

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/binbin1213/hotel-bi-platform.git
cd hotel-bi-platform
```

2. 安装依赖
```bash
npm install
# 或
yarn install
```

3. 启动开发服务器
```bash
npm run dev
# 或
yarn dev
```

4. 构建生产版本
```bash
npm run build
# 或
yarn build
```

## 📁 项目结构

```
Hotel BI/
├── public/                 # 静态资源
├── src/
│   ├── api/                # API服务
│   │   ├── client.ts       # Axios配置
│   │   └── services.ts     # API服务封装
│   ├── assets/             # 静态资源
│   ├── components/         # 通用组件
│   ├── router/             # 路由配置
│   ├── types/              # TypeScript类型定义
│   │   └── models.ts       # 数据模型类型
│   ├── views/              # 页面组件
│   │   ├── DashboardView.vue  # 仪表盘页面
│   │   ├── LoginView.vue      # 登录页面
│   │   ├── ReportsView.vue    # 报告管理页面
│   │   ├── UploadView.vue     # 数据上传页面
│   │   ├── DataSourceView.vue # 数据源管理页面
│   │   ├── UsersView.vue      # 用户管理页面
│   │   └── SettingsView.vue   # 系统设置页面
│   ├── App.vue             # 根组件
│   └── main.ts             # 入口文件
├── package.json            # 项目依赖
└── tsconfig.json           # TypeScript配置
```

## 🖥️ 主要页面

### 仪表盘 (Dashboard)

系统的核心页面，包含：
- 酒店选择器和日期范围选择器
- KPI数据卡片，展示入住率、平均房价、每可用房收入和总收入
- 入住率趋势图和收入趋势图
- 生成分析报告的快捷按钮

### 报表管理 (Reports)

用于管理生成的报告：
- 报告列表展示
- 报告生成请求表单
- 报告下载功能

### 数据上传 (Upload)

用于上传酒店数据：
- 文件上传组件
- 上传进度显示
- 上传历史记录

### 数据源管理 (Data Source)

管理系统数据来源：
- 数据源列表
- 连接配置
- 数据同步状态

### 用户管理 (Users)

管理系统用户和权限：
- 用户列表
- 角色分配
- 权限设置

### 系统设置 (Settings)

配置系统参数：
- 系统安全设置
- 数据保留策略
- 系统维护选项

## 🔐 登录信息

开发环境下可使用以下账号登录：

- 用户名：admin
- 密码：admin

## 🔄 API服务层

采用模块化设计，将API调用封装为服务：
- `dataService`：数据相关API，如获取酒店列表、指标数据等
- `uploadService`：文件上传相关API
- `reportService`：报告管理相关API
- `taskService`：任务管理相关API
- `authService`：用户认证相关API

## 📱 响应式设计

系统采用响应式设计，适配不同屏幕尺寸：
- 大屏幕：完整显示侧边栏和所有内容
- 中屏幕：可折叠侧边栏，内容区域自适应
- 小屏幕：自动折叠侧边栏，内容区域垂直排列

## 📊 数据可视化

基于ECharts实现，主要图表类型：
- 折线图：展示入住率等时间序列数据
- 柱状图：展示收入等指标
- 数据卡片：展示关键业绩指标(KPI)

## 🎨 样式设计

采用Element Plus的设计语言，并进行了定制：
- 深色侧边栏搭配浅色内容区
- 响应式布局，确保在各种设备上的良好体验
- 数据可视化采用统一的配色方案
- 卡片式设计，增强信息层次和可读性

## 🔜 未来扩展计划

1. **状态管理优化**：考虑引入Pinia进行更复杂的状态管理
2. **国际化支持**：添加多语言支持
3. **主题切换**：支持明暗主题切换
4. **更多数据可视化**：添加更多类型的图表和分析视图
5. **离线支持**：实现部分功能的离线使用能力

## 📄 许可证

[MIT](LICENSE)

## 👥 贡献指南

欢迎贡献代码、报告问题或提出新功能建议！请查看[贡献指南](CONTRIBUTING.md)了解更多信息。

---

© 2025 酒店业BI报告平台 | 版本 v1.0.0
