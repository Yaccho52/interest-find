"""把现有网站打包为可独立托管的文件，不包含 ChatGPT 托管配置。"""

# ============================================================
# 第一部分：定位网站源文件与独立发布目录
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'site' / 'dist'
DESTINATION = ROOT / 'independent_site'
OUTPUT = ROOT / 'output' / 'independent'


# ============================================================
# 第二部分：复制可公开的网站文件，保留活动数据与相对资源地址
def main():
    """生成独立目录和 ZIP；不会创建账号、发布网站或购买域名。"""
    DESTINATION.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = ['index.html', 'app.js', 'styles.css', 'refinements.css', 'data.json']
    assets = sorted(p for p in (SOURCE / 'assets').rglob('*') if p.is_file())
    for relative in files + [p.relative_to(SOURCE).as_posix() for p in assets]:
        source = SOURCE / relative
        target = DESTINATION / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    # 浏览器只读同站点文件；无需 OpenAI API、登录服务或原来的托管标识。
    for name in ['index.html', 'app.js', 'styles.css', 'refinements.css']:
        text = (DESTINATION / name).read_text(encoding='utf-8')
        if re.search(r'chatgpt\.site|api\.openai\.com|auth\.openai\.com', text, re.I):
            raise ValueError(f'{name} 仍有原平台的运行地址，需要先检查。')
    data = json.loads((DESTINATION / 'data.json').read_text(encoding='utf-8'))
    assert data['total'] == len(data['events'])
    assert all((DESTINATION / event['image']).is_file() for event in data['events'])

    # ============================================================
    # 第三部分：生成平台配置及可直接上传的压缩包
    configuration = '# 静态网站已构建完成，不需要在线运行 Python。\n[build]\n  publish = "."\n'
    (DESTINATION / 'netlify.toml').write_text(configuration, encoding='utf-8')
    included = files + [p.relative_to(SOURCE).as_posix() for p in assets] + ['netlify.toml']
    archive = OUTPUT / '拾趣香港_独立部署.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as package:
        for relative in included:
            package.write(DESTINATION / relative, arcname=relative)
    # 文件校验结果放在发布目录之外，便于确认压缩包没有混入原始数据或凭据。
    with zipfile.ZipFile(archive) as package:
        assert 'index.html' in package.namelist()
        assert not any('.git/' in name or '.openai/' in name for name in package.namelist())
        assert package.testzip() is None
    report = {'events': len(data['events']), 'files': len(included),
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'external_platform_api_required': False}
    (OUTPUT / 'package_check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'独立部署文件夹：{DESTINATION}')
    print(f'独立部署压缩包：{archive}')
    print(f'验证通过：{len(data["events"])} 条活动，{len(included)} 个发布文件。')


if __name__ == '__main__':
    # 更新网页数据后重新运行本文件，即可刷新独立部署版本。
    main()
