# GitHub + Cloudflare Pages 部署步骤

## 1. 上传 GitHub 仓库

1. 登录你的 GitHub 账号，新建一个仓库；名称可自行选择。
2. 如果使用网页上传：解压 hk-events-github.zip，把解压后的所有内容上传到仓库根目录。
3. 仓库首页应直接看到 README.md、model_events.py、data 和 site；不要再包一层 github_repo 文件夹。
4. ZIP 只是传输容器，不要只上传 ZIP 压缩文件本身。
5. 如果网页上传时遗漏隐藏文件，可使用 Git 推送，或在 GitHub 手动添加 .gitignore 和 .gitattributes。

也可以在整理好的 github_repo 目录打开终端，使用你实际创建的仓库 URL：

```text
git init
git add .
git commit -m "Initial project"
git branch -M main
git remote add origin 你自己的GitHub仓库URL
git push -u origin main
```

上述“你自己的GitHub仓库URL”为说明文字，执行前替换为真实地址。
如果保密提交作业源码，可使用私有仓库并仅授权 Cloudflare 访问该仓库。

## 2. 在 Cloudflare 连接仓库

1. 登录 Cloudflare，在 Workers & Pages 中创建应用，选择 **Pages**。
2. 选择连接或导入现有 Git 仓库，授权 GitHub，选中你的仓库。
3. 不要选择创建 Worker；本项目当前采用 Pages 静态网站部署。
4. 构建配置填写：

| 项目 | 值 |
|---|---|
| 生产分支 | main |
| 框架预设 | None |
| 根目录 | 留空 |
| 构建命令 | exit 0 |
| 构建输出目录 | site/dist |
| 环境变量 | SKIP_DEPENDENCY_INSTALL = 1 |

这些参数部署仓库中已有的静态网页，不在云端重新训练 Python 模型。
请将 SKIP_DEPENDENCY_INSTALL 同时应用于生产和预览环境，以免平台尝试安装本地建模专用依赖。
等待成功后，Cloudflare 会给出实际的 pages.dev 地址。该地址以你的项目结果为准，本文没有创建网站或预订名称。

## 3. 自定义网址

- 可以使用 Cloudflare 项目分配的 pages.dev 网址。
- 如果要使用你自己的域名，需要先拥有域名，再在该 Pages 项目中的 Custom domains 添加。
- 按 Cloudflare 给出的准确验证和 DNS 记录完成配置，等 HTTPS 就绪后测试。
- 不要只凭示例域名创建 DNS；以实际项目中的记录为准。

## 4. 以后如何更新

在自己电脑运行 run_pipeline.py 后，把更新的源码和 site/dist 文件提交到 GitHub。
Cloudflare 的 Git 集成会按配置自动发布该分支的更新。
如果你只改活动数据，仍需要运行建模和网站导出，网页才会使用新目录。

## 5. 发布后检查

1. 普通浏览器不登录时，首页也能打开。
2. 三轮兴趣点击可以到达结果页。
3. 不填写日期能看到全部匹配记录，并可继续加载。
4. 开始日期晚于结束日期时出现提示。
5. 图片、地点、活动日期和官方详情链接正常。

如果首页 404，确认输出目录为 site/dist，而且其中直接包含 index.html。
如果首页能开但活动加载失败，确认 data.json、app.js 和 assets 也已提交。

## 官方参考

- https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- https://developers.cloudflare.com/pages/get-started/git-integration/
- https://developers.cloudflare.com/pages/configuration/custom-domains/
- https://developers.cloudflare.com/pages/configuration/build-image/#skip-dependency-install
