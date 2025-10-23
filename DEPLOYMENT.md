# AI有声书工具 - 部署指南

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 一键部署

```bash
# 1. 克隆或下载项目
cd asr_story_tools

# 2. 运行部署脚本
./deploy.sh
```

部署脚本会自动完成：
- ✅ 检查系统依赖
- ✅ 创建环境配置文件
- ✅ 创建必要的目录
- ✅ 构建Docker镜像
- ✅ 启动所有服务
- ✅ 等待服务就绪
- ✅ 显示访问地址

### 手动部署

如果需要手动控制部署过程：

```bash
# 1. 复制环境配置
cp env.example .env

# 2. 编辑配置文件（可选）
nano .env

# 3. 创建存储目录
mkdir -p storage/{uploads,audio,temp}

# 4. 构建并启动服务
docker-compose up -d --build

# 5. 查看服务状态
docker-compose ps

# 6. 查看日志
docker-compose logs -f
```

## 配置说明

### 环境变量

编辑 `.env` 文件配置以下参数：

#### 数据库配置
```env
MYSQL_ROOT_PASSWORD=asr_story_2025
MYSQL_DATABASE=asr_story
MYSQL_USER=asr_user
MYSQL_PASSWORD=asr_pass_2025
MYSQL_PORT=3306
```

#### 后端配置
```env
BACKEND_PORT=8000
APP_ENV=production
DEBUG=false
SECRET_KEY=your-random-secret-key
```

#### 前端配置
```env
FRONTEND_PORT=80
VITE_API_BASE_URL=http://localhost:8000
```

#### TTS引擎配置

根据使用的TTS服务商配置相应参数：

**Azure TTS**
```env
TTS_ENGINE=azure
AZURE_TTS_KEY=your-azure-speech-key
AZURE_TTS_REGION=eastasia
```

**阿里云TTS**
```env
TTS_ENGINE=aliyun
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_APP_KEY=your-app-key
```

## 服务访问

部署成功后，可以通过以下地址访问：

### 本地访问
- **前端界面**: http://localhost:80
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 局域网访问

找到本机IP地址（例如 192.168.1.100）：
- **前端界面**: http://192.168.1.100:80
- **后端API**: http://192.168.1.100:8000

在 `.env` 中配置 `ALLOWED_ORIGINS` 以允许跨域访问：
```env
ALLOWED_ORIGINS=http://localhost,http://192.168.1.100
```

## 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

### 数据管理

```bash
# 进入MySQL容器
docker-compose exec mysql mysql -u root -p

# 备份数据库
docker-compose exec mysql mysqldump -u root -p asr_story > backup.sql

# 恢复数据库
docker-compose exec -T mysql mysql -u root -p asr_story < backup.sql

# 清理数据卷（警告：会删除所有数据）
docker-compose down -v
```

### 开发模式

如果需要开发调试：

```bash
# 修改 docker-compose.yml 中的 volumes 配置以启用代码热重载

# 后端开发模式
docker-compose up backend

# 前端开发模式（需要单独启动）
cd frontend
npm install
npm run dev
```

## 生产环境部署

### 使用Nginx反向代理

1. 修改 `.env` 启用Nginx：
```env
NGINX_PORT=8080
```

2. 创建Nginx配置文件 `nginx/conf.d/default.conf`

3. 使用production profile启动：
```bash
docker-compose --profile production up -d
```

### 安全建议

1. **修改默认密码**
   - 更改 `MYSQL_ROOT_PASSWORD`
   - 更改 `MYSQL_PASSWORD`
   - 生成随机的 `SECRET_KEY`

2. **启用HTTPS**
   - 使用Let's Encrypt获取SSL证书
   - 配置Nginx SSL

3. **限制访问**
   - 配置防火墙规则
   - 仅开放必要端口（80/443）

4. **备份策略**
   - 定期备份MySQL数据
   - 备份storage目录

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose logs

# 检查端口占用
netstat -tuln | grep 8000
netstat -tuln | grep 80

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 数据库连接失败

```bash
# 检查MySQL服务
docker-compose ps mysql

# 查看MySQL日志
docker-compose logs mysql

# 测试连接
docker-compose exec backend python -c "from app.core.database import engine; print(engine)"
```

### 前端无法访问后端

1. 检查 `VITE_API_BASE_URL` 配置
2. 检查 `ALLOWED_ORIGINS` 是否包含前端地址
3. 查看浏览器控制台CORS错误

## 性能优化

### 数据库优化

编辑 `docker-compose.yml` 添加MySQL配置：
```yaml
mysql:
  command:
    - --max_connections=200
    - --innodb_buffer_pool_size=1G
```

### 资源限制

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

## 更新升级

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose down
docker-compose build
docker-compose up -d
```

## 技术支持

如遇到问题，请检查：
1. Docker和Docker Compose版本
2. 系统资源（内存、磁盘）
3. 日志文件
4. 网络连接

---

**版本**: v1.0.0  
**更新日期**: 2025-10-23

