#!/bin/bash

# ==========================================
# AI有声书工具 - 一键部署脚本
# ==========================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    print_info "✓ 系统依赖检查通过"
}

# 检查环境变量文件
check_env_file() {
    if [ ! -f .env ]; then
        print_warn ".env文件不存在，正在从模板创建..."
        cp env.example .env
        print_info "✓ 已创建.env文件，请根据需要修改配置"
        print_warn "请编辑 .env 文件并配置必要的参数，然后重新运行此脚本"
        exit 0
    fi
    print_info "✓ 环境配置文件存在"
}

# 创建必要的目录
create_directories() {
    print_info "创建存储目录..."
    mkdir -p storage/uploads
    mkdir -p storage/audio
    mkdir -p storage/temp
    mkdir -p data/mysql
    mkdir -p nginx/conf.d
    print_info "✓ 目录创建完成"
}

# 构建镜像
build_images() {
    print_info "构建Docker镜像..."
    docker-compose build --no-cache
    print_info "✓ 镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."
    docker-compose up -d
    print_info "✓ 服务启动完成"
}

# 等待服务健康
wait_for_health() {
    print_info "等待服务就绪..."
    
    # 等待MySQL
    print_info "等待MySQL就绪..."
    for i in {1..30}; do
        if docker-compose exec -T mysql mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD:-asr_story_2025} &> /dev/null; then
            print_info "✓ MySQL已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "MySQL启动超时"
            exit 1
        fi
        sleep 2
    done
    
    # 等待后端
    print_info "等待后端服务就绪..."
    for i in {1..30}; do
        if curl -f http://localhost:${BACKEND_PORT:-8000}/health &> /dev/null; then
            print_info "✓ 后端服务已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "后端服务启动超时"
            exit 1
        fi
        sleep 2
    done
    
    # 等待前端
    print_info "等待前端服务就绪..."
    for i in {1..30}; do
        if curl -f http://localhost:${FRONTEND_PORT:-80} &> /dev/null; then
            print_info "✓ 前端服务已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "前端服务启动超时"
            exit 1
        fi
        sleep 2
    done
}

# 显示服务状态
show_status() {
    print_info "服务状态："
    docker-compose ps
}

# 显示访问信息
show_access_info() {
    echo ""
    print_info "========================================="
    print_info "🎉 部署完成！"
    print_info "========================================="
    echo ""
    print_info "访问地址："
    print_info "  前端: http://localhost:${FRONTEND_PORT:-80}"
    print_info "  后端: http://localhost:${BACKEND_PORT:-8000}"
    print_info "  API文档: http://localhost:${BACKEND_PORT:-8000}/docs"
    echo ""
    print_info "局域网访问："
    LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
    if [ -n "$LOCAL_IP" ]; then
        print_info "  前端: http://${LOCAL_IP}:${FRONTEND_PORT:-80}"
        print_info "  后端: http://${LOCAL_IP}:${BACKEND_PORT:-8000}"
    fi
    echo ""
    print_info "常用命令："
    print_info "  查看日志: docker-compose logs -f"
    print_info "  停止服务: docker-compose down"
    print_info "  重启服务: docker-compose restart"
    print_info "  查看状态: docker-compose ps"
    echo ""
    print_info "========================================="
}

# 主函数
main() {
    echo ""
    print_info "========================================="
    print_info "AI有声书工具 - 部署脚本"
    print_info "========================================="
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 检查环境变量
    check_env_file
    
    # 创建目录
    create_directories
    
    # 询问是否重新构建
    read -p "是否重新构建镜像？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_images
    fi
    
    # 启动服务
    start_services
    
    # 等待服务健康
    wait_for_health
    
    # 显示状态
    show_status
    
    # 显示访问信息
    show_access_info
}

# 运行主函数
main

