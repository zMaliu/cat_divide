@echo off
chdir /d "%~dp0"
echo 正在启动 Milvus...
docker compose -p catdivide-milvus up -d
if %errorlevel% neq 0 (
    echo 请确认已安装并启动 Docker。
    pause
    exit /b 1
)
echo Milvus 已后台启动。请稍等约 1 分钟后运行 main.py。
pause
