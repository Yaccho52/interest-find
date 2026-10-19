"""加载已保存模型，通过命令行查询香港活动推荐结果。"""

# ============================================================
# 第一部分：加载现有环境与本地模型
import argparse
from datetime import datetime, timedelta, timezone
import json

from model_events import OUT, Tfidf, np, pd, recommend


def main():
    """读取查询及筛选条件，并输出带推荐理由的结果。"""
    parser = argparse.ArgumentParser(description='香港文化、体育及电竞活动推荐')
    parser.add_argument('--query', default='', help='兴趣文字，例如 CS2 BLAST 或音樂')
    parser.add_argument('--liked', nargs='*', default=[], help='已喜欢的活动编号')
    # 香港为固定 UTC+8，避免 Windows 缺少 IANA 时区库时无法运行。
    parser.add_argument('--as-of', default=datetime.now(timezone(timedelta(hours=8))).date().isoformat(), help='参考日期 YYYY-MM-DD')
    parser.add_argument('--on-date', help='指定参加日期 YYYY-MM-DD')
    parser.add_argument('--category', help='类别代码，例如 esports 或 football')
    parser.add_argument('--venue', help='场地名称中的文字')
    parser.add_argument('--all-dates', action='store_true', help='包括历史及日期未知的活动')
    args = parser.parse_args()
    if not (OUT / 'model.npz').exists():
        parser.error('请先运行 python model_events.py 完成建模')
    if not args.query.strip() and not args.liked:
        parser.error('请提供 --query 兴趣文字或 --liked 活动编号')

    # ============================================================
    # 第二部分：恢复词表、IDF 和活动向量
    catalog = pd.read_csv(OUT / 'catalog.csv', dtype=str, keep_default_na=False)
    catalog['dates'] = catalog.dates.map(json.loads)
    model = Tfidf()
    model.vocabulary = json.loads((OUT / 'vocabulary.json').read_text(encoding='utf-8'))
    model.lookup = {term: i for i, term in enumerate(model.vocabulary)}
    with np.load(OUT / 'model.npz', allow_pickle=False) as arrays:
        model.idf = arrays['idf']
        vectors = arrays['vectors']

    # ============================================================
    # 第三部分：根据条件推荐并展示共同关键词
    results = recommend(catalog, model, vectors, query=args.query, liked_ids=args.liked,
                        as_of=None if args.all_dates else args.as_of, on_date=args.on_date,
                        category=args.category, venue=args.venue)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if not results:
        print('当前条件下没有足够匹配的活动，请更换关键词或筛选条件。')


if __name__ == '__main__':
    # 程序入口保持简单，便于现场演示和解释。
    main()
