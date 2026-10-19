"""Inspect the downloaded LCSD snapshot without modifying the source XML."""
from pathlib import Path
import collections
import csv
import json
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
RAW = BASE / 'data' / 'raw'
OUT = BASE / 'data' / 'processed'


def main():
    events = list(ET.parse(RAW / 'events.xml').getroot())
    venues = {v.attrib['id']: v for v in ET.parse(RAW / 'venues.xml').getroot()}
    dates = {}
    for record in ET.parse(RAW / 'eventDates.xml').getroot():
        dates.setdefault(record.attrib['id'], set()).update(
            node.text for node in record.findall('indate') if node.text)
    rows = []
    for event in events:
        row = {'event_id': event.attrib['id']}
        row.update({node.tag: (node.text or '').strip() for node in event})
        venue = venues.get(row.get('venueid'))
        for field in ('venuec', 'venuee', 'latitude', 'longitude'):
            row[field] = (venue.findtext(field) or '').strip() if venue is not None else ''
        row['dates'] = '|'.join(sorted(dates.get(row['event_id'], set())))
        # 20990101 appears in the source; preserve it but flag it for review.
        row['date_needs_review'] = any(d >= '20900101' for d in dates.get(row['event_id'], []))
        row['price_status'] = ('unknown' if not row.get('pricec') and not row.get('pricee')
                               else 'source_text_available')
        rows.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (OUT / 'events.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    report = {
        'events': len(rows), 'venues': len(venues),
        'duplicate_event_ids': len(rows) - len({r['event_id'] for r in rows}),
        'missing_fields': {field: sum(not r.get(field) for r in rows)
                           for field in ('titlec', 'titlee', 'descc', 'desce', 'pricec', 'latitude')},
        'category_counts': dict(collections.Counter(r['cat1'] for r in rows)),
        'subcategory_counts': dict(collections.Counter(r['cat2'] for r in rows)),
        'events_without_date_records': sum(not r['dates'] for r in rows),
        'events_with_dates_needing_review': sum(r['date_needs_review'] for r in rows),
        'unmatched_venues': sum(r.get('venueid') not in venues for r in rows),
    }
    (OUT / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
