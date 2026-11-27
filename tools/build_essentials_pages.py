#!/usr/bin/env python3
"""Builds the Essentials archive on anly.app from articles/essentials.json.

  essentials/index.html          list of published posts, newest first
  essentials/<id>-<slug>.html    one page per post (title, picture, text, source)

Run from the website folder after essentials.json changes:

  python3 tools/build_essentials_pages.py

Standard library only. Every post gets a page (essentials.json is public
anyway), but the list only links posts whose publishOn has come; the list page
also re-reads essentials.json in the browser, so a new day's post shows up
without a rebuild. Pages are plain HTML so search engines can read them and
links can be shared (Demi 2026-11-27: one post a day; the app's SEE ALL keeps
8 weeks and sends older ones here).
"""
import datetime
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEED = os.path.join(ROOT, 'articles', 'essentials.json')
OUT = os.path.join(ROOT, 'essentials')
SITE = 'https://anly.app'
SUPPORT = os.path.join(ROOT, 'support.html')


def esc(s):
    return html.escape(s or '', quote=True)


def slug(a):
    s = re.sub(r'[^a-z0-9]+', '-', a['title'].lower()).strip('-')
    return f"{a['id']}-{s[:60].rstrip('-')}"


def page_name(a):
    return slug(a) + '.html'


def nice_date(d):
    return datetime.date.fromisoformat(d).strftime('%B %-d, %Y')


def shared_parts():
    """Nav, fonts and footer copied from support.html, with links pointed one
    folder up, so the archive always matches the rest of the site."""
    src = open(SUPPORT, encoding='utf-8').read()
    head_links = re.search(r'(\s*<link rel="icon".*?<link rel="stylesheet" href="styles.css" />)', src, re.S).group(1)
    nav = re.search(r'(<header class="nav">.*?</header>)', src, re.S).group(1)
    footer = re.search(r'(<footer class="footer">.*?</footer>)', src, re.S).group(1)

    def up(s):
        s = re.sub(r'(href|src)="(?!https?:|mailto:|#|\.\./)([^"]*)"', r'\1="../\2"', s)
        return s
    footer = up(footer).replace('<a href="../shop.html">Shop</a>',
                                '<a href="index.html">Essentials</a>\n      <a href="../shop.html">Shop</a>')
    return up(head_links), up(nav), footer


def first_text(a):
    for b in a['blocks']:
        if b['kind'] in ('paragraph', 'step'):
            t = b['text'].replace('\n', ' ')
            return t if len(t) <= 160 else t[:157].rsplit(' ', 1)[0] + '…'
    return a['title']


def body_html(a):
    out, steps = [], []

    def flush():
        if steps:
            out.append('<ol class="ess-steps">' + ''.join(steps) + '</ol>')
            steps.clear()
    for b in a['blocks']:
        k, t = b['kind'], b['text']
        if k == 'step':
            head, _, rest = t.partition('\n')
            item = f'<strong>{esc(head)}</strong>' + (f'<br />{esc(rest)}' if rest else '')
            steps.append(f'<li>{item}</li>')
            continue
        flush()
        if k == 'bigNumber':
            out.append(f'<p class="ess-big">{esc(t)}</p>')
        elif k == 'source':
            out.append(f'<p class="ess-source">{esc(t)}</p>')
        else:
            out.append(f'<p>{esc(t)}</p>')
    flush()
    return '\n      '.join(out)


def article_page(a, head_links, nav, footer):
    url = f"{SITE}/essentials/{page_name(a)}"
    desc = first_text(a)
    img = a.get('hero')
    hero = f'<img class="ess-hero" src="{esc(img)}" alt="" />' if img else ''
    og_img = f'\n  <meta property="og:image" content="{esc(img)}" />' if img else ''
    ld = json.dumps({
        '@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'],
        'datePublished': a['publishOn'], 'image': img or f'{SITE}/assets/app-icon-1024.jpg',
        'publisher': {'@type': 'Organization', 'name': 'ANLY APP LLC'},
        'mainEntityOfPage': url}, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(a['title'])} — Anly Essentials</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{esc(a['title'])}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{url}" />{og_img}
  <meta name="twitter:card" content="summary_large_image" />
  <script type="application/ld+json">{ld}</script>
{head_links}
</head>
<body>

  {nav}

  <main>
    <article class="ess-article">
      <p class="ess-crumb"><a href="index.html">Essentials</a></p>
      {hero}
      <p class="eyebrow ess-tag">{esc(a['tag'])}</p>
      <h1>{esc(a['title'])}</h1>
      <p class="legal-meta">{nice_date(a['publishOn'])} · {esc(a['readTime'])}</p>
      <div class="ess-body">
      {body_html(a)}
      </div>
      <p class="ess-cta">One tap a day tells your people you're okay. <a href="../index.html#download">Get Anly</a></p>
    </article>
  </main>

  {footer}

</body>
</html>
'''


def card(a):
    img = a.get('hero')
    pic = f'<img src="{esc(img)}" alt="" loading="lazy" />' if img else '<span class="ess-card-blank" aria-hidden="true"></span>'
    return (f'<a class="ess-card" href="{page_name(a)}">{pic}'
            f'<span class="ess-card-text"><span class="ess-card-tag">{esc(a["tag"])}</span>'
            f'<span class="ess-card-title">{esc(a["title"])}</span>'
            f'<span class="ess-card-meta">{nice_date(a["publishOn"])} · {esc(a["readTime"])}</span></span></a>')


def list_page(published, head_links, nav, footer):
    cards = '\n        '.join(card(a) for a in published)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Essentials — Anly</title>
  <meta name="description" content="Short stories and tips about caring for the people you love from a distance, from the Anly app." />
  <link rel="canonical" href="{SITE}/essentials/" />
  <meta property="og:title" content="Anly Essentials" />
  <meta property="og:description" content="Short stories and tips about caring from a distance." />
  <meta property="og:url" content="{SITE}/essentials/" />
{head_links}
</head>
<body>

  {nav}

  <main>
    <section class="legal-hero">
      <div class="legal-hero-inner ess-head">
        <h1>Essentials</h1>
        <p class="legal-meta">Short stories and tips about caring from a distance. A new one every day in the Anly app.</p>
      </div>
    </section>

    <section class="ess-list">
      <div class="ess-grid" id="ess-grid">
        {cards}
      </div>
    </section>
  </main>

  {footer}

  <script>
  // Adds posts whose day has come since this page was built (one a day).
  (function () {{
    var grid = document.getElementById('ess-grid');
    var d = new Date();
    var today = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    var shown = {{}};
    grid.querySelectorAll('a.ess-card').forEach(function (a) {{ shown[a.getAttribute('href')] = true; }});
    var pages = {json.dumps({str(a['id']): page_name(a) for a in ALL})};
    fetch('../articles/essentials.json', {{cache: 'no-store'}}).then(function (r) {{ return r.json(); }}).then(function (f) {{
      f.articles.filter(function (a) {{ return a.publishOn <= today && pages[a.id] && !shown[pages[a.id]]; }})
        .sort(function (a, b) {{ return a.publishOn < b.publishOn ? -1 : 1; }})
        .forEach(function (a) {{
          var el = document.createElement('a');
          el.className = 'ess-card'; el.href = pages[a.id];
          if (a.hero) {{ var i = document.createElement('img'); i.src = a.hero; i.alt = ''; el.appendChild(i); }}
          else {{ var s = document.createElement('span'); s.className = 'ess-card-blank'; el.appendChild(s); }}
          var t = document.createElement('span'); t.className = 'ess-card-text';
          [['ess-card-tag', a.tag], ['ess-card-title', a.title], ['ess-card-meta', a.readTime]].forEach(function (p) {{
            var x = document.createElement('span'); x.className = p[0]; x.textContent = p[1]; t.appendChild(x);
          }});
          el.appendChild(t);
          grid.insertBefore(el, grid.firstChild);
        }});
    }}).catch(function () {{}});
  }})();
  </script>

</body>
</html>
'''


ALL = json.load(open(FEED, encoding='utf-8'))['articles']

if __name__ == '__main__':
    head_links, nav, footer = shared_parts()
    os.makedirs(OUT, exist_ok=True)
    keep = {'index.html'}
    for a in ALL:
        name = page_name(a)
        keep.add(name)
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(article_page(a, head_links, nav, footer))
    for f in os.listdir(OUT):  # pages of posts that left the feed
        if f.endswith('.html') and f not in keep:
            os.remove(os.path.join(OUT, f))
    today = datetime.date.today().isoformat()
    published = sorted((a for a in ALL if a['publishOn'] <= today), key=lambda a: (a['publishOn'], a['id']), reverse=True)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(list_page(published, head_links, nav, footer))
    print(f'{len(ALL)} article pages, {len(published)} on the list (published by {today})')
