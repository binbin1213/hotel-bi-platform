# 🏨 酒店业BI报告平台 | Hotel BI Platform

![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

一个自动化、智能化、可视化的酒店业务智能分析平台，帮助酒店从业者从重复性的报告工作中解放出来，专注于数据背后的洞察和业务决策。

## 📸 项目截图

> *这里将放置项目截图*

## ✨ 核心功能

- 📊 **数据上传与管理** - 提供简洁的Web界面，支持拖拽上传标准格式的Excel数据文件
- 📈 **KPI自动计算** - 自动处理数据，计算核心经营指标（OCC, ADR, RevPAR等）
- 🧠 **AI智能分析** - 对接DeepSeek等大语言模型，自动生成对当周业绩的分析、洞察和建议
- 📄 **双格式报告生成** - 自动生成PDF(高保真)和PPT(可编辑)两种格式的专业报告
- 📱 **历史数据仪表盘** - 提供交互式仪表盘，查看并对比历史各周期的经营数据和KPI趋势
- 👥 **用户权限管理** - 支持多用户及不同权限级别的管理

## 🏗️ 系统架构

```
                    ┌─────────────────┐
                    │   Nginx/API网关  │
                    └─────────────────┘
                            │
                    ┌───────────────────┐
                    │    单体应用服务    │ ← 阶段1: 单体架构
                    │  (FastAPI + Vue)  │
                    └───────────────────┘
                            │
                    ┌───────┼───────┐
                    │       │       │
            ┌───────────┐ ┌─────────┐ ┌──────────────┐
            │   Redis   │ │ Celery  │ │ PostgreSQL   │
            │  (缓存)   │ │ Worker  │ │   (数据库)   │
            └───────────┘ └─────────┘ └──────────────┘
                                            │
                                      ┌──────────────┐
                                      │ MinIO/S3     │
                                      │ (文件存储)   │
                                      └──────────────┘
```

## 🛠️ 技术栈

### 后端

- **语言/框架**: Python 3.11+ / FastAPI
- **数据处理**: Pandas
- **数据库**: PostgreSQL 15+ / SQLAlchemy (ORM)
- **缓存与任务队列**: Redis + Celery
- **PDF生成**: Playwright (通过驱动无头浏览器渲染HTML)
- **PPT生成**: python-pptx
- **HTML模板**: Jinja2
- **AI调用**: httpx
- **文件存储**: MinIO/S3

### 前端

- **框架**: Vue 3 (使用 Vite 构建)
- **类型系统**: TypeScript
- **UI组件库**: Element Plus
- **数据可视化**: Apache ECharts
- **API通信**: Axios

### 部署

- **容器化**: Docker / Docker Compose

## 🚀 快速开始

### 前提条件

- Docker & Docker Compose
- Node.js (v16+) (仅开发环境需要)
- Python 3.11+ (仅开发环境需要)

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/binbin1213/hotel-bi-platform.git
cd hotel-bi-platform
```

2. 使用Docker Compose启动所有服务
```bash
docker-compose up -d
```

3. 访问应用
```
前端: http://localhost:8080
API文档: http://localhost:8000/docs
```

### 开发环境设置

1. 安装后端依赖
```bash
pip install -r requirements.txt
```

2. 安装前端依赖
```bash
cd frontend
npm install
```

3. 启动开发服务器
```bash
# 后端
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

## 📁 项目结构

```
hotel-bi-platform/
├── app/                        # 后端应用
│   ├── main.py                 # FastAPI应用入口
│   ├── config/                 # 配置管理
│   ├── models/                 # 数据模型
│   ├── schemas/                # Pydantic模式
│   ├── services/               # 业务服务层
│   ├── api/                    # API路由层
│   ├── tasks/                  # 异步任务
│   └── utils/                  # 工具函数
├── docker/                     # Docker配置
│   ├── docker-compose.yml      # 开发环境配置
│   ├── docker-compose.prod.yml # 生产环境配置
│   └── nginx/                  # Nginx配置
├── frontend/                   # 前端应用
│   ├── src/                    # 前端源码
│   │   ├── main.js             # 入口文件
│   │   ├── App.vue             # 根组件
│   │   ├── router/             # 路由配置
│   │   ├── views/              # 页面组件
│   │   ├── components/         # 通用组件
│   │   ├── stores/             # 状态管理
│   │   ├── services/           # API服务
│   │   └── utils/              # 工具函数
│   ├── package.json            # 依赖配置
│   └── vite.config.js          # Vite配置
├── migrations/                 # 数据库迁移脚本
├── scripts/                    # 部署和维护脚本
├── docs/                       # 项目文档
│   ├── api/                    # API文档
│   ├── user-guide/             # 用户指南
│   └── development/            # 开发文档
├── tests/                      # 测试文件
├── .gitignore                  # Git忽略配置
├── requirements.txt            # Python依赖
├── alembic.ini                 # Alembic配置
├── LICENSE                     # 许可证文件
├── CONTRIBUTING.md             # 贡献指南
└── README.md                   # 项目说明
```

## 🖥️ 核心工作流程

1. **上传数据**: 用户在前端界面上传Excel文件
2. **处理与入库**: 
   - 后端API接收文件
   - Pandas服务读取文件，进行数据清洗、校验，并计算所有KPI
   - SQLAlchemy服务将数据存入PostgreSQL数据库
3. **AI分析**:
   - 后端触发AI分析服务
   - 构建结构化的Prompt
   - 调用DeepSeek API，获取分析文本
4. **双格式报告生成**:
   - **PDF生成器**: 使用Jinja2填充HTML模板，Playwright渲染并生成PDF
   - **PPT生成器**: 使用python-pptx基于模板生成可编辑的PPT
5. **下载与展示**:
   - 前端提供两种格式报告的下载
   - 仪表盘页面通过ECharts动态展示历史趋势

## 🔐 登录信息

开发环境下可使用以下账号登录：

- 用户名：admin
- 密码：admin

## 📊 数据可视化

基于Apache ECharts实现，主要图表类型：
- 折线图：展示入住率等时间序列数据
- 柱状图：展示收入等指标
- 数据卡片：展示关键业绩指标(KPI)

## 🧠 AI分析功能

系统集成了多种AI供应商的API：
- **DeepSeek** (主要)
- **OpenAI** (备用)
- **Claude** (高质量)

AI分析服务通过智能路由调度器进行负载均衡、故障转移和成本优化。

## 🔜 项目实施路线图

- **第一阶段**: 核心后端与数据处理 (约2-3周)
- **第二阶段**: 基础报告生成与前端MVP (约3-4周)
- **第三阶段**: 集成AI分析与仪表盘 (约2-3周)
- **第四阶段**: 优化与扩展 (持续进行)

## 📄 许可证与使用限制

[CC BY-NC 4.0](LICENSE) - 创作共用署名-非商业性 4.0 国际许可证

### 重要说明

本项目仅供个人学习和非商业性使用：

- ✅ **允许**: 个人学习、研究、教育目的使用
- ✅ **允许**: 在非商业环境中部署和使用
- ✅ **允许**: 修改代码并分享这些修改（需遵循相同许可条款）

- ❌ **禁止**: 将本项目或其衍生作品用于商业目的
- ❌ **禁止**: 销售本项目或基于本项目开发的产品/服务
- ❌ **禁止**: 在未经授权的情况下将本项目用于盈利活动

如需商业使用，请联系项目维护者获取专门授权。

## 👥 贡献指南

欢迎贡献代码、报告问题或提出新功能建议！请查看[贡献指南](CONTRIBUTING.md)了解更多信息。

---

© 2025 酒店业BI报告平台 | 版本 v1.0.0 

联系方式: piaozhitian@gmail.com 