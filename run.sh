#!/bin/bash

echo "=========================================="
echo "      自动发卡系统启动脚本 (Linux)"
echo "=========================================="

# 1. 检查 Python 是否安装
if ! command -v python3 &> /dev/null
then
    echo "❌ 错误: 未找到 python3"
    echo "   请先安装 Python 3.8 或以上版本:"
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    echo "   CentOS: sudo yum install python3 python3-pip"
    exit 1
fi

echo "[1/3] 正在检查依赖库..."
# 使用清华源加速下载
python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo ""
echo "[2/3] 正在启动服务器..."
echo "   提示: 如果想要后台运行，请使用 'nohup ./run.sh &'"
echo "   程序将运行在: http://0.0.0.0:8000"
echo ""

# 启动 uvicorn
# --host 0.0.0.0 允许外部IP访问
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
