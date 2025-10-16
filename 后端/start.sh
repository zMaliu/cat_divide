#!/bin/bash
# 启动脚本 - 自动清理并运行服务器

echo "=========================================="
echo "正在准备启动服务器..."
echo "=========================================="

# 清理 macOS 扩展属性（防止 null bytes 错误）
echo "1. 清理 macOS 扩展属性..."
# 使用 xargs 方法更可靠
find . -name "*.py" -print0 | xargs -0 xattr -c 2>/dev/null
# 额外清理顽固的特定属性
find . -name "*.py" -print0 | xargs -0 -I {} sh -c 'xattr -d com.apple.macl "{}" 2>/dev/null; xattr -d com.apple.provenance "{}" 2>/dev/null; xattr -d com.apple.quarantine "{}" 2>/dev/null' 2>/dev/null
echo "   ✓ 扩展属性已清理"

# 清理 Python 缓存文件
echo "2. 清理 Python 缓存..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "   ✓ 缓存文件已清理"

# 激活 conda 环境
echo "3. 激活 yolov8 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate yolov8
echo "   ✓ 环境已激活: $(which python)"

# 显示 Python 版本
echo "4. Python 版本: $(python --version)"

echo "=========================================="
echo "启动服务器..."
echo "=========================================="

# 运行主程序（禁用字节码生成）
python -B main.py

