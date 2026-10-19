"""Normalize public M Mark and HKFA fixtures snapshots. No JavaScript execution."""
import csv
import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent / 'data'
RAW = BASE / 'raw' / 'sports'


def parse_hkfa(path):
    """Read the literal fixture object from Nuxt's serialized public page data.

    The parser accepts only objects, arrays, primitives and references to
    primitive function arguments. It never evaluates downloaded code.
    """
    text = path.read_text(encoding='utf-8')
    header = re.search(r'window\.__NUXT__=\(function\(([^)]*)\)', text)
    if not header:
        raise ValueError('HKFA page serialization changed')
    end = re.search(r'\}\((.*?)\)\);</script>', text[header.end():], re.S)
    args = re.sub(r'Array\(\d+\)', 'null', end.group(1))
    values = json.loads('[' + args + ']')
    names = header.group(1).split(',')
    if len(names) != len(values):
        raise ValueError('Argument count mismatch')
    lookup = dict(zip(names, values))
    lookup.update({'null': None, 'true': True, 'false': False})
    fragment = text[text.index('listMatchs:', header.end()) + len('listMatchs:'):]
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?|[A-Za-z_$][\w$]*|[{}\[\]:,]', fragment))

    def read(token=None):
        token = next(tokens) if token is None else token
        if token == '{':
            result = {}
            key = next(tokens)
            while key != '}':
                key = json.loads(key) if key.startswith('"') else key
                assert next(tokens) == ':'
                result[key] = read()
                separator = next(tokens)
                if separator == '}':
                    break
                assert separator == ','
                key = next(tokens)
            return result
        if token == '[':
            result = []
            item = next(tokens)
            while item != ']':
                result.append(read(item))
                separator = next(tokens)
                if separator == ']':
                    break
                assert separator == ','
                item = next(tokens)
            return result
        if token.startswith('"') or re.fullmatch(r'-?\d+(?:\.\d+)?', token):
            return json.loads(token)
        return lookup[token]

    return [game for day in read().values() for game in day]


def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = []
    source = 'https://www.cstb.gov.hk/datagovhk/cstbdiv011/resource.csv'
    with (RAW / 'm_mark_events.csv').open(encoding='utf-8-sig', newline='') as f:
        for i, r in enumerate(csv.DictReader(f), 1):
            title = r['event_name_en'].strip()
            # These are transparent derived tags, not government category labels.
            category = ('esports' if 'LCK' in title else
                        'football' if any(w in title.lower() for w in ['football', 'fifa']) else
                        'basketball' if 'basketball' in title.lower() else 'other_sport')
            rows.append(dict(event_id=f'mmark:{i}', title=title, title_tc=r['event_name_tc'].strip(),
                             category=category, date_text=r['date_en'], start_local='',
                             venue=r['venue_en'].strip(), price_text='',
                             source=source, detail_url=r['website'].strip(),
                             location_scope='hong_kong', timezone='Asia/Hong_Kong',
                             status='date_text_only', provenance='government_open_data'))
    games = {}
    for p in sorted(RAW.glob('hkpl_fixtures*.html')):
        for g in parse_hkfa(p):
            if g['match_id'] in games:
                assert games[g['match_id']] == g, 'Conflicting match records'
            games[g['match_id']] = g
    for mid, g in games.items():
        rows.append(dict(event_id=f'hkfa:{mid}',
                         title=f"{g['team_home']['TeamName']} vs {g['team_guest']['TeamName']}",
                         title_tc='', category='football', date_text=g['match_date'],
                         start_local=(f"{g['match_date']}T{g['match_time']}:00+08:00"
                                      if re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', g['match_time']) else ''),
                         venue=g['Venue']['VenueName'], price_text=g.get('match_ticket', ''),
                         source='https://www.hkfa.com/en/competitions/fixtures?competition=2041&year=2026-2027',
                         detail_url='https://www.hkfa.com/en/competitions/fixtures?competition=2041&year=2026-2027',
                         location_scope='hong_kong', timezone='Asia/Hong_Kong',
                         status=g.get('matchStatus', ''), provenance='official_website_extraction'))
    mmark_count = len(rows) - len(games)
    supplements_path = BASE / 'processed' / 'esports_supplements.json'
    supplements = json.loads(supplements_path.read_text(encoding='utf-8')) if supplements_path.exists() else []
    for supplement in supplements:
        # Preserve detailed provenance in JSON; project onto the existing CSV schema.
        rows.append({field: supplement.get(field, '') for field in rows[0]})
    assert len({row['event_id'] for row in rows}) == len(rows), 'Duplicate event IDs'
    output = BASE / 'processed' / 'sports_events.csv'
    write_csv(output, rows)
    # Cross-source duplicates must be reviewed when merging with the cultural catalogue.
    manifest = json.loads((BASE / 'manifest.json').read_text(encoding='utf-8'))
    manifest['files'] = [dict(file=p.relative_to(BASE).as_posix(), bytes=p.stat().st_size,
                              sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                         for p in sorted(BASE.rglob('*')) if p.is_file() and p.name != 'manifest.json']
    (BASE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'M Mark events: {mmark_count}; HKPL matches: {len(games)}; supplements: {len(supplements)}; total: {len(rows)}')


if __name__ == '__main__':
    main()
