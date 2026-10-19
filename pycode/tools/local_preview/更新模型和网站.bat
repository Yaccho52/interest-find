@echo off
chcp 65001 >nul
REM ============================================================
REM 第一部分：使用现有 Python 环境检查建模依赖
cd /d "%~dp0..\.."
set "TASK_PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "%TASK_PYTHON%" goto check
set "TASK_PYTHON=python"
:check
"%TASK_PYTHON%" -X utf8 -c "import numpy, pandas; print('现有 NumPy 和 pandas 可用。')"
if errorlevel 1 goto failed

REM ============================================================
REM 第二部分：重新训练、验证并导出本地网站数据
"%TASK_PYTHON%" -X utf8 model_events.py
if errorlevel 1 goto failed
"%TASK_PYTHON%" -X utf8 check_models.py
if errorlevel 1 goto failed
"%TASK_PYTHON%" -X utf8 build_website.py
if errorlevel 1 goto failed
echo.
echo 模型和网站数据已更新。请双击“启动网站.bat”，或刷新已经打开的网站。
pause
exit /b 0
:failed
echo.
echo 更新未完成，请查看上方错误信息。现有 Python 环境未被更改。
pause
exit /b 1
