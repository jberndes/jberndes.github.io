#!/usr/bin/env python3
"""Bygger /ai/arkiv/ (index + en sida per månad) från _tools/tldr/ÅÅÅÅ-MM.json.
Kör:  python3 -I _tools/bygg_arkiv.py   (från repots rot)"""
import json, glob, os, html, re

MAN = ['januari','februari','mars','april','maj','juni','juli','augusti','september','oktober','november','december']
e = html.escape

STYLE = open('_tools/arkiv.css', encoding='utf-8').read()

def shell(title, desc, canon, body, back_href, back_txt):
    return f'''<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" media="(prefers-color-scheme: light)" content="#fafaf8">
  <meta name="theme-color" media="(prefers-color-scheme: dark)" content="#131512">
  <title>{e(title)} – Joakim Berndes</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="https://joakimberndes.se{canon}">
  <style>
{STYLE}  </style>
</head>
<body>
  <a class="hoppa" href="#innehall">Hoppa till innehållet</a>
{body}
</body>
</html>
'''

def header(back_href, back_txt, h1, ingress):
    return f'''  <header>
    <div class="inre">
      <a class="tillbaka" href="{back_href}"><span aria-hidden="true">&larr;</span> {e(back_txt)}</a>
      <h1>{e(h1)}</h1>
      <p class="ingress">{ingress}</p>
    </div>
  </header>'''

FOOT = '''  <footer>
    <div class="inre">
      <p>Källa: <a href="https://tldr.tech/" target="_blank" rel="noopener">TLDR<span class="dold"> (öppnas i ny flik)</span></a> (TLDR AI och TLDR Tech). Rubrikerna står på originalspråket och länkarna leder till originalet. Sammanfattningarna är gjorda på svenska med egna ord.</p>
    </div>
  </footer>'''

months = {}
for f in sorted(glob.glob('_tools/tldr/*.json')):
    key = os.path.basename(f)[:-5]
    months[key] = json.load(open(f, encoding='utf-8'))
keys = sorted(months)

def mname(k):
    y, m = k.split('-'); return f'{MAN[int(m)-1]} {y}'

def li(it):
    return f'''          <li>
            <a lang="en" href="{e(it['url'])}" target="_blank" rel="noopener">{e(it['rubrik'])}<span class="dold"> (öppnas i ny flik)</span></a>
            <span class="meta">{e(it['nyhetsbrev'])} · {e(it['kategori'])}</span>
            <span class="sv">{e(it['sv'])}</span>
          </li>'''

for i, k in enumerate(keys):
    items = months[k]
    days = []
    for it in items:
        if not days or days[-1][0] != it['datum']:
            days.append((it['datum'], it['dag'], it['dag_kort'], []))
        days[-1][3].append(it)
    y, m = k.split('-')
    idx = '\n'.join(f'        <li><a href="#d-{d}">{e(kort)}</a></li>' for d, _, kort, _ in days)
    secs = '\n'.join(f'''      <section id="d-{d}" aria-labelledby="h-{d}">
        <h2 id="h-{d}">{e(dag)}</h2>
        <ol class="tldr">
{chr(10).join(li(x) for x in its)}
        </ol>
      </section>''' for d, dag, _, its in days)
    nav = []
    if i > 0: nav.append(f'<a href="/ai/arkiv/{keys[i-1].replace("-", "/")}/">&larr; {e(mname(keys[i-1]))}</a>')
    if i < len(keys)-1: nav.append(f'<a href="/ai/arkiv/{keys[i+1].replace("-", "/")}/">{e(mname(keys[i+1]))} &rarr;</a>')
    navhtml = f'      <p class="manadsnav">{" · ".join(nav)}</p>\n' if nav else ''
    ingress = f'{len(days)} dagar och {len(items)} länkar ur TLDR AI och TLDR Tech, med egna korta sammanfattningar på svenska. Senaste dagen överst.'
    body = header('/ai/arkiv/', 'Arkiv', mname(k).capitalize(), ingress) + f'''
  <main id="innehall" tabindex="-1">
    <div class="inre">
{navhtml}      <nav aria-label="Hoppa till datum" class="dagar">
        <ul>
{idx}
        </ul>
      </nav>
{secs}
{navhtml}    </div>
  </main>
''' + FOOT
    out = f'ai/arkiv/{y}/{m}/index.html'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(shell(f'{mname(k).capitalize()} – AI-arkiv', f'Arkiv över dagliga AI- och tekniknyheter från TLDR, {mname(k)}.', f'/ai/arkiv/{y}/{m}/', body, '/ai/arkiv/', 'Arkiv'))

rows = '\n'.join(f'''        <li><a href="/ai/arkiv/{k.replace("-", "/")}/">{e(mname(k).capitalize())}</a> <span class="antal">{len({x["datum"] for x in months[k]})} dagar, {len(months[k])} länkar</span></li>''' for k in reversed(keys))
body = header('/ai/', 'AI-nyheter', 'Arkiv', 'Dagliga urval ur TLDR AI och TLDR Tech, sorterade per månad.') + f'''
  <main id="innehall" tabindex="-1">
    <div class="inre">
      <h2 class="dold">Månader</h2>
      <ul class="manader">
{rows}
      </ul>
    </div>
  </main>
''' + FOOT
os.makedirs('ai/arkiv', exist_ok=True)
open('ai/arkiv/index.html', 'w', encoding='utf-8').write(shell('AI-arkiv', 'Arkiv över dagliga AI- och tekniknyheter från TLDR, sorterat per månad.', '/ai/arkiv/', body, '/ai/', 'AI-nyheter'))
print('klart:', keys)
