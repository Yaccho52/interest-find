@echo off
chcp 65001 >nul
REM ============================================================
REM 第一部分：定位项目并优先使用电脑现有的 Python
cd /d "%~dp0"
set "TASK_PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "%TASK_PYTHON%" goto run_known
where python >nul 2>nul
if not errorlevel 1 goto run_path
where py >nul 2>nul
if not errorlevel 1 goto run_py
echo 没有找到 Python，请先安装 Python 或配置 PATH。
pause
exit /b 1

REM ============================================================
REM 第二部分：启动本地网页，服务运行期间保留此窗口
:run_known
"%TASK_PYTHON%" -X utf8 "%~dp0run_local.py"
goto finished
:run_path
python -X utf8 "%~dp0run_local.py"
goto finished
:run_py
py -3 -X utf8 "%~dp0run_local.py"
:finished
if errorlevel 1 pause
