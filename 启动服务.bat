@echo off
chcp 65001 >nul
REM ===========================================
REM 产业避险参谋 - 启动脚本（Windows版）
REM ===========================================

echo 🚀 正在启动产业避险参谋服务...
echo.

REM 进入项目目录
cd /d %~dp0

REM 检查 .env 文件
if not exist .env (
    echo ⚠️  警告：未找到 .env 文件
    echo 📝 正在创建默认配置...
    (
        echo # 基础配置
        echo PORT=5000
        echo DEBUG=true
        echo LOG_LEVEL=INFO
        echo.
        echo # AI配置（系统会自动使用环境变量）
        echo COZE_WORKLOAD_IDENTITY_API_KEY=请填入您的API_Key
        echo COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn
    ) > .env
    echo ✅ 已创建 .env 文件
    echo.
)

REM 启动服务
echo 🌐 启动服务中...
echo 📍 访问地址：
echo    - 主页：http://localhost:5000
echo    - 实时版：http://localhost:5000/static/realtime_index.html
echo    - API文档：http://localhost:5000/docs
echo.
echo 💡 按 Ctrl+C 停止服务
echo.

python src\main.py
