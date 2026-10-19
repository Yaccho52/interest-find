"""验证手写算法关键性质及真实目录上的日期、重复与无匹配行为。"""

# ============================================================
# 第一部分：验证 TF-IDF 数学实现及聚类基本性质
import json
from model_events import Tfidf, load_catalog, np, recommend, spherical_kmeans


def main():
    """使用小型可手算数据验证算法，再检查真实目录关键功能。"""
    model = Tfidf().fit(['alpha beta', 'alpha gamma'])
    assert np.isclose(model.idf[model.lookup['alpha']], 1)
    assert np.isclose(model.idf[model.lookup['beta']], np.log(3 / 2) + 1)
    x = model.transform(['alpha beta', 'alpha gamma'])
    assert np.allclose(np.linalg.norm(x, axis=1), 1)
    assert not model.transform(['zzzzunknown']).any()
    labels, centers, objective, _ = spherical_kmeans(x, k=2)
    assert len(set(labels)) == 2 and np.isclose(objective, 1)
    assert np.allclose(np.linalg.norm(centers, axis=1), 1)

    # ============================================================
    # 第二部分：检查真实活动的日期、类别、冷启动及去重行为
    catalog = load_catalog()
    model = Tfidf().fit(catalog.text.tolist())
    vectors = model.transform(catalog.text.tolist())
    blast_id = 'blast:rivals-hong-kong-2026'
    results = recommend(catalog, model, vectors, 'CS2 BLAST', as_of='2026-10-19')
    assert results and results[0]['event_id'] == blast_id
    assert not recommend(catalog, model, vectors, 'CS2 BLAST', on_date='2026-11-11')
    assert recommend(catalog, model, vectors, 'CS2 BLAST', on_date='2026-11-13')[0]['event_id'] == blast_id
    assert not recommend(catalog, model, vectors, 'zzzzunknown')
    football = recommend(catalog, model, vectors, '足球', on_date='2026-10-19')
    assert football and all(r['category'] == 'football' for r in football)
    assert all('2026-10-19' in r['dates'] for r in football)
    liked = recommend(catalog, model, vectors, liked_ids=[blast_id], as_of='2026-10-19')
    assert all(r['event_id'] != blast_id for r in liked)
    music = recommend(catalog, model, vectors, '音樂 music', as_of='2026-10-19')
    groups = catalog.set_index('event_id').title_group
    assert len({groups[r['event_id']] for r in music}) == len(music)
    assert all(any(d >= '2026-10-19' for d in r['dates']) for r in music)
    print(json.dumps({'status': '通过', 'checks': ['TF-IDF公式', '向量归一化', '聚类', 'BLAST观众日期',
                                                   '足球查询', '未知词', '已选活动排除', '标题去重', '未来日期过滤']}, ensure_ascii=False))


if __name__ == '__main__':
    # 独立运行检查，无需重新保存模型。
    main()
