@echo off
chcp 65001
echo ==========================================
echo       自动发卡系统启动脚本
echo ==========================================

echo [1/2] 正在检查并安装依赖库...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [2/2] 正在启动服务器...
echo 请保持此窗口打开。
echo 如果看到 "Application startup complete"，请在浏览器打开 http://localhost:8000
echo.

python main.py

pause
