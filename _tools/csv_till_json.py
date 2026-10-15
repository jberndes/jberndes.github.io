#!/usr/bin/env python3
"""Gör om en månads-CSV (semikolon) till _tools/tldr/ÅÅÅÅ-MM.json.
Kör:  python3 -I _tools/csv_till_json.py sokvag/2026-09.csv"""
import csv, json, sys, datetime
VD = ['måndag','tisdag','onsdag','torsdag','fredag','lördag','söndag']
MN = ['januari','februari','mars','april','maj','juni','juli','augusti','september','oktober','november','december']
MS = ['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec']
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig'), delimiter=';'))
out = []
for r in rows:
    d = datetime.date.fromisoformat(r['datum'])
    out.append(dict(datum=r['datum'], dag=f"{VD[d.weekday()]} {d.day} {MN[d.month-1]} {d.year}",
                    dag_kort=f"{d.day} {MS[d.month-1]}", nyhetsbrev=r['nyhetsbrev'], rubrik=r['rubrik'].strip(),
                    url=r['url'].strip(), sv=r['sammanfattning_sv'].strip(), kategori=r['kategori'].strip()))
dagar = sorted({o['datum'] for o in out}, reverse=True)
out = [o for d in dagar for o in out if o['datum'] == d]
key = out[0]['datum'][:7]
json.dump(out, open(f'_tools/tldr/{key}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(key, len(out), 'länkar,', len(dagar), 'dagar')
