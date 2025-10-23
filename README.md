# AI有声书工具

> 将文本小说转换为有声读物的全栈Web应用

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Vue](https://img.shields.io/badge/vue-3.x-brightgreen)
![FastAPI](https://img.shields.io/badge/fastapi-latest-009688)
![MySQL](https://img.shields.io/badge/mysql-8.0-orange)

## ✨ 特性

- 📚 **智能文本导入** - 支持TXT文件，自动识别章节
- 🎭 **角色自动识别** - AI识别对话中的角色
- 🎵 **多TTS引擎支持** - 支持Azure、阿里云、腾讯云等
- 🎨 **可视化编辑器** - 直观的对话编辑界面
- 🎧 **音频预览** - 波形可视化，实时试听
- 💾 **灵活导出** - 多格式、多音质选择
- 🐳 **容器化部署** - 一键Docker部署
- 🌐 **局域网访问** - 支持团队协作

## 🚀 快速开始

### 方式一：Docker部署（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd asr_story_tools

# 一键部署
./deploy.sh

# 访问应用
# 前端: http://localhost:80
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：本地开发

**后端**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**前端**
```bash
cd frontend
npm install
npm run dev
```

## 📖 文档

- [项目总结](./PROJECT_SUMMARY.md) - 完整的项目介绍和架构说明
- [部署指南](./DEPLOYMENT.md) - 详细的部署步骤和配置说明

## 🏗️ 技术栈

### 前端
- Vue 3 + TypeScript
- Element Plus
- Pinia
- Vite

### 后端
- FastAPI
- SQLAlchemy
- Pydantic
- PyMySQL

### 数据库
- MySQL 8.0

### 部署
- Docker + Docker Compose
- Nginx

## 📸 功能预览

### 项目列表
展示所有项目，支持创建、搜索和管理

### 文本导入
拖拽上传TXT文件，自动识别章节结构

### 智能配音
AI识别角色，配置专属声音

### 对话编辑
可视化编辑每一段对话，调整语音参数

### 音频预览
波形显示，实时播放，精确定位

### 导出功能
多格式导出，灵活配置

## 🔧 配置

### 环境变量

复制 `env.example` 为 `.env` 并配置：

```env
# 数据库配置
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=asr_story
MYSQL_USER=asr_user
MYSQL_PASSWORD=user_password

# TTS引擎配置（可选）
TTS_ENGINE=azure
AZURE_TTS_KEY=your_key
AZURE_TTS_REGION=eastasia
```

详细配置说明请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 📊 项目结构

```
asr_story_tools/
├── backend/          # FastAPI后端
│   ├── app/
│   │   ├── api/      # API路由
│   │   ├── models/   # 数据模型
│   │   ├── schemas/  # 验证模型
│   │   └── services/ # 业务逻辑
│   └── main.py       # 入口文件
├── frontend/         # Vue3前端
│   ├── src/
│   │   ├── views/    # 页面组件
│   │   ├── components/ # 通用组件
│   │   ├── api/      # API调用
│   │   └── stores/   # 状态管理
│   └── vite.config.ts
├── storage/          # 文件存储
└── docker-compose.yml
```

## 🎯 核心功能

### 已实现

- ✅ 项目管理（CRUD）
- ✅ 文本导入和章节识别
- ✅ 角色识别和配置
- ✅ 对话编辑器
- ✅ 音频预览
- ✅ 多格式导出
- ✅ Docker部署

### 待开发

- [ ] 真实TTS引擎对接
- [ ] 音频编辑功能
- [ ] 用户认证系统
- [ ] 项目分享协作
- [ ] 移动端适配

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📝 许可证

本项目仅供学习和内部使用。

## 📧 联系方式

如有问题或建议，请联系项目维护者。

---

**开发日期**: 2025-10-23  
**版本**: v1.0.0  
**状态**: 生产就绪

