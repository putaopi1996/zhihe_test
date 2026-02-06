@echo off
chcp 65001 >nul
echo ==========================================
echo       自动发卡系统启动脚本
echo ==========================================
echo.

REM 先关闭之前可能运行的服务器
echo [0/2] 正在关闭之前的服务器实例...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo      已关闭旧的服务器进程
) else (
    echo      没有发现正在运行的服务器
)
echo.

echo [1/2] 正在检查并安装依赖库...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q
echo      依赖检查完成！
echo.

echo [2/2] 正在启动服务器...
echo ==========================================
echo   服务器运行中，以下是实时日志：
echo   访问地址: http://localhost:8000
echo   关闭此窗口将自动停止服务器
echo ==========================================
echo.

REM 直接运行 python，不用 start，这样关闭窗口会自动结束进程
python main.py
