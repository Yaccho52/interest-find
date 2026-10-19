@echo off
chcp 65001 >nul
REM ============================================================
REM 第一部分：定位已验证的 Python 3.14，不更改系统环境
cd /d "%~dp0"
set "TASK_PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "%TASK_PYTHON%" goto run
where python >nul 2>nul
if errorlevel 1 goto no_python
set "TASK_PYTHON=python"

REM ============================================================
REM 第二部分：执行建模、算法检查和网站数据导出，并保留运行结果
:run
"%TASK_PYTHON%" -u -X utf8 "%~dp0run_pipeline.py"
if errorlevel 1 echo 请把 output\logs 中最新日志的报错文字提供给我。
pause
exit /b
:no_python
echo 未找到 Python。此电脑已验证的解释器应位于 LocalAppData\Programs\Python\Python314。
pause
exit /b 1
