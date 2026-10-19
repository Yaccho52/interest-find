"""香港活动推荐：使用现有 NumPy 环境，自行实现 TF-IDF、球面 K-means 和 MMR。"""

# ============================================================
# 第一部分：导入依赖与固定运行配置
import collections
from datetime import date, timedelta
import hashlib
import html
import json
import os
from pathlib import Path
import re
import unicodedata

# 限制线程数量，避免小型矩阵计算占用过多资源；不安装或切换 Python 环境。
os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'processed'
OUT = ROOT / 'output' / 'model'
SEED = 7005
STOP = set('the a an and or of in on at to for by with from is are this that hong kong presented series'.split())

# 显式维护少量简繁体及领域别名；这属于人工检索规则，不是学习得到的翻译模型。
ALIASES = {
    '音乐': '音樂', '电影': '電影', '戏剧': '戲劇', '展览': '展覽',
    '图书馆': '圖書館', '儿童': '兒童', '电竞': '電競', '足球': 'football',
    '篮球': 'basketball', '电競': '電競', '電競': 'esports',
    '反恐精英': 'counterstrike cs2', '絕對武力': 'counterstrike cs2',
    'counter-strike': 'counterstrike cs2', '工作坊': 'workshop',
    '音樂': 'music', '電影': 'film', '戲劇': 'theatre', '展覽': 'exhibition',
    '舞蹈': 'dance', '兒童': 'children', '中國戲曲': 'opera',
}


def normalize(text):
    """清除 HTML 与格式差异，保留中文、英文和数字。"""
    text = html.unescape(re.sub(r'<[^>]*>', ' ', str(text)))
    return unicodedata.normalize('NFKC', text).lower().strip()


def tokens(text):
    """英文使用词项，中文使用二字及三字片段；适合无分词依赖的现有环境。"""
    text = normalize(text)
    # 保留原文字，再追加匹配到的别名，因此简繁中文标题仍可保留原始特征。
    expanded = text + ' ' + ' '.join(value for key, value in ALIASES.items() if key in text)
    result = [w for w in re.findall(r'[a-z][a-z0-9]+', expanded) if w not in STOP]
    for run in re.findall(r'[\u3400-\u9fff]+', expanded):
        for width in (2, 3):
            result.extend(run[i:i + width] for i in range(len(run) - width + 1))
    return result


def title_key(text):
    """把标点及空格差异合并，用于排除相同节目标题的推荐和评估泄漏。"""
    return re.sub(r'[^a-z0-9\u3400-\u9fff]', '', normalize(text))


# ============================================================
# 第二部分：合并文化、体育和电竞数据，并处理可用日期
def parse_sports_dates(text):
    """解析目录中的日/月/年范围；遇到无法识别的格式返回空列表。"""
    text = text.strip()
    patterns = [r'(\d+)-(\d+)/(\d+)/(\d{4})',
                r'(\d+)/(\d+)-(\d+)/(\d+)/(\d{4})',
                r'(\d+)/(\d+)/(\d{4})']
    for index, pattern in enumerate(patterns):
        match = re.fullmatch(pattern, text)
        if not match:
            continue
        values = list(map(int, match.groups()))
        try:
            if index == 0:
                a, b, m, y = values
                start, end = date(y, m, a), date(y, m, b)
            elif index == 1:
                a, m, b, n, y = values
                start, end = date(y, m, a), date(y, n, b)
            else:
                a, m, y = values
                start = end = date(y, m, a)
            if not 0 <= (end - start).days <= 90:
                return []
            return [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]
        except ValueError:
            return []
    return []


def load_catalog():
    """统一字段并保留真实来源，未知价格与未确认日期不擅自填补。"""
    culture = pd.read_csv(DATA / 'events.csv', dtype=str, keep_default_na=False)
    sports = pd.read_csv(DATA / 'sports_events.csv', dtype=str, keep_default_na=False)
    supplements = {r['event_id']: r for r in json.loads((DATA / 'esports_supplements.json').read_text(encoding='utf-8'))}
    rows = []
    for r in culture.to_dict('records'):
        valid = []
        for raw in r['dates'].split('|'):
            try:
                d = date.fromisoformat(f'{raw[:4]}-{raw[4:6]}-{raw[6:8]}')
                if d.year < 2090:
                    valid.append(d.isoformat())
            except ValueError:
                pass
        rows.append(dict(event_id='lcsd:' + r['event_id'], title=r['titlec'] or r['titlee'],
                         title_en=r['titlee'], description=r['descc'] + ' ' + r['desce'],
                         category=r['cat2'].lower(), venue=r['venuec'] or r['venuee'],
                         price_text=r['pricec'] or r['pricee'], dates=sorted(set(valid)),
                         date_text=r['predateC'] or r['predateE'], url=r['urlc'] or r['urle'],
                         source='LCSD', extra_terms=''))
    for r in sports.to_dict('records'):
        detail = supplements.get(r['event_id'], {})
        if detail:
            valid = detail['public_dates']
        elif r['start_local']:
            valid = [r['start_local'][:10]]
        elif re.fullmatch(r'\d{4}-\d{2}-\d{2}', r['date_text']):
            # 开赛时间待定并不意味着比赛日期也未知。
            valid = [r['date_text']]
        else:
            valid = parse_sports_dates(r['date_text'])
        rows.append(dict(event_id=r['event_id'], title=r['title_tc'] or r['title'],
                         title_en=r['title'], description='', category=r['category'],
                         venue=r['venue'], price_text=r['price_text'], dates=valid,
                         date_text=r['date_text'], url=r['detail_url'], source=r['provenance'],
                         extra_terms=' '.join([detail.get('game', ''), *detail.get('game_aliases', [])])))
    catalog = pd.DataFrame(rows)
    assert catalog.event_id.is_unique, '活动编号重复，需先审查数据'
    catalog['title_group'] = catalog.title.map(title_key)
    # 训练文本不加入类别代码、价格或日期，避免类别代理评估出现直接标签泄漏。
    catalog['text'] = catalog.apply(lambda r: ' '.join([r.title, r.title_en, r.title,
                                                         r.description, r.extra_terms]), axis=1)
    return catalog


# ============================================================
# 第三部分：自行实现 TF-IDF 及向量归一化
def unit(matrix):
    """将向量归一化，使点积等于余弦相似度；零向量保留为零。"""
    return matrix / np.maximum(np.linalg.norm(matrix, axis=-1, keepdims=True), 1e-12)


class Tfidf:
    """采用平滑 IDF 和对数词频，不调用机器学习库的一行向量化接口。"""
    def fit(self, texts, max_features=12000):
        # 文档频次用于学习词表及 IDF；目录无监督拟合不等于留出测试评估。
        df = collections.Counter()
        for text in texts:
            df.update(set(tokens(text)))
        vocabulary = sorted(df, key=lambda term: (-df[term], term))[:max_features]
        self.vocabulary = vocabulary
        self.lookup = {term: i for i, term in enumerate(vocabulary)}
        self.idf = np.array([np.log((1 + len(texts)) / (1 + df[t])) + 1 for t in vocabulary], dtype=np.float32)
        return self

    def transform(self, texts):
        """把新查询映射至训练词表；词表外查询得到零向量。"""
        matrix = np.zeros((len(texts), len(self.vocabulary)), dtype=np.float32)
        for row, text in enumerate(texts):
            for term, count in collections.Counter(tokens(text)).items():
                if term in self.lookup:
                    column = self.lookup[term]
                    matrix[row, column] = (1 + np.log(count)) * self.idf[column]
        return unit(matrix)


# ============================================================
# 第四部分：自行实现球面 K-means 主题聚类
def spherical_kmeans(x, k=8, seed=SEED, max_iter=40):
    """在单位向量上按余弦相似度聚类，使用距离加权初始化。"""
    rng = np.random.default_rng(seed)
    chosen = [int(rng.integers(len(x)))]
    for _ in range(1, k):
        distance = np.maximum(1 - (x @ x[chosen].T).max(axis=1), 0)
        distance[chosen] = 0
        chosen.append(int(rng.choice(len(x), p=distance / distance.sum())))
    centers = x[chosen].copy()
    previous = None
    for iteration in range(max_iter):
        similarities = x @ centers.T
        labels = similarities.argmax(axis=1)
        if previous is not None and np.array_equal(labels, previous):
            break
        previous = labels.copy()
        for cluster in range(k):
            members = x[labels == cluster]
            # 空簇用当前最难匹配的样本重置，防止出现无效中心。
            centers[cluster] = members.mean(axis=0) if len(members) else x[similarities.max(axis=1).argmin()]
        centers = unit(centers)
    # 最后一次更新中心之后重新计算标签和目标值。
    similarity = x @ centers.T
    labels = similarity.argmax(axis=1)
    return labels, centers, float(similarity.max(axis=1).mean()), iteration + 1


# ============================================================
# 第五部分：相关性推荐、兴趣向量与 MMR 多样性重排
def rank(x, scores, candidates, groups, top_k=5, diversity=0.2):
    """MMR 在相关度与重复度间权衡，同时排除同标题重复活动。"""
    candidates = [int(i) for i in candidates if scores[i] > 1e-8]
    candidates.sort(key=lambda i: (-float(scores[i]), i))
    candidates = candidates[:100]
    selected, selected_groups = [], set()
    while candidates and len(selected) < top_k:
        def objective(i):
            redundancy = max(float(x[i] @ x[j]) for j in selected) if selected else 0
            return (1 - diversity) * float(scores[i]) - diversity * redundancy
        best = max(candidates, key=objective)
        candidates.remove(best)
        if groups[best] not in selected_groups:
            selected.append(best)
            selected_groups.add(groups[best])
    return selected


def recommend(catalog, model, x, query='', liked_ids=None, as_of=None, on_date=None,
              category=None, venue=None, diversity=0.2, top_k=5):
    """结合文字及已选活动形成兴趣向量；没有匹配时返回空列表。"""
    vectors = []
    if query.strip():
        vectors.append(model.transform([query])[0])
    liked_ids = liked_ids or []
    known = set(catalog.event_id)
    if set(liked_ids) - known:
        raise ValueError('所选活动编号不存在')
    liked_mask = catalog.event_id.isin(liked_ids).to_numpy()
    if liked_mask.any():
        vectors.append(unit(x[liked_mask].mean(axis=0)))
    if not vectors:
        return []
    interest = unit(np.mean(vectors, axis=0))
    scores = x @ interest
    # 球队名称可能没有“足球”字样：明确类别意图时加入可解释的元数据加分。
    # 这项规则仅用于产品查询，不加入向量训练或前述类别代理评估。
    query_tokens = set(tokens(query))
    requested = [name for name in ('football', 'basketball', 'esports') if name in query_tokens]
    category_bonus = catalog.category.isin(requested).to_numpy() if requested else np.zeros(len(catalog), dtype=bool)
    scores = scores + 0.15 * category_bonus
    keep = ~liked_mask
    # 不为凑满五条而返回极弱词面匹配；阈值是公开的产品规则，尚未用用户反馈调优。
    threshold = max(0.05, float(scores.max()) * 0.1)
    keep &= scores >= threshold
    if liked_mask.any():
        keep &= ~catalog.title_group.isin(catalog.loc[liked_mask, 'title_group']).to_numpy()
    if as_of:
        date.fromisoformat(as_of)
        keep &= catalog.dates.map(lambda dates: any(d >= as_of for d in dates)).to_numpy()
    if on_date:
        date.fromisoformat(on_date)
        keep &= catalog.dates.map(lambda dates: on_date in dates).to_numpy()
    if category:
        keep &= catalog.category.eq(category).to_numpy()
    if venue:
        keep &= catalog.venue.str.contains(venue, case=False, regex=False).to_numpy()
    selected = rank(x, scores, np.flatnonzero(keep), catalog.title_group.tolist(), top_k, diversity)
    result = []
    for i in selected:
        event = catalog.iloc[i]
        overlap = x[i] * interest
        terms = [model.vocabulary[j] for j in np.argsort(-overlap)[:5] if overlap[j] > 0]
        if category_bonus[i]:
            terms.append('类别匹配:' + event.category)
        result.append(dict(event_id=event.event_id, title=event.title, score=round(float(scores[i]), 4),
                           matched_terms=terms, category=event.category, venue=event.venue,
                           dates=event.dates, price_text=event.price_text or '未知', url=event.url))
    return result


# ============================================================
# 第六部分：目录代理评估与聚类结果解释
def evaluate(catalog, model, x):
    """用同类别检索作为弱代理，不宣称真实用户满意度或未来泛化准确率。"""
    counts = catalog.category.value_counts()
    # 单例类别不纳入此项统计，且明确排除相同标题组，避免简单复现标题。
    pool = np.flatnonzero(catalog.category.map(counts).ge(10).to_numpy())
    rng = np.random.default_rng(SEED)
    queries = rng.choice(pool, size=min(100, len(pool)), replace=False)
    groups = catalog.title_group.tolist()
    metrics = {name: [] for name in ['keyword', 'tfidf', 'tfidf_mmr']}
    coverage = {name: set() for name in metrics}
    similarities = {name: [] for name in metrics}
    empty_queries = 0
    for i in queries:
        candidates = np.flatnonzero(catalog.title_group.ne(groups[i]).to_numpy())
        q = model.transform([catalog.iloc[i].title])[0]
        scores = x @ q
        empty_queries += int(not np.any(q))
        query_terms = set(tokens(catalog.iloc[i].title))
        keyword = np.array([len(query_terms & set(tokens(t))) for t in catalog.text], dtype=np.float32)
        for name, values, penalty in [('keyword', keyword, 0), ('tfidf', scores, 0), ('tfidf_mmr', scores, 0.2)]:
            selected = rank(x, values, candidates, groups, diversity=penalty)
            # 不足五项仍除以五，避免只返回一项时获得虚高的 precision@5。
            metrics[name].append(sum(catalog.iloc[j].category == catalog.iloc[i].category for j in selected) / 5)
            coverage[name].update(selected)
            if len(selected) > 1:
                block = x[selected] @ x[selected].T
                similarities[name].append(float(block[np.triu_indices(len(selected), 1)].mean()))
    return dict(protocol='目录内检索代理评估；无用户反馈；非留出测试；按相同标题排除自匹配',
                queries=len(queries), empty_query_vectors=empty_queries,
                methods={name: dict(category_precision_at_5=float(np.mean(values)),
                                    catalog_coverage=len(coverage[name]) / len(catalog),
                                    mean_intra_list_similarity=float(np.mean(similarities[name])))
                         for name, values in metrics.items()})


# ============================================================
# 第七部分：训练、保存模型和生成可复查报告
def train():
    """运行完整流程并保存模型、统一目录、评估和示例结果。"""
    print('[1/6] 正在读取活动数据……', flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog()
    print(f'[2/6] 已读取 {len(catalog)} 条记录，正在计算 TF-IDF……', flush=True)
    model = Tfidf().fit(catalog.text.tolist())
    x = model.transform(catalog.text.tolist())
    if np.any(np.linalg.norm(x, axis=1) == 0):
        raise ValueError('目录中出现零向量，请检查标题或词表截断')
    print('[3/6] 正在运行三次主题聚类……', flush=True)
    runs = []
    for offset in range(3):
        runs.append(spherical_kmeans(x, seed=SEED + offset))
        print(f'      聚类初始化 {offset + 1}/3 已完成', flush=True)
    labels, centers, objective, iterations = max(runs, key=lambda run: run[2])
    catalog['cluster'] = labels
    topics = []
    for cluster, center in enumerate(centers):
        members = np.flatnonzero(labels == cluster)
        representative = sorted(members, key=lambda i: float(x[i] @ center), reverse=True)[:5]
        topics.append(dict(cluster=cluster, size=len(members),
                           terms=[model.vocabulary[j] for j in np.argsort(-center)[:10]],
                           examples=catalog.iloc[representative].title.tolist()))
    print('[4/6] 正在比较关键词、TF-IDF 和多样性排序……', flush=True)
    evaluation = evaluate(catalog, model, x)
    examples = {query: recommend(catalog, model, x, query=query, as_of='2026-10-19')
                for query in ['CS2 BLAST', '足球 football', '音樂 music', '兒童 children', 'exhibition 展覽']}
    # 目录保留所有真实样本，推荐时才按日期过滤；不对历史样本进行未来预测。
    print('[5/6] 正在保存模型、目录和报告……', flush=True)
    serial = catalog.copy()
    serial['dates'] = serial.dates.map(lambda value: json.dumps(value, ensure_ascii=False))
    serial.to_csv(OUT / 'catalog.csv', index=False, encoding='utf-8-sig')
    np.savez_compressed(OUT / 'model.npz', vectors=x, idf=model.idf, centers=centers, labels=labels)
    (OUT / 'vocabulary.json').write_text(json.dumps(model.vocabulary, ensure_ascii=False), encoding='utf-8')
    summary = dict(python=os.sys.executable, numpy=np.__version__, pandas=pd.__version__, seed=SEED,
                   catalog_size=len(catalog), vocabulary_size=len(model.vocabulary),
                   title_groups=int(catalog.title_group.nunique()),
                   unknown_dates=int(catalog.dates.map(len).eq(0).sum()),
                   sources=catalog.source.value_counts().to_dict(),
                   input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in [DATA / 'events.csv', DATA / 'sports_events.csv', DATA / 'esports_supplements.json']},
                   clustering=dict(k=len(centers), objective=objective, iterations=iterations,
                                   restart_objectives=[r[2] for r in runs], topics=topics),
                   evaluation=evaluation, examples=examples)
    (OUT / 'results.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 第一轮建模报告', '', f'样本数：{len(catalog)}；标题组：{summary["title_groups"]}；词表：{len(model.vocabulary)}。',
             '', '使用当前 Python、NumPy、pandas；未安装新环境。自行实现 TF-IDF、球面 K-means 与 MMR。',
             '类别不进入文本向量；日期仅用于筛选。少量人工简繁及游戏别名规则已在代码中明示。',
             '', '## 代理评估', '', '这是目录内的同类别检索代理，不是用户满意度，也不是监督学习留出测试。',
             '每次排除相同标题组；近似标题仍可能相似。类别较粗且样本不均衡，不用于宣称推荐准确率。',
             '', '| 方法 | 同类 P@5 | 目录覆盖率 | 列表内相似度 |', '|---|---:|---:|---:|']
    for name, value in evaluation['methods'].items():
        lines.append(f'| {name} | {value["category_precision_at_5"]:.3f} | {value["catalog_coverage"]:.3f} | {value["mean_intra_list_similarity"]:.3f} |')
    lines += ['', '## 聚类主题', '', '固定八簇是可浏览界面的设计选择，未使用 elbow method；比较三个随机初始化并选余弦目标最高者。',
              '主题簇可能反映标题模板、语言或系列名称，需要人工检查，不保证每簇都是独立语义主题。']
    for topic in topics:
        lines += ['', f'簇 {topic["cluster"]}（{topic["size"]} 项）：' + '、'.join(topic['terms']),
                  '代表活动：' + '；'.join(topic['examples'][:3])]
    lines += ['', '## 使用与限制', '', '运行 python recommend_events.py --query "CS2 BLAST" 查看现有目录推荐。',
              '默认仅推荐香港日期当天或之后有可用日期的活动；日期未知的活动不会被当作未来活动。',
              '产品查询对明确足球、篮球、电竞意图加入 0.15 类别加分；此规则不进入训练或上面的代理评估。',
              '推荐分数为排序分数，不是用户喜欢概率。过滤低于 0.05 或最高分十分之一的弱匹配，不强行填满结果。',
              '没有用户评分、点击或购票数据，因此不训练协同过滤；电竞只有少量赛事，不单独训练分类器。',
              '保留未知价格与原始票价说明，不声称掌握实时余票。',
              '在线网站：https://hk-interest-events.civilvale513.chatgpt.site；本地导出不会自动修改线上版本。',
              '报告应声明 AI 协助实现代码、数据整理和分析；学生需要独立理解公式、实现与局限。']
    (OUT / '建模报告.md').write_text('\n'.join(lines), encoding='utf-8')
    print('[6/6] 建模完成。', flush=True)
    print(json.dumps({key: summary[key] for key in ['catalog_size', 'vocabulary_size', 'title_groups', 'unknown_dates', 'evaluation']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    # 直接执行本文件即可完成第一轮模型训练。
    train()
