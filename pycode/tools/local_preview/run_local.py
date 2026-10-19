"""在本机启动拾趣香港：仅使用 Python 标准库，不需要安装网站框架。"""

# ============================================================
# 第一部分：导入标准库并定位项目内的网站文件
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import webbrowser

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'site' / 'dist'


# ============================================================
# 第二部分：创建仅供本机访问的网页服务
class LocalHandler(SimpleHTTPRequestHandler):
    """只提供网站目录，禁用目录列表，并避免浏览器缓存旧版数据。"""

    def list_directory(self, path):
        # 网站不需要目录索引，不向访问者列出文件。
        self.send_error(403, 'Directory listing is disabled')
        return None

    def end_headers(self):
        # 修改页面或更新数据后，刷新浏览器即可看到新版本。
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, format, *args):
        # 日常成功请求保持安静；错误请求仍显示，方便排查。
        if len(args) > 1 and str(args[1]).startswith(('4', '5')):
            print('网页请求提示：', format % args, flush=True)


def create_server(port):
    """默认端口占用时寻找附近可用端口；只绑定本机回环地址。"""
    handler = partial(LocalHandler, directory=str(WEB))
    ports = [0] if port == 0 else range(port, min(port + 20, 65536))
    last_error = None
    for candidate in ports:
        try:
            server = ThreadingHTTPServer(('127.0.0.1', candidate), handler)
            server.daemon_threads = True
            return server
        except OSError as error:
            last_error = error
            # 只对端口已占用重试；权限、系统限制等错误原样报告。
            if getattr(error, 'winerror', None) != 10048 and error.errno != 98:
                raise
    raise OSError('没有找到可用端口，请关闭旧的网站窗口后重试。') from last_error


# ============================================================
# 第三部分：检查文件、打开浏览器并等待用户关闭
def main():
    """启动时直接使用已经生成的推荐数据，不需要联网或重新训练。"""
    parser = argparse.ArgumentParser(description='启动拾趣香港本地网站')
    parser.add_argument('--port', type=int, default=8765, help='本机端口，默认 8765；0 表示自动选择')
    parser.add_argument('--no-browser', action='store_true', help='只启动服务，不自动打开浏览器')
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error('端口必须在 0 至 65535 之间')
    required = ['index.html', 'app.js', 'styles.css', 'refinements.css', 'data.json']
    missing = [name for name in required if not (WEB / name).is_file()]
    if missing:
        print('缺少网站文件：' + '、'.join(missing))
        print('请保留完整项目文件夹；数据缺失时运行 python -X utf8 build_website.py。')
        return 1
    try:
        server = create_server(args.port)
    except OSError as error:
        print(f'本地网站启动失败：{error}')
        return 1
    url = f'http://127.0.0.1:{server.server_port}/'
    print('\n拾趣香港本地网站已启动。', flush=True)
    print(f'访问地址：{url}', flush=True)
    print('无需登录，无需联网。活动详情链接仍需网络。', flush=True)
    print('使用期间请保留此窗口；按 Ctrl+C 或关闭窗口停止网站。\n', flush=True)
    try:
        if not args.no_browser:
            # 浏览器无法自动打开时，仍保留服务并提供可手动打开的地址。
            try:
                if not webbrowser.open(url, new=2):
                    print('请复制上面的地址到浏览器打开。', flush=True)
            except webbrowser.Error:
                print('浏览器未能自动打开，请手动访问上面的地址。', flush=True)
        server.serve_forever(poll_interval=0.3)
    except KeyboardInterrupt:
        print('\n本地网站已停止。')
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    # -X utf8 可保证中文路径和提示在当前 Windows 环境正确显示。
    sys.exit(main())
