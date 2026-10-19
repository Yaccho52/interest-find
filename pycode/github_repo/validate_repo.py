"""只用 Python 标准库检查 GitHub 仓库和 Cloudflare 发布文件。"""

# ============================================================
# 第一部分：检查首页、资源路径和目录完整性
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
WEB = ROOT / 'site' / 'dist'


def main():
    """只检查源码和数据，不联网、不安装包、不运行模型训练。"""
    required = ['index.html', 'app.js', 'styles.css', 'refinements.css', 'data.json']
    for name in required:
        assert (WEB / name).is_file(), f'缺少网站文件：{name}'
    page = (WEB / 'index.html').read_text(encoding='utf-8')
    for reference in re.findall(r'(?:src|href)="([^"]+)"', page):
        if reference.startswith(('https:', 'http:', '#', './')):
            continue
        assert (WEB / reference).is_file(), f'本地资源不存在：{reference}'

    # ============================================================
    # 第二部分：检查活动与全部兴趣路径，不允许丢失匹配活动
    data = json.loads((WEB / 'data.json').read_text(encoding='utf-8'))
    events = data['events']
    assert data['total'] == len(events)
    assert len({event['event_id'] for event in events}) == len(events)
    for event in events:
        assert (WEB / event['image']).is_file(), f'缺少配图：{event["image"]}'
    covered = set()
    for broad in data['tree']:
        for branch in broad['branches']:
            for leaf in branch['leaves']:
                order = data['rankings'][leaf['key']]
                assert len(order) == len(set(order)) == leaf['count']
                assert all(0 <= index < len(events) for index in order)
                covered.update(order)
    assert covered == set(range(len(events))), '有活动未进入兴趣树'

    # ============================================================
    # 第三部分：检查源码语法与独立部署要求
    for path in ROOT.glob('*.py'):
        # 使用内置编译检查，不在可上传目录生成 __pycache__。
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
    assert not (ROOT / 'site' / '.openai').exists(), '仓库混入原平台托管配置'
    for name in ['index.html', 'app.js', 'styles.css', 'refinements.css']:
        text = (WEB / name).read_text(encoding='utf-8')
        assert not re.search(r'chatgpt\.site|api\.openai\.com|auth\.openai\.com', text, re.I)
    print(f'检查通过：{len(events)} 条活动、{len(data["rankings"])} 条兴趣路径、全部配图和 Python 语法正常。')
    print('Cloudflare Pages：构建命令 exit 0；输出目录 site/dist。')


if __name__ == '__main__':
    # 直接运行即可检查，无需 NumPy、pandas 或 GitHub 凭据。
    main()
