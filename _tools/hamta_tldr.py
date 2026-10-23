#!/usr/bin/env python3
"""Hämtar TLDR AI och TLDR Tech för de senaste dagarna och sparar dem som
läsbar text med länkar i _tools/tldr/raw/. Körs av GitHub Actions (hamta-tldr.yml).
Bara standardbiblioteket. Hoppar över utgåvor som redan finns och rensar filer
äldre än 14 dagar. Avslutar med felkod om något oväntat gick fel."""
import datetime
import html.parser
import os
import re
import sys
import time
import urllib.error
import urllib.request

RAW = '_tools/tldr/raw'
LETTERS = {'ai': 'TLDR AI', 'tech': 'TLDR Tech'}
DAYS_BACK = 10
KEEP_DAYS = 14
UA = 'joakimberndes.se-tldr-hamtare (privat bruk, en hämtning per utgåva och dag)'


class Text(html.parser.HTMLParser):
    SKIP = {'script', 'style', 'noscript', 'svg', 'head'}
    BLOCK = {'p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'br', 'section', 'article', 'tr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0
        self.href = None
        self.buf = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == 'a':
            self.href = dict(attrs).get('href')
            self.buf = []
        elif tag in self.BLOCK:
            self.out.append('\n')

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == 'a':
            text = ' '.join(''.join(self.buf).split())
            if self.href and text:
                self.out.append(f'[{text}]({self.href})')
            elif text:
                self.out.append(text)
            self.href = None
            self.buf = []
        elif tag in self.BLOCK:
            self.out.append('\n')

    def handle_data(self, data):
        if self.skip:
            return
        if self.href is not None:
            self.buf.append(data)
        else:
            self.out.append(data)

    def result(self):
        s = ''.join(self.out)
        s = re.sub(r'[ \t]+', ' ', s)
        s = re.sub(r'\n\s*\n+', '\n\n', s)
        return s.strip() + '\n'


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', errors='replace')


def main():
    os.makedirs(RAW, exist_ok=True)
    today = datetime.date.today()
    saved, errors = [], []
    for back in range(DAYS_BACK, -1, -1):
        d = today - datetime.timedelta(days=back)
        if d.weekday() >= 5:
            continue
        for slug, name in LETTERS.items():
            path = f'{RAW}/{d.isoformat()}-{slug}.md'
            if os.path.exists(path):
                continue
            url = f'https://tldr.tech/{slug}/{d.isoformat()}'
            try:
                page = fetch(url)
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    errors.append(f'{url}: HTTP {e.code}')
                continue
            except Exception as e:  # nätverksfel
                errors.append(f'{url}: {e}')
                continue
            p = Text()
            p.feed(page)
            text = p.result()
            if len(text) < 1500:
                print(f'Hoppar över {url}: för lite text ({len(text)} tecken)')
                continue
            header = f'Källa: {url}\nNyhetsbrev: {name}\nDatum: {d.isoformat()}\nHämtad: {datetime.datetime.utcnow().isoformat(timespec="seconds")}Z\n\n'
            with open(path, 'w', encoding='utf-8') as f:
                f.write(header + text)
            saved.append(path)
            print(f'Sparade {path} ({len(text)} tecken)')
            time.sleep(2)
    cutoff = today - datetime.timedelta(days=KEEP_DAYS)
    for fn in os.listdir(RAW):
        m = re.match(r'(\d{4}-\d{2}-\d{2})-(ai|tech)\.md$', fn)
        if m and datetime.date.fromisoformat(m.group(1)) < cutoff:
            os.remove(os.path.join(RAW, fn))
            print(f'Tog bort {fn}')
    print(f'Klart: {len(saved)} nya filer, {len(errors)} fel')
    for e in errors:
        print('FEL', e)
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
