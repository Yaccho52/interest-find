# 拾趣香港 · 香港文化、体育与电竞活动推荐

使用香港开放数据和 Python 实现的活动推荐项目，支持三轮兴趣点击、可选日期筛选与活动卡片展示。

本仓库可以独立部署到 Cloudflare Pages，不调用 OpenAI API，不要求访客登录，不依赖 ChatGPT 托管。
当前收录 1,231 条目录记录，数据快照为 2026-10-19；不是实时票务服务。

## 在 Cloudflare Pages 发布

本仓库已包含生成好的网站，首次发布无需训练模型或安装 Python 依赖。

| 设置 | 填写内容 |
|---|---|
| 部署服务 | Cloudflare **Pages**，连接 GitHub 仓库 |
| Framework preset / 框架预设 | None |
| Production branch / 生产分支 | main |
| Root directory / 根目录 | 留空，使用仓库根目录 |
| Build command / 构建命令 | `exit 0` |
| Build output directory / 构建输出目录 | `site/dist` |
| Environment variables / 环境变量 | `SKIP_DEPENDENCY_INSTALL` = `1` |

完整操作与自定义域名说明见 [CLOUDFLARE_PAGES.md](CLOUDFLARE_PAGES.md)。

该环境变量跳过云端依赖安装；仓库中的 requirements.txt 仅用于本地建模，静态网页部署无需安装这些包。

## 文件结构

```text
仓库根目录/
  README.md
  CLOUDFLARE_PAGES.md
  .gitignore
  .gitattributes
  requirements.txt
  run_pipeline.py          # 统一运行入口和错误日志
  model_events.py          # 手写 TF-IDF、聚类与 MMR
  recommend_events.py      # 命令行推荐
  check_models.py          # 算法与真实数据行为检查
  audit_data.py            # 文化数据清洗和检查
  prepare_sports.py        # 体育与电竞资料整理
  build_website.py         # 导出兴趣树、活动与排序
  validate_repo.py         # 无第三方依赖的部署文件检查
  data/                   # 原始资料、整理表格及来源说明
  output/model/           # 已训练模型和评估报告
  site/dist/              # Cloudflare 实际发布的网页目录
```

## 在自己的电脑重新建模

已验证环境：Python 3.14.7、NumPy 2.5.3、pandas 3.0.5。

```text
python -m pip install -r requirements.txt
python -X utf8 run_pipeline.py
```

Windows 也可以使用“安装依赖.bat”和“运行建模.bat”。
脚本以自身所在目录定位资料，可以从其他工作目录启动。

重新建模会更新 output/model 和 site/dist/data.json。
把更新后的 site/dist 内容提交到 GitHub，Cloudflare 才会将新的网页数据发布。
只改 Python 而没有重新导出网站数据，不会改变网页推荐结果。

## 网站与模型

- Python 预先计算活动文本向量、主题聚类和每条兴趣路径的推荐排序。
- 网页使用 HTML、CSS、JavaScript 处理点击、日期过滤及展示。
- 不填写日期时，保留该兴趣下全部记录，包括历史活动；不是仅显示五项。
- 填写日期时，按实际活动日期匹配范围；日期未知的活动不参与日期筛选。
- 主题插画不代表活动现场照片；票价与余票需到官方页面核实。
- 目录没有真实用户评分，评估为目录检索代理指标，不能解释为用户满意度。

## 数据来源与使用声明

主要数据来自 data.gov.hk 的康文署文化活动和政府Ｍ品牌体育赛事目录，补充香港足总及 BLAST 官方资料。
来源详情见 data/README.md、data/SPORTS_SOURCES.md 及 data/manifest.json。
代码整理和建模使用过 AI 辅助；报告和现场答辩需要明确声明并独立解释实现。
上游数据和网页资料保留其原有权利，本仓库没有替上游内容授予额外许可。

## 检查发布文件

```text
python -X utf8 validate_repo.py
```

仓库未包含 ChatGPT 托管项目标识、旧 Git 历史、个人编辑器配置、日志、缓存或原平台发布包。
