# 拾趣香港完整源码

网站仍通过原网址联网访问：
https://hk-interest-events.civilvale513.chatgpt.site

双击“打开在线网站.bat”即可访问；不需要启动本地网页服务。

## 运行建模代码

双击 **运行建模.bat**，会使用本机已经验证的 Python 3.14，依次执行：

1. model_events.py：训练与代理评估。
2. check_models.py：公式、日期和推荐行为检查。
3. build_website.py：导出网站使用的推荐数据。

运行过程显示进度，错误会完整保存在 output/logs/。不自动安装软件或更改 Python 环境。
也可以在 IDE 中直接运行 run_pipeline.py，或使用命令 `python -X utf8 run_pipeline.py`。
只打开 model_events.py 并运行也可以，其路径以自身所在目录为准。

当前验证的环境：

- Python 3.14.7
- NumPy 2.5.3
- pandas 3.0.5
- debugpy 1.8.22（编辑器调试支持）

以上库已安装到本机 Python 3.14 的 site-packages，并已验证可以导入。
需要重新安装时，可双击“安装依赖.bat”。json、csv、pathlib 等为 Python 自带模块，不需要单独安装。
model_events 是本目录中的模型源码文件，不是需要从网上下载的库。
VS Code 可以打开“拾趣香港.code-workspace”，使用项目解释器配置。

VS Code 中请打开整个 pycode 文件夹。本目录提供指向当前电脑 Python 3.14 的调试配置。
如果编辑器之前选中了其他解释器，请选择上述现有解释器；不要仅凭终端显示的版本判断编辑器环境。

## 文件布局

- model_events.py、recommend_events.py：核心模型与推荐查询。
- audit_data.py、prepare_sports.py：数据检查及体育资料整理。
- check_models.py：算法及真实数据行为检查。
- build_website.py：网页数据导出。
- run_pipeline.py：环境诊断、运行和日志入口。
- data/：官方原始数据、整理数据、字段说明与来源。
- output/model/：训练输出、推荐示例及报告。
- output/logs/：运行日志。
- site/dist/：已发布网站的 HTML、CSS、JavaScript、图片及数据。
- site/.openai/：原在线网站的项目标识，供后续更新同一网站使用。
- tools/local_preview/：之前的本地预览工具，仅作开发留档，不作为网站使用入口。

## 运行与发布的区别

运行建模代码会更新本地模型与网站数据，不会自动修改线上网站。
网站始终可通过原网址打开。需要把模型或界面更新到线上时，再进行网站发布。

## 本次排查结论

当前电脑的 Python 3.14 环境能够完整训练，原始报错未复现，因此没有把某个推测说成已确认原因。
本次补充固定解释器入口、明确工作目录、中文输出编码、训练进度和完整错误日志，便于稳定运行和继续定位。
推荐程序的香港时间改为标准库 UTC+8，避免依赖 Windows 系统是否安装 IANA 时区数据库。

所有源码与运行所需数据都在本文件夹中，请整体保留或移动。
