# 香港文化活动推荐系统数据

下载日期：2026-10-19。来源为香港康文署公开数据。
数据入口：https://data.gov.hk/en-data/dataset/hk-lcsd-event-event-cultural

## 文件内容

- raw/events.xml：官方活动原始数据，1,103 条。
- raw/eventDates.xml：官方活动日期，按活动 ID 关联；每条记录可含多个日期。
- raw/venues.xml：官方场地数据，165 个场地，按 venueid 关联。
- raw/holiday.xml：官方场地休息日期文件；本次快照没有休息日期记录，不代表场地全年开放。
- processed/events.csv：已合并活动、日期和场地的表格，UTF-8 BOM 编码，可供后续建模读取。
- processed/audit.json：样本量、缺失值、类别分布等数据检查结果。
- docs/data_dictionary.pdf：官方字段说明及类别编码表。
- manifest.json：文件清单、大小及 SHA-256 校验值。
- raw/sports/：新增大型体育赛事、港超赛程及电竞核查页面原始资料。
- processed/sports_events.csv：128 条体育与电竞记录（包含历史赛事）。
- processed/esports_supplements.json：BLAST 香港 CS2 赛事详情及逐项来源，区分完整赛期与现场观众日期。
- SPORTS_SOURCES.md：体育来源、范围、限制及 NBA 接入状态。

## 使用注意

原始 XML 保持下载内容不变。价格缺失不等于免费，详情缺失不使用虚构内容补齐。
日期 20990101 已在整理表中标记为需要审查，不能直接当作真实活动日期。
部分场地没有坐标。官方数据是活动目录，不包含用户评分、点击或购票记录。
后续建模优先读取 processed/events.csv；处理逻辑可通过项目根目录的 audit_data.py 复现。
