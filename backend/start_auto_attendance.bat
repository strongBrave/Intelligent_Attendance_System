@echo off
echo ========================================
echo 微信小程序考勤系统 - 自动考勤服务
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

:: 检查是否在正确目录
if not exist "auto_attendance.py" (
    echo 错误: 请在backend目录下运行此脚本
    pause
    exit /b 1
)

:: 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

:: 检查schedule库是否安装
python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo 安装schedule库...
    pip install schedule
    if errorlevel 1 (
        echo 错误: 安装schedule库失败
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 启动自动考勤系统...
echo ========================================
echo 定时检查时间:
echo - 10:30 检查缺勤记录
echo - 12:00 中午检查
echo - 15:00 下午检查
echo - 18:30 检查晚退记录
echo - 20:00 晚上检查
echo - 22:00 夜间检查
echo.
echo 按 Ctrl+C 停止系统
echo ========================================
echo.

:: 启动自动考勤系统
python auto_attendance.py

echo.
echo 自动考勤系统已停止
pause 