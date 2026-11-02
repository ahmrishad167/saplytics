"""Build the SAPlytics blog from _posts-src/*.html.

Each source file starts with a JSON block between <!--meta and -->, followed by
the article body HTML. Run:  python _tools/build_blog.py
It writes blog/<slug>/index.html, blog/index.html and sitemap.xml.
Posts with "status": "draft" get a page (for review) but stay out of the
blog index and the sitemap.
"""
import json, re, os, html, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://ahmrishad167.github.io/saplytics/'
LINKEDIN = 'https://www.linkedin.com/in/md-rishad-ahmed-8633b5231'
CAL = 'https://calendly.com/saplytics/30min'

HEAD = '''<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<meta name="author" content="Rishad Ahmed">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0B1A33">
<link rel="icon" type="image/svg+xml" href="{up}assets/saplytics-badge-dark.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{up}assets/favicon-32.png">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="SAPlytics">
<meta property="og:locale" content="en_CA">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{ogtitle}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{base}og-image.png">
<script type="application/ld+json">
{ld}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/blog.css">
</head>
<body>
<a href="#main" class="skip">Skip to content</a>
<header class="bar">
  <div class="wrap">
    <a href="{up}" class="wm" aria-label="SAPlytics home"><img src="{up}assets/saplytics-badge-dark.svg" alt="SAPlytics" width="64" height="64"></a>
    <p class="tagline">For Distributors and Manufacturers Running SAP Business One</p>
    <nav aria-label="Primary">
      <a href="{up}#services">Services</a>
      <a href="{up}#work">Case Studies</a>
      <a href="{up}#about">About</a>
      <a href="{up}#faq">FAQ</a>
      <a href="{up}#contact">Contact</a>
      <a href="{up}blog/"{blogcur}>Blog</a>
    </nav>
    <a class="btn" href="{cal}" target="_blank" rel="noopener">Free Review</a>
  </div>
</header>
<main id="main">
'''

FOOT = '''</main>
<footer>
  <div class="wrap">
    <div class="f-brand">
      <a href="{up}" aria-label="SAPlytics home"><img src="{up}assets/saplytics-badge-dark.svg" alt="SAPlytics" width="72" height="72"></a>
      <p class="f-tag">Your ERP Knows Everything. <span>Your Reports Should Too.</span></p>
    </div>
    <span class="f-copy">© 2026 Rishad Ahmed</span>
  </div>
</footer>
</body>
</html>
'''

CTA = '''<aside class="a-cta">
  <h2>Numbers Off? <span>Let's Fix Them</span></h2>
  <p>Book a free 30-minute review. Show me the SAP report that doesn't match, and I'll show you why, on your own screens.</p>
  <div class="row">
    <a class="btn" href="{cal}" target="_blank" rel="noopener">Book a Free 30-Min Review</a>
    <a class="btn ghost" href="mailto:ahm.rishad@outlook.com?subject=SAPlytics%20Enquiry">Email Me</a>
  </div>
</aside>
'''


def human_date(d):
    y, m, dd = d.split('-')
    months = 'January February March April May June July August September October November December'.split()
    return '%s %d, %s' % (months[int(m) - 1], int(dd), y)


def load_posts():
    posts = []
    for path in sorted(glob.glob(os.path.join(ROOT, '_posts-src', '*.html'))):
        raw = open(path, encoding='utf-8').read()
        m = re.match(r'\s*<!--meta\s*(\{.*?\})\s*-->\s*(.*)', raw, flags=re.S)
        meta = json.loads(m.group(1))
        meta['body'] = m.group(2).strip()
        meta['words'] = len(re.sub(r'<[^>]+>', ' ', meta['body']).split())
        posts.append(meta)
    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts


def build_post(p):
    url = BASE + 'blog/%s/' % p['slug']
    up = '../../'
    draft = p.get('status') == 'draft'
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BlogPosting", "headline": p['title'], "description": p['description'],
         "datePublished": p['date'], "dateModified": p.get('updated', p['date']),
         "inLanguage": "en-CA", "mainEntityOfPage": url, "image": BASE + "og-image.png",
         "wordCount": p['words'], "keywords": p.get('keywords', ''),
         "author": {"@type": "Person", "name": "Rishad Ahmed", "url": BASE + "#about", "sameAs": [LINKEDIN]},
         "publisher": {"@type": "Organization", "name": "SAPlytics", "logo": {"@type": "ImageObject", "url": BASE + "assets/icon-512.png"}}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": BASE + "blog/"},
            {"@type": "ListItem", "position": 3, "name": p['title'], "item": url}]}]}
    page = HEAD.format(title=html.escape(p['seo_title']), desc=html.escape(p['description']), url=url, up=up, base=BASE,
                       ogtype='article', ogtitle=html.escape(p['title']), robots='noindex' if draft else 'index, follow, max-image-preview:large',
                       ld=json.dumps(ld, ensure_ascii=False, indent=1), blogcur=' aria-current="page"', cal=CAL)
    mins = max(1, round(p['words'] / 220))
    page += '''<div class="wrap">
<article>
  <p class="crumb"><a href="{up}">Home</a> · <a href="{up}blog/">Blog</a></p>
  <header class="a-head">
    <p class="k">{kicker}</p>
    <h1>{title}</h1>
    <p class="lede">{lede}</p>
    <p class="by"><img src="{up}assets/rishad-ahmed.jpg" alt="" width="44" height="44"><span><b>Rishad Ahmed</b> · {date} · {mins} min read</span></p>
  </header>
  <div class="prose">
{body}
  </div>
{cta}</article>
</div>
'''.format(up=up, kicker=p['kicker'], title=html.escape(p['title']), lede=p['lede'], date=human_date(p['date']),
           mins=mins, body=p['body'], cta=CTA.format(cal=CAL))
    page += FOOT.format(up=up)
    out = os.path.join(ROOT, 'blog', p['slug'])
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)


def build_index(posts):
    live = [p for p in posts if p.get('status') != 'draft' or os.environ.get('BLOG_PREVIEW')]
    url = BASE + 'blog/'
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "SAPlytics Blog", "url": url, "inLanguage": "en-CA",
          "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "url": BASE + 'blog/%s/' % p['slug'],
                        "datePublished": p['date']} for p in live]}
    page = HEAD.format(title='SAP Business One Reporting Blog | SAPlytics',
                       desc='Practical articles on SAP Business One reporting, Power BI, Excel automation, inventory planning and trade data for distributors and manufacturers.',
                       url=url, up='../', base=BASE, ogtype='website', ogtitle='SAPlytics Blog',
                       robots='index, follow', ld=json.dumps(ld, ensure_ascii=False, indent=1), blogcur=' aria-current="page"', cal=CAL)
    cards = ''.join('''    <li><a href="{slug}/">
      <span class="k">{kicker} · {date}</span>
      <h2>{title}</h2>
      <p>{desc}</p>
      <span class="more">Read the Article →</span>
    </a></li>
'''.format(slug=p['slug'], kicker=p['kicker'], date=human_date(p['date']), title=html.escape(p['title']),
           desc=html.escape(p['description'])) for p in live)
    page += '''<div class="wrap">
  <header class="b-head">
    <h1>SAP Business One <span>Reporting Blog</span></h1>
    <p>Practical fixes for SAP B1 reports, Power BI and Excel, written for owners, controllers and the people who run the numbers.</p>
  </header>
  <ul class="posts">
{cards}  </ul>
</div>
'''.format(cards=cards or '    <li><p>New articles are on the way.</p></li>\n')
    page += FOOT.format(up='../')
    os.makedirs(os.path.join(ROOT, 'blog'), exist_ok=True)
    open(os.path.join(ROOT, 'blog', 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    return live


def build_sitemap(live):
    rows = ['  <url><loc>%s</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>' % BASE]
    if live:
        rows.append('  <url><loc>%sblog/</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>' % (BASE, live[0]['date']))
    for p in live:
        rows.append('  <url><loc>%sblog/%s/</loc><lastmod>%s</lastmod><priority>0.7</priority></url>' % (BASE, p['slug'], p.get('updated', p['date'])))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % '\n'.join(rows)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(xml)


if __name__ == '__main__':
    posts = load_posts()
    for p in posts:
        build_post(p)
    live = build_index(posts)
    build_sitemap([p for p in live if p.get('status') != 'draft'])
    print('built %d posts (%d live, %d draft)' % (len(posts), len(live), len(posts) - len(live)))
