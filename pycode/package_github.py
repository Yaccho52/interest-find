"""整理 GitHub 与 Cloudflare Pages 专用仓库，不修改原项目或上传远程。"""

# ============================================================
# 第一部分：定义允许进入仓库的源码、数据与静态网站
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT / 'github_repo'
ARCHIVE = ROOT / 'output' / 'github' / 'hk-events-github.zip'


def copy_file(relative):
    """逐个复制文件，禁止携带原项目的 Git 历史或隐藏凭据。"""
    source, target = ROOT / relative, REPOSITORY / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


# ============================================================
# 第二部分：生成便携、无账号路径的仓库内容
def main():
    """使用明确白名单生成可上传仓库，并输出可校验的 ZIP。"""
    REPOSITORY.mkdir(parents=True, exist_ok=True)
    scripts = ['audit_data.py', 'prepare_sports.py', 'model_events.py', 'recommend_events.py',
               'check_models.py', 'build_website.py', 'run_pipeline.py', 'requirements.txt',
               '安装依赖.bat', '运行建模.bat']
    for name in scripts:
        copy_file(name)
    for directory in ['data', 'site/dist', 'output/model']:
        for source in sorted((ROOT / directory).rglob('*')):
            if source.is_file() and not any(part.startswith('.') for part in source.relative_to(ROOT).parts):
                copy_file(source.relative_to(ROOT))
    # 模型报告中的旧线上网址只作为过去的展示入口，导出版本改用独立部署说明。
    for relative in ['model_events.py', 'run_pipeline.py', 'output/model/建模报告.md']:
        path = REPOSITORY / relative
        text = path.read_text(encoding='utf-8')
        text = text.replace('https://hk-interest-events.civilvale513.chatgpt.site', '请参阅 CLOUDFLARE_PAGES.md 配置独立网站地址')
        path.write_text(text, encoding='utf-8')
    # 不把本机账户名和解释器绝对路径作为公开仓库的运行记录。
    result_path = REPOSITORY / 'output' / 'model' / 'results.json'
    result = json.loads(result_path.read_text(encoding='utf-8'))
    result['python'] = 'Python 3.14（原始环境已验证）'
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    # ============================================================
    # 第三部分：输出仓库设置、部署文档与检查入口
    documents = ROOT / 'github_templates'
    for source in sorted(documents.rglob('*')):
        if source.is_file():
            target = REPOSITORY / source.relative_to(documents)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED) as package:
        for source in sorted(REPOSITORY.rglob('*')):
            if source.is_file() and not any(part in ('__pycache__', '.git', '.openai') for part in source.relative_to(REPOSITORY).parts):
                package.write(source, arcname=source.relative_to(REPOSITORY).as_posix())
    with zipfile.ZipFile(ARCHIVE) as package:
        names = package.namelist()
        assert 'README.md' in names and 'site/dist/index.html' in names
        assert not any('/.git/' in name or '.openai/' in name or '__pycache__/' in name for name in names)
        assert package.testzip() is None
    print(f'仓库目录：{REPOSITORY}')
    print(f'上传压缩包：{ARCHIVE}')
    print(f'共 {len(names)} 个文件，压缩包 {ARCHIVE.stat().st_size:,} 字节。')


if __name__ == '__main__':
    # 仅整理本地文件，不创建 GitHub 仓库，不读取任何访问令牌。
    main()
