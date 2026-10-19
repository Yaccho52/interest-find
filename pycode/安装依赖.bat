@echo off
chcp 65001 >nul
REM ============================================================
REM 第一部分：选择与运行建模入口相同的 Python 环境
cd /d "%~dp0"
set "TASK_PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "%TASK_PYTHON%" goto install
where python >nul 2>nul
if errorlevel 1 goto missing
set "TASK_PYTHON=python"

REM ============================================================
REM 第二部分：联网安装已验证依赖，然后确认库可以导入
:install
"%TASK_PYTHON%" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto failed
"%TASK_PYTHON%" -X utf8 -c "import sys,numpy,pandas,debugpy; print('解释器：',sys.executable); print('依赖导入成功。')"
if errorlevel 1 goto failed
echo 安装与检查已完成。
pause
exit /b 0
:missing
echo 没有找到 Python，请检查安装位置。
pause
exit /b 1
:failed
echo 安装或导入失败，请保留上方完整报错。
pause
exit /b 1
