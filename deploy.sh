#!/bin/bash

# UFO Galaxy 部署脚本
# 用途: 自动化部署 UFO Galaxy 应用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
APP_NAME="ufo-galaxy"
APP_DIR="/opt/ufo-galaxy"
REPO_URL="https://github.com/DannyFish-11/ufo-galaxy-realization.git"
BRANCH="main"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 克隆或更新代码
clone_or_update_code() {
    log_info "步骤1: 克隆/更新代码..."

    if [ -d "$APP_DIR/.git" ]; then
        log_info "检测到已存在的代码目录，执行更新..."
        cd "$APP_DIR"
        git fetch origin
        git reset --hard origin/$BRANCH
        git pull origin $BRANCH
    else
        log_info "首次部署，克隆代码..."
        sudo mkdir -p "$APP_DIR"
        sudo git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
        cd "$APP_DIR"
    fi

    log_info "代码更新完成"
}

# 安装依赖
install_dependencies() {
    log_info "步骤2: 安装依赖..."

    # 检查并安装 Docker
    if ! command -v docker &> /dev/null; then
        log_info "安装 Docker..."
        curl -fsSL https://get.docker.com | sh
        sudo usermod -aG docker $USER
        log_warn "Docker 已安装，请重新登录以应用组权限"
    fi

    # 检查并安装 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_info "安装 Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi

    # 检查并安装 Node.js (如果需要)
    if ! command -v node &> /dev/null; then
        log_info "安装 Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi

    log_info "依赖安装完成"
}

# 配置环境变量
configure_environment() {
    log_info "步骤3: 配置环境变量..."

    # 创建 .env 文件（如果不存在）
    if [ ! -f "$APP_DIR/.env" ]; then
        log_info "创建 .env 文件..."
        cat > "$APP_DIR/.env" << EOF
# UFO Galaxy 环境配置
NODE_ENV=production
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ufo_galaxy
DB_USER=ufo_user
DB_PASSWORD=your_secure_password_here
JWT_SECRET=$(openssl rand -hex 32)
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=info
EOF
        log_warn "请编辑 $APP_DIR/.env 文件，设置正确的配置值"
    else
        log_info ".env 文件已存在，跳过创建"
    fi

    log_info "环境配置完成"
}

# 启动 Docker 服务
start_docker_services() {
    log_info "步骤4: 启动 Docker 服务..."

    cd "$APP_DIR"

    # 检查 docker-compose.yml 是否存在
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        log_info "启动 Docker Compose 服务..."
        docker-compose down 2>/dev/null || true
        docker-compose pull
        docker-compose up -d --build

        # 等待服务启动
        log_info "等待服务启动..."
        sleep 10

        # 检查服务状态
        if docker-compose ps | grep -q "Up"; then
            log_info "Docker 服务启动成功"
        else
            log_error "Docker 服务启动失败，请检查日志"
            docker-compose logs
            exit 1
        fi
    else
        log_warn "未找到 docker-compose.yml 文件，跳过 Docker 启动"
    fi

    log_info "Docker 服务处理完成"
}

# 设置 systemd 服务
setup_systemd_service() {
    log_info "步骤5: 设置 systemd 服务..."

    SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

    # 创建 systemd 服务文件
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=UFO Galaxy Application
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose -f $APP_DIR/$DOCKER_COMPOSE_FILE up
ExecStop=/usr/local/bin/docker-compose -f $APP_DIR/$DOCKER_COMPOSE_FILE down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载 systemd
    sudo systemctl daemon-reload

    # 启用服务
    sudo systemctl enable "${APP_NAME}.service"

    log_info "systemd 服务设置完成"
}

# 启动 UFO Galaxy
start_ufo_galaxy() {
    log_info "步骤6: 启动 UFO Galaxy..."

    # 启动 systemd 服务
    sudo systemctl start "${APP_NAME}.service"

    # 检查服务状态
    sleep 5
    if sudo systemctl is-active --quiet "${APP_NAME}.service"; then
        log_info "UFO Galaxy 启动成功！"
        log_info "服务状态:"
        sudo systemctl status "${APP_NAME}.service" --no-pager
    else
        log_error "UFO Galaxy 启动失败"
        sudo systemctl status "${APP_NAME}.service" --no-pager
        exit 1
    fi

    log_info "部署完成！"
}

# 显示帮助信息
show_help() {
    echo "UFO Galaxy 部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  -u, --update    仅更新代码"
    echo "  -r, --restart   重启服务"
    echo "  -s, --status    查看服务状态"
    echo "  -l, --logs      查看服务日志"
    echo "  -d, --delete    停止并删除服务"
    echo ""
    echo "示例:"
    echo "  $0              完整部署"
    echo "  $0 -u           仅更新代码"
    echo "  $0 -r           重启服务"
}

# 仅更新代码
update_only() {
    log_info "仅更新代码..."
    clone_or_update_code
    cd "$APP_DIR"
    docker-compose up -d --build
    log_info "代码更新完成"
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    sudo systemctl restart "${APP_NAME}.service"
    log_info "服务已重启"
}

# 查看状态
show_status() {
    log_info "服务状态:"
    sudo systemctl status "${APP_NAME}.service" --no-pager
    echo ""
    log_info "Docker 容器状态:"
    cd "$APP_DIR" && docker-compose ps
}

# 查看日志
show_logs() {
    log_info "服务日志:"
    sudo journalctl -u "${APP_NAME}.service" -f
}

# 删除服务
delete_service() {
    log_warn "停止并删除服务..."
    sudo systemctl stop "${APP_NAME}.service" 2>/dev/null || true
    sudo systemctl disable "${APP_NAME}.service" 2>/dev/null || true
    sudo rm -f "/etc/systemd/system/${APP_NAME}.service"
    cd "$APP_DIR" && docker-compose down 2>/dev/null || true
    log_info "服务已删除"
}

# 主函数
main() {
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--update)
            update_only
            exit 0
            ;;
        -r|--restart)
            restart_service
            exit 0
            ;;
        -s|--status)
            show_status
            exit 0
            ;;
        -l|--logs)
            show_logs
            exit 0
            ;;
        -d|--delete)
            delete_service
            exit 0
            ;;
        "")
            # 完整部署流程
            log_info "开始部署 UFO Galaxy..."
            check_command git
            clone_or_update_code
            install_dependencies
            configure_environment
            start_docker_services
            setup_systemd_service
            start_ufo_galaxy
            log_info "=========================================="
            log_info "UFO Galaxy 部署成功！"
            log_info "=========================================="
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
