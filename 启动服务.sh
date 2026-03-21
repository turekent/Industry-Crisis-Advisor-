#!/bin/bash

# ===========================================
# 产业避险参谋 - 启动脚本
# ===========================================

echo "🚀 正在启动产业避险参谋服务..."
echo ""

# 进入项目目录
cd /workspace/projects

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告：未找到 .env 文件"
    echo "📝 正在创建默认配置..."
    cat > .env << 'EOF'
# 基础配置
PORT=5000
DEBUG=true
LOG_LEVEL=INFO

# AI配置（系统会自动使用环境变量）
COZE_WORKLOAD_IDENTITY_API_KEY=请填入您的API_Key
COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn
EOF
    echo "✅ 已创建 .env 文件"
    echo ""
fi

# 启动服务
echo "🌐 启动服务中..."
echo "📍 访问地址："
echo "   - 主页：http://localhost:5000"
echo "   - 实时版：http://localhost:5000/static/realtime_index.html"
echo "   - API文档：http://localhost:5000/docs"
echo ""
echo "💡 按 Ctrl+C 停止服务"
echo ""

python src/main.py
