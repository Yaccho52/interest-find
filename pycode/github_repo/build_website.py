"""用现有 Python 推荐模型导出网站数据与主题插画，不重新训练或安装依赖。"""

# ============================================================
# 第一部分：载入活动目录和现有模型
import csv
import json
from pathlib import Path
import re

from model_events import OUT, ROOT, Tfidf, np, pd, rank

DEST = ROOT / 'site' / 'dist'


def category_filter(*categories):
    """生成类别筛选器；标签只用于明确的用户兴趣过滤。"""
    return lambda row: row['category'] in categories


def contains(*words):
    """按真实标题关键词建立更细的兴趣分组，不虚构活动属性。"""
    return lambda row: any(word.lower() in (row['title'] + ' ' + row['title_en']).lower() for word in words)


# ============================================================
# 第二部分：定义三轮点击的兴趣树，第三轮只显示有真实样本的选项
def make_tree(records):
    """大方向、活动类型、具体偏好构成三轮选择；全部选项保留完整目录。"""
    definitions = [
        ('arts', '文化与艺术', '一场演出，一次展览，或一点新灵感。', 'music', [
            ('music', '音乐现场', '古典、流行与人声的相遇', category_filter('inc4sc1', 'inc4sc9'), [
                ('classical', '古典与器乐', contains('钢琴', '鋼琴', '管弦', '交響', 'piano', 'orchestra', 'recital'), 'classical music piano'),
                ('pop', '流行音乐', category_filter('inc4sc9'), 'pop concert'),
                ('choir', '合唱与人声', contains('合唱', '聖樂', 'choir', 'choral'), 'choir choral music')]),
            ('stage', '戏剧与舞蹈', '走进舞台上的另一个世界', category_filter('inc4sc2', 'inc4sc3', 'inc4sc6', 'inc4sc7', 'inc4sc12'), [
                ('dance', '舞蹈', category_filter('inc4sc3'), 'dance 舞蹈'),
                ('opera', '中国戏曲', category_filter('inc4sc2'), 'opera 中國戲曲'),
                ('theatre', '戏剧', category_filter('inc4sc6'), 'theatre 戲劇'),
                ('multi', '跨媒介与综合表演', category_filter('inc4sc7', 'inc4sc12'), 'multi arts show')]),
            ('art', '展览与工作坊', '慢慢看，也亲手试一试', category_filter('inc4sc4', 'inc4sc14', 'inc6sc1', 'inc7sc3', 'inc7sc5'), [
                ('exhibition', '看一场展览', category_filter('inc4sc4', 'inc6sc1', 'inc7sc3'), 'exhibition 展覽'),
                ('workshop', '参加工作坊', category_filter('inc4sc14', 'inc7sc5'), 'workshop 工作坊')]),
            ('film', '电影与影像', '把时间交给一个好故事', category_filter('inc4sc5'), [
                ('cinema', '电影放映', contains('電影', 'film', 'cinema', 'screening'), 'film cinema')]),
            ('family', '亲子与阅读', '给大小朋友都留一点好奇心', category_filter('inc7sc1', 'inc7sc2', 'inc7sc6', 'inc4sc11'), [
                ('children', '儿童活动', category_filter('inc7sc1', 'inc4sc11'), 'children 兒童'),
                ('reading', '阅读与文学', category_filter('inc7sc2', 'inc7sc6'), 'reading literature')]),
            ('festival', '节庆与更多', '在城市里偶遇一份惊喜', category_filter('inc4sc8', 'inc4sc10', 'inc4sc11', 'inc7sc8', 'inc9sc2', 'inc9sc3'), [
                ('festivals', '节庆节目', category_filter('inc4sc10', 'inc9sc3'), 'festival 節慶'),
                ('free', '免费文娱节目', category_filter('inc9sc2'), 'free entertainment')])]),
        ('sports', '体育赛事', '去现场，为喜欢的球队和运动喝彩。', 'football', [
            ('football', '足球', '港超联赛与国际足球盛事', category_filter('football'), [
                ('hkpl', '香港超级联赛', lambda r: r['event_id'].startswith('hkfa:'), 'football Hong Kong Premier League'),
                ('international', '国际足球赛事', lambda r: r['event_id'].startswith('mmark:'), 'football international FIFA')]),
            ('major', '更多体育盛事', '网球、榄球、排球与更多精彩', category_filter('other_sport', 'basketball'), [
                ('tennis', '网球', contains('tennis'), 'tennis'),
                ('rugby', '榄球', contains('sevens', 'rugby', 'wxv'), 'rugby sevens'),
                ('volleyball', '排球', contains('volleyball'), 'volleyball'),
                ('golf', '高尔夫球', contains('golf'), 'golf'),
                ('running', '马拉松', contains('marathon'), 'marathon'),
                ('other', '其他竞技项目', lambda r: not contains('tennis', 'sevens', 'rugby', 'wxv', 'volleyball', 'golf', 'marathon')(r), 'sports competition')])]),
        ('esports', '电子竞技', '从召唤师峡谷，到 Counter-Strike 赛场。', 'esports', [
            ('cs2', 'Counter-Strike 2', 'BLAST 香港站，感受线下赛场', contains('BLAST'), [
                ('blast', 'BLAST 香港站', contains('BLAST'), 'CS2 BLAST')]),
            ('lol', '英雄联盟', 'LCK 顶级赛事的香港现场', contains('LCK'), [
                ('lck', 'LCK 香港赛事', contains('LCK'), 'LCK League of Legends')])])]
    tree, rankings, memberships = [], {}, {}
    for bid, label, description, image, branches in definitions:
        branch_nodes = []
        for sid, slabel, subtitle, predicate, leaves in branches:
            members = [i for i, row in enumerate(records) if predicate(row)]
            if not members:
                continue
            leaf_nodes = []
            for lid, llabel, lp, query in [('all', '全部相关活动', lambda row: True, slabel), *leaves]:
                ids = [i for i in members if lp(records[i])]
                if not ids:
                    continue
                key = f'{bid}/{sid}/{lid}'
                memberships[key] = ids
                rankings[key] = query
                leaf_nodes.append(dict(id=lid, key=key, label=llabel, count=len(ids)))
            branch_nodes.append(dict(id=sid, label=slabel, description=subtitle, count=len(members), leaves=leaf_nodes))
        all_ids = set(i for key, ids in memberships.items() if key.startswith(bid + '/') for i in ids)
        tree.append(dict(id=bid, label=label, description=description, image=f'assets/{image}.svg', count=len(all_ids), branches=branch_nodes))
    # 无法分类的新类别必须显式失败，防止数据被悄悄排除。
    all_members = set(i for ids in memberships.values() for i in ids)
    assert all_members == set(range(len(records))), '有活动尚未分入兴趣树'
    return tree, memberships, rankings


# ============================================================
# 第三部分：生成自绘横版主题插画，避免把配图冒充活动现场照片
def illustrations():
    """文化数据没有官方图片，提供清楚标记的本地主题插画作为稳定后备。"""
    drawings = {
        'music': ('#f8eae5', '#b97962', '<path d="M410 305V145l155-35v160M410 185l155-35"/><ellipse cx="385" cy="307" rx="28" ry="20"/><ellipse cx="540" cy="272" rx="28" ry="20"/><path d="M295 240q-40 50 0 100M640 140q50 50 0 100"/>'),
        'football': ('#e8f0e9', '#548269', '<circle cx="465" cy="245" r="105"/><path d="m465 195 47 34-18 55h-58l-18-55zM465 140v55M565 211l-53 18M527 330l-33-46M402 330l34-46M365 211l53 18M315 365h305"/>'),
        'esports': ('#eceaf8', '#8176aa', '<rect x="310" y="125" width="320" height="205" rx="18"/><path d="M435 330v40m70-40v40m-110 0h150M350 280l65-75 55 35 70-65 50 35"/><circle cx="570" cy="155" r="6"/>'),
        'stage': ('#f5e9ee', '#a9768e', '<path d="M310 130h320v225H310zM310 130q140 120 10 225M630 130q-140 120-10 225M365 355h210M440 215l70 40-70 40z"/>'),
        'art': ('#e8eff3', '#678698', '<rect x="315" y="125" width="300" height="220" rx="8"/><path d="m340 315 80-90 75 65 50-50 45 75M420 170h1"/><circle cx="535" cy="185" r="25"/><path d="M295 370h340"/>'),
        'film': ('#eeece5', '#918262', '<rect x="315" y="175" width="310" height="180" rx="12"/><path d="M315 175v-55h310v55M345 120l40 55m35-55 40 55m35-55 40 55m35-55 40 55M440 220l70 42-70 42z"/>'),
        'family': ('#faf0dc', '#b19758', '<path d="M300 175q85-30 165 20 80-50 165-20v165q-85-30-165 15-80-45-165-15zM465 195v160M330 220h90m-90 35h90m90-35h90m-90 35h90"/><path d="m660 130 8 20 22 3-17 15 4 22-17-11-18 11 4-22-17-15 23-3z"/>'),
    }
    folder = DEST / 'assets'
    folder.mkdir(parents=True, exist_ok=True)
    for name, (background, ink, shapes) in drawings.items():
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="480" viewBox="0 0 900 480"><rect width="900" height="480" fill="{background}"/><circle cx="150" cy="80" r="180" fill="white" opacity=".25"/><circle cx="800" cy="470" r="220" fill="white" opacity=".3"/><g fill="none" stroke="{ink}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{shapes}</g><circle cx="710" cy="140" r="5" fill="{ink}" opacity=".3"/><circle cx="245" cy="350" r="8" fill="{ink}" opacity=".2"/></svg>'
        (folder / f'{name}.svg').write_text(svg, encoding='utf-8')


# ============================================================
# 第四部分：计算选项对应的推荐排序并导出网页数据
def main():
    """页面只处理点击、日期筛选和展示，推荐向量与排序由 Python 预先计算。"""
    DEST.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(OUT / 'catalog.csv', dtype=str, keep_default_na=False)
    frame['dates'] = frame.dates.map(json.loads)
    records = frame.to_dict('records')
    model = Tfidf()
    model.vocabulary = json.loads((OUT / 'vocabulary.json').read_text(encoding='utf-8'))
    model.lookup = {term: i for i, term in enumerate(model.vocabulary)}
    with np.load(OUT / 'model.npz', allow_pickle=False) as arrays:
        model.idf, x = arrays['idf'], arrays['vectors']
    tree, memberships, queries = make_tree(records)
    rankings = {}
    for key, ids in memberships.items():
        scores = x @ model.transform([queries[key]])[0]
        priority = rank(x, scores, ids, frame.title_group.tolist(), top_k=8, diversity=0.2)
        # 推荐优先项排在前面，其余匹配记录全部保留，不用 Top-5 截断目录。
        rest = sorted(set(ids) - set(priority), key=lambda i: (-float(scores[i]), records[i]['event_id']))
        rankings[key] = priority + rest
    public = []
    sports_original = {r['event_id']: r for r in csv.DictReader((ROOT / 'data' / 'processed' / 'sports_events.csv').open(encoding='utf-8-sig'))}
    for r in records:
        category = r['category']
        image = ('esports' if category == 'esports' else 'football' if category in ('football', 'other_sport', 'basketball')
                 else 'music' if category in ('inc4sc1', 'inc4sc9') else 'stage' if category in ('inc4sc2', 'inc4sc3', 'inc4sc6', 'inc4sc7', 'inc4sc12')
                 else 'film' if category == 'inc4sc5' else 'family' if category.startswith('inc7') else 'art')
        # 仅公开活动事实；不上传原始数据、完整模型或项目文件。
        original = sports_original.get(r['event_id'], {})
        start = original.get('start_local', '')
        session_time = f'{start[11:16]}（香港时间）' if start else ''
        public.append({key: r[key] for key in ('event_id', 'title', 'title_en', 'category', 'venue', 'price_text', 'dates', 'date_text', 'url', 'source')}
                      | dict(image=f'assets/{image}.svg', image_kind='主题插画', session_time=session_time))
    payload = dict(snapshot='2026-10-19', total=len(public), tree=tree, events=public, rankings=rankings)
    (DEST / 'data.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    illustrations()
    print(f'网站已导出：{len(public)} 条活动，{len(rankings)} 条兴趣路径。')


if __name__ == '__main__':
    # 从项目根目录运行 python -X utf8 build_website.py 即可刷新网站数据。
    main()
