@echo off
cd /d %~dp0
echo ===============================
echo Starting Project Launcher...
echo ===============================

:: 确保 Python 和 venv 可用
if not exist venv (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

:: 激活虚拟环境
echo Activating virtual environment...
call venv\Scripts\activate

:: 安装缺失的 Python 依赖
echo Installing required Python packages...
pip install -r ./backend/requirements.txt

:: 运行 Launcher.py
echo Launching the UI...
echo ===============================
echo Launcher has been started!
echo ===============================
python docker_launcher.py

pause
