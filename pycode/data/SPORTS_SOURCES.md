# 体育与电竞数据扩展

核查日期：2026-10-19。当前已整理 128 条赛事目录记录，包含历史赛事和未举行赛事。

## 已下载和整理

### 政府 M 品牌赛事：17 条

- 入口：https://data.gov.hk/en-data/dataset/hk-cstb-cstbdiv011-result-of-m-mark-events
- CSV：https://www.cstb.gov.hk/datagovhk/cstbdiv011/resource.csv
- 原始文件：raw/sports/m_mark_events.csv
- 含日期文字、中英文赛事名称、场地、主办方、查询方式和网站。
- 已包含香港 LCK Cup 电竞赛事及足球赛事；并非完整电竞赛程库。
- 原日期文字保留，范围日期尚未全部标准化；没有票价字段，缺失不当作免费。

### 香港超级联赛：110 场

- 官方入口：https://www.hkfa.com/en/competitions/fixtures?competition=2041&year=2026-2027
- 原始文件：raw/sports/hkpl_fixtures.html、hkpl_fixtures_page2.html、hkpl_fixtures_page3.html
- 从官网公开页面保存的赛程资料中提取：主客队、日期时间、场地、票价文字、比赛状态。
- 数据性质是官方网页提取，不是政府开放数据，也不承诺未来网页结构或更新稳定。
- 对主办方版权和使用条款应保留来源并在正式公开发布前核对，不假定官网公开即为开放许可。

### 电竞补充核查页面

- 官方场地页：https://www.kaitaksportspark.com.hk/events-tickets/2026-lck-cup-finals-in-hong-kong-presented-by-cga
- 原始文件：raw/sports/lck_hong_kong.html
- 用于核对 M 品牌目录中的赛事，不另外生成重复活动。
- 此赛事已于 2026-02-28 至 2026-03-01 举办，属于历史样本；默认未来活动推荐应排除。

## 统一表

processed/sports_events.csv 包含 17 条政府赛事、110 场港超比赛及 1 条 BLAST 补充赛事。
每条有来源和 provenance，category 为透明规则派生标签，不冒充官方分类。
start_local 使用香港时间；空白表示尚未解析，不表示全天活动。
后续合并文化目录时需要跨来源查重、统一分类，并处理已结束赛事。
当前单独保留该表，避免直接改变原有 events.csv 的字段。
可通过项目根目录 prepare_sports.py 离线复现。

## NBA 和海外足球：尚未纳入

- NBA 官方赛程：https://www.nba.com/schedule
- 本次尝试的 NBA 公开 JSON 地址返回 HTTP 403，未保存成可用赛事数据，不进行绕过。
- 足球接口说明：https://docs.football-data.org/general/v4/competition.html
- football-data.org 的比赛接口使用 API token；当前没有配置，不创建账号或使用收费服务。
- 海外比赛应标记为海外赛事，不自动推断香港有直播、免费观看或本地观赛活动。
- 若扩展线上观赛推荐，应另加香港时间、当地直播来源及其核查日期。

## 建模范围

继续做内容推荐、聚类及多样性排序，不预测比分、不做时间序列。
目录没有真实用户偏好、点击或满意度；不能将赛事数量或类别当作用户喜好标签。
电竞样本目前为 1 个政府目录 LCK 赛事和 1 个 BLAST 官方资料补充赛事，仍不足以单独训练可靠的电竞类别模型。

## BLAST 香港 CS2 补充

- 已加入 BLAST Premier Rivals Hong Kong 2026，一条赛事级记录，不虚构逐场对阵。
- 详细结构化信息：processed/esports_supplements.json；统一表也包含该赛事。
- BLAST 整体赛期：2026-11-11 至 2026-11-15。
- 场馆和香港旅发局公布的现场观众日期：2026-11-13 至 2026-11-15。
- 场地：AsiaWorld-Arena（亚洲国际博览馆 1 号展馆）。
- 官方来源链接保存在 JSON 的 verification_sources 字段。
- 场馆票价和旅发局摘要有差异，标记 price_needs_review，不将最低票面价格当作当前可买最低价。
- 每日具体比赛时刻未核实，start_local 留空，不能解释为午夜开赛。
- 原始网页如下载成功保存在 raw/sports/blast_hong_kong_2026*.html。
- 这是主办方、场馆与旅发局公开资料整理，不冒充 data.gov.hk 数据。
