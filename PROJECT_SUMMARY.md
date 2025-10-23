# AI有声书工具 - 项目总结

## 📋 项目概览

AI有声书工具是一个完整的全栈Web应用，用于将文本小说转换为有声读物。该项目采用前后端分离架构，支持Docker容器化部署，可在局域网内使用。

### 技术栈

**前端**
- Vue 3 (Composition API)
- TypeScript
- Vite
- Element Plus
- Pinia (状态管理)
- Vue Router

**后端**
- Python 3.10+
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (数据验证)
- PyMySQL

**数据库**
- MySQL 8.0

**部署**
- Docker
- Docker Compose
- Nginx

## 🗂️ 项目结构

```
asr_story_tools/
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── projects.py    # 项目管理API
│   │   │   ├── chapters.py    # 章节管理API
│   │   │   ├── characters.py  # 角色管理API
│   │   │   ├── dialogues.py   # 对话编辑API
│   │   │   └── audio.py       # 音频处理API
│   │   ├── models/            # SQLAlchemy数据模型
│   │   │   ├── project.py
│   │   │   ├── chapter.py
│   │   │   ├── character.py
│   │   │   ├── dialogue.py
│   │   │   └── audio_export.py
│   │   ├── schemas/           # Pydantic验证模型
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── text_parser.py    # 文本解析服务
│   │   │   ├── audio_service.py  # 音频处理服务
│   │   │   ├── tts_base.py       # TTS抽象基类
│   │   │   └── tts_factory.py    # TTS工厂类
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── database.py    # 数据库连接
│   │   │   ├── exceptions.py  # 自定义异常
│   │   │   └── response.py    # 响应格式
│   │   └── utils/             # 工具函数
│   ├── migrations/            # 数据库迁移脚本
│   │   └── init.sql          # 初始化SQL
│   ├── main.py               # 应用入口
│   ├── requirements.txt      # Python依赖
│   └── Dockerfile           # Docker镜像配置
│
├── frontend/                  # Vue3前端
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   │   ├── ProjectList.vue      # 项目列表
│   │   │   ├── ProjectDetail.vue    # 项目详情
│   │   │   ├── TextImport.vue       # 文本导入
│   │   │   ├── VoiceConfig.vue      # 智能配音
│   │   │   ├── DialogueEditor.vue   # 对话编辑器
│   │   │   ├── AudioPreview.vue     # 音频预览
│   │   │   └── ExportPage.vue       # 导出页面
│   │   ├── components/       # 通用组件
│   │   │   ├── AudioPlayer.vue
│   │   │   ├── DialogueBlock.vue
│   │   │   ├── DialogueEditBlock.vue
│   │   │   ├── CharacterCard.vue
│   │   │   ├── ChapterList.vue
│   │   │   └── ProjectCard.vue
│   │   ├── api/             # API调用模块
│   │   │   ├── project.ts
│   │   │   ├── chapter.ts
│   │   │   ├── character.ts
│   │   │   ├── dialogue.ts
│   │   │   └── audio.ts
│   │   ├── stores/          # Pinia状态管理
│   │   │   ├── project.ts
│   │   │   ├── chapter.ts
│   │   │   ├── character.ts
│   │   │   ├── dialogue.ts
│   │   │   └── audio.ts
│   │   ├── router/          # 路由配置
│   │   │   └── index.ts
│   │   ├── types/           # TypeScript类型定义
│   │   │   └── index.ts
│   │   └── utils/           # 工具函数
│   │       └── http.ts      # Axios封装
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
│
├── storage/                  # 文件存储目录
│   ├── uploads/             # 上传的文本文件
│   ├── audio/               # 生成的音频文件
│   └── temp/                # 临时文件
│
├── docker-compose.yml       # Docker Compose配置
├── env.example             # 环境变量模板
├── deploy.sh               # 一键部署脚本
├── DEPLOYMENT.md           # 部署指南
└── PROJECT_SUMMARY.md      # 本文件
```

## 🎯 核心功能

### 1. 项目管理
- ✅ 创建、编辑、删除项目
- ✅ 项目列表展示（卡片式）
- ✅ 项目详情页面
- ✅ 项目统计数据

### 2. 文本导入
- ✅ 支持TXT文件上传
- ✅ 智能章节识别（基于正则表达式）
- ✅ 章节内容预览和编辑
- ✅ 批量上传处理

### 3. 角色管理
- ✅ AI自动识别角色（基于对话标记）
- ✅ 角色声音配置
- ✅ TTS引擎选择（Azure/阿里云/腾讯云等）
- ✅ 角色统计信息

### 4. 对话编辑
- ✅ 章节对话列表
- ✅ 对话类型管理（对话/旁白）
- ✅ 对话内容编辑
- ✅ 语音参数调整（语速、音调、音量）
- ✅ 对话排序和删除

### 5. 音频生成
- ✅ 单段音频生成
- ✅ 批量音频生成
- ✅ TTS服务抽象层（支持多引擎）
- ✅ 音频状态追踪

### 6. 音频预览
- ✅ 波形可视化
- ✅ 音频播放器
- ✅ 段落导航
- ✅ 播放速度控制
- ✅ 音频属性查看

### 7. 导出功能
- ✅ 多格式支持（MP3/WAV/M4A/OGG）
- ✅ 音质选择（标准/高/超高）
- ✅ 章节范围选择
- ✅ 合并导出选项
- ✅ 导出历史记录

### 8. 系统设置
- ✅ TTS引擎配置
- ✅ 音频参数设置
- ✅ 文件存储管理

## 📊 数据库设计

### 核心表

**projects** - 项目表
- id, name, description, cover_image
- status, chapters_count, characters_count, total_duration
- created_at, updated_at

**chapters** - 章节表
- id, project_id, title, order_index
- content, word_count, status, duration

**characters** - 角色表
- id, project_id, name, avatar, description
- dialogue_count, total_duration, voice_config (JSON)

**dialogues** - 对话/旁白表
- id, chapter_id, order_index, type
- content, character_id, start_time, end_time
- audio_path, status, voice_config (JSON), pause_after

**audio_exports** - 导出记录表
- id, project_id, format, quality
- file_path, file_size, export_range (JSON)

## 🔌 API接口

### 项目管理
- `POST /api/projects` - 创建项目
- `GET /api/projects` - 项目列表
- `GET /api/projects/{id}` - 项目详情
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

### 章节管理
- `GET /api/chapters?project_id={id}` - 章节列表
- `GET /api/chapters/{id}` - 章节详情
- `POST /api/chapters/upload` - 上传章节文件
- `PUT /api/chapters/{id}` - 更新章节
- `DELETE /api/chapters/{id}` - 删除章节

### 角色管理
- `GET /api/characters?project_id={id}` - 角色列表
- `GET /api/characters/{id}` - 角色详情
- `POST /api/characters/extract` - 提取角色
- `POST /api/characters` - 创建角色
- `PUT /api/characters/{id}` - 更新角色
- `DELETE /api/characters/{id}` - 删除角色

### 对话编辑
- `GET /api/dialogues?chapter_id={id}` - 对话列表
- `GET /api/dialogues/{id}` - 对话详情
- `POST /api/dialogues` - 创建对话
- `PUT /api/dialogues/{id}` - 更新对话
- `DELETE /api/dialogues/{id}` - 删除对话
- `POST /api/dialogues/parse` - 解析章节对话

### 音频处理
- `POST /api/audio/generate` - 生成单段音频
- `POST /api/audio/batch-generate` - 批量生成
- `POST /api/audio/export` - 导出音频
- `GET /api/audio/exports?project_id={id}` - 导出历史

## 🚀 部署说明

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ 内存
- 10GB+ 磁盘空间

### 快速部署

```bash
# 1. 克隆项目
cd asr_story_tools

# 2. 运行部署脚本
./deploy.sh
```

### 访问地址
- **前端**: http://localhost:80
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

详细部署说明请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🎨 前端页面

### 页面列表

1. **ProjectList** (/)
   - 项目卡片网格展示
   - 创建新项目
   - 项目搜索和筛选

2. **ProjectDetail** (/projects/:id)
   - 项目信息展示
   - 统计卡片
   - 章节列表
   - 快捷操作

3. **TextImport** (/projects/:id/import)
   - 文件拖拽上传
   - 文本粘贴导入
   - 章节预览
   - 章节识别配置

4. **VoiceConfig** (/projects/:id/voice-config)
   - 角色列表
   - 声音配置
   - TTS引擎选择
   - 试听功能

5. **DialogueEditor** (/projects/:id/editor)
   - 三栏布局
   - 章节切换
   - 对话编辑
   - 属性面板

6. **AudioPreview** (/projects/:id/audio-preview/:chapterId)
   - 波形可视化
   - 音频播放器
   - 段落列表
   - 属性检查器

7. **ExportPage** (/projects/:id/export)
   - 导出设置
   - 格式选择
   - 音质配置
   - 导出历史

## 🔧 开发指南

### 后端开发

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python main.py
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

### API文档

FastAPI自动生成的交互式API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 待实现功能

### 短期计划
- [ ] 完善音频播放器组件（波形显示）
- [ ] 实现真实的TTS引擎对接
- [ ] 添加音频编辑功能（剪辑、调整）
- [ ] 批量操作优化（进度条、取消）

### 中期计划
- [ ] 用户认证和权限管理
- [ ] 项目分享和协作
- [ ] 模板市场
- [ ] 项目统计分析

### 长期计划
- [ ] AI声音克隆
- [ ] 多语言支持
- [ ] 移动端适配
- [ ] 云端TTS集成

## 🐛 已知问题

1. **音频播放器**: 
   - 波形显示为模拟数据，需要实现真实音频解析
   - 播放进度同步需要优化

2. **批量生成**:
   - 需要添加任务队列和进度追踪
   - 异步处理机制待完善

3. **文件管理**:
   - 需要添加文件清理机制
   - 存储空间监控

## 📈 性能优化建议

1. **数据库优化**
   - 添加适当的索引
   - 实现查询缓存
   - 数据分页优化

2. **音频处理**
   - 使用任务队列（Celery/RQ）
   - 音频流式传输
   - CDN加速

3. **前端优化**
   - 组件懒加载
   - 虚拟滚动（长列表）
   - 音频文件缓存

## 🔒 安全建议

1. **生产环境**
   - 修改所有默认密码
   - 启用HTTPS
   - 配置防火墙
   - 限制API访问速率

2. **数据安全**
   - 定期备份数据库
   - 文件加密存储
   - 访问日志记录

## 📄 许可证

本项目仅供学习和内部使用。

## 👥 贡献

如需贡献代码或报告问题，请联系项目维护者。

---

**版本**: v1.0.0  
**创建日期**: 2025-10-23  
**最后更新**: 2025-10-23

