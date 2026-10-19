"""使用当前电脑 Python 完成建模和检查，并将完整错误保存为日志。"""

# ============================================================
# 第一部分：标准库环境检查与项目路径定位
import argparse
from datetime import datetime
import importlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def check_environment():
    """显示实际解释器，避免编辑器使用不同 Python 时无法发现。"""
    print('实际 Python：' + sys.executable, flush=True)
    print('Python 版本：' + sys.version.split()[0], flush=True)
    print('项目目录：' + str(ROOT), flush=True)
    if sys.version_info < (3, 10):
        raise RuntimeError('本项目需要 Python 3.10 或以上；当前已验证环境为 Python 3.14。')
    for name in ('numpy', 'pandas'):
        try:
            module = importlib.import_module(name)
        except Exception as error:
            raise RuntimeError(f'当前解释器无法导入 {name}：{error}。请使用运行建模.bat 中已验证的 Python，或在同一解释器中安装 requirements.txt。') from error
        print(f'{name}：{module.__version__}', flush=True)
    required = ['data/processed/events.csv', 'data/processed/sports_events.csv',
                'data/processed/esports_supplements.json']
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        raise RuntimeError('缺少数据文件：' + '、'.join(missing) + '。请保留完整 pycode 文件夹。')


# ============================================================
# 第二部分：在同一解释器、固定工作目录下执行代码
def execute(filename, arguments, log):
    """子进程使用 sys.executable，不依赖另一个 python 命令或终端当前目录。"""
    command = [sys.executable, '-u', '-X', 'utf8', str(ROOT / filename), *arguments]
    environment = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    print('\n正在执行：' + filename, flush=True)
    log.write('\n正在执行：' + filename + '\n')
    log.flush()
    with subprocess.Popen(command, cwd=ROOT, env=environment, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace') as process:
        # 实时显示训练进度，并把完整 traceback 留在日志中。
        for line in process.stdout:
            print(line, end='', flush=True)
            log.write(line)
            log.flush()
        code = process.wait()
    if code:
        raise RuntimeError(f'{filename} 执行失败，退出码 {code}。完整报错已经保存在日志中。')


# ============================================================
# 第三部分：选择运行环节并保存调试结果
def main():
    """默认完整运行；只想检查环境可使用 --action environment。"""
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser(description='拾趣香港建模代码运行入口')
    parser.add_argument('--action', choices=['all', 'train', 'check', 'export', 'environment'], default='all')
    args = parser.parse_args()
    logs = ROOT / 'output' / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    log_path = logs / ('run_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.log')
    with log_path.open('w', encoding='utf-8') as log:
        log.write(f'Python: {sys.executable}\n工作目录: {ROOT}\n')
        try:
            check_environment()
            steps = {'all': ['model_events.py', 'check_models.py', 'build_website.py'],
                     'train': ['model_events.py'], 'check': ['check_models.py'],
                     'export': ['build_website.py'], 'environment': []}[args.action]
            for filename in steps:
                execute(filename, [], log)
        except Exception as error:
            print('\n执行未完成：' + str(error), flush=True)
            log.write('\n执行未完成：' + str(error) + '\n')
            print('错误日志：' + str(log_path), flush=True)
            return 1
    print('\n执行成功。日志：' + str(log_path), flush=True)
    print('网站请联网访问：请参阅 CLOUDFLARE_PAGES.md 配置独立网站地址', flush=True)
    print('本次操作只运行源码，不启动本地网站，也不自动修改线上版本。', flush=True)
    return 0


if __name__ == '__main__':
    # IDE 中直接运行本文件即可，不需要附加命令行参数。
    sys.exit(main())
