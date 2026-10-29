"""Step 3: copy the built site into the GitHub repo folder (only the files the site uses).
usage: python -I assemble.py <src_dir> <site_dir> <repo_dir> <htaccess_template>
"""
import sys, os, json, shutil, re

SRC, SITE, REPO, HT = sys.argv[1:5]
URLS = json.load(open(os.path.join(SRC, "_urls.json")))
# every photo/asset path mentioned in the built pages and the Design components
REFS = set()
_texts = [os.path.join(r, f) for r, _, fs in os.walk(SITE) for f in fs if f == "index.html"]
_texts += [os.path.join(SRC, c + ".dc.html") for c in ("SiteHeader", "SiteFooter", "ServicePage", "DestinationPage")]
for _p in _texts:
    for _m in re.finditer(r"/(fotos|uploads|assets)/[^\"'\s)>,]+", open(_p, encoding="utf-8").read()):
        if "{{" not in _m.group(0): REFS.add(_m.group(0).split("?")[0])
missing = [r for r in REFS if not os.path.exists(os.path.join(SRC, r.lstrip("/")))]
if missing: raise SystemExit("missing files: " + ", ".join(sorted(missing)[:20]))

# remove previously built pages (keep .git, fotos/, README.md, FOTOS.md)
KEEP = {".git", "fotos", "tools", "README.md", "FOTOS.md"}
for f in os.listdir(REPO):
    if f in KEEP: continue
    p = os.path.join(REPO, f)
    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

# pages
for url in URLS.values():
    rel = url.strip("/")
    dst = os.path.join(REPO, rel)
    os.makedirs(dst, exist_ok=True)
    shutil.copy2(os.path.join(SITE, rel, "index.html"), os.path.join(dst, "index.html"))

# contact form handler
shutil.copy2(os.path.join(REPO, "tools", "extra", "send.php"), os.path.join(REPO, "contact", "send.php"))

# client presentation (not in Design, noindex, not in the sitemap)
os.makedirs(os.path.join(REPO, "presentation"), exist_ok=True)
shutil.copy2(os.path.join(REPO, "tools", "extra", "presentation", "index.html"), os.path.join(REPO, "presentation", "index.html"))

# runtime + components + search files
for f in ["support.js", "image-slot.js", ".image-slots.state.json", "SiteHeader.dc.html", "SiteFooter.dc.html",
          "ServicePage.dc.html", "DestinationPage.dc.html", "robots.txt", "sitemap.xml", "llms.txt"]:
    shutil.copy2(os.path.join(SRC, f), os.path.join(REPO, f))

# photos/assets that the pages use (fotos/ keeps everything already in the repo too)
n = 0
for r in REFS:
    s = os.path.join(SRC, r.lstrip("/")); d = os.path.join(REPO, r.lstrip("/"))
    if os.path.exists(s):
        os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(s, d); n += 1
print("files copied:", n)

# .htaccess: template + redirects from old Design file names
ht = open(HT, encoding="utf-8").read()
extra = "".join(f"RewriteRule ^{re.escape(k)}$ {v} [R=301,L]\n" for k, v in sorted(URLS.items()) if k != "Home.dc.html")
ht = ht.replace("RewriteRule ^Home\\.dc\\.html$ / [R=301,L]\n", "RewriteRule ^Home\\.dc\\.html$ / [R=301,L]\n" + extra)
open(os.path.join(REPO, ".htaccess"), "w", encoding="utf-8").write(ht)

# 404 page
open(os.path.join(REPO, "404.html"), "w", encoding="utf-8").write("""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found | DMC Seville Event</title><meta name="robots" content="noindex">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap" rel="stylesheet">
<style>body{margin:0;font-family:Montserrat,sans-serif;color:#0d3d40;background:#f6f8f8;display:flex;min-height:100vh;align-items:center;justify-content:center;text-align:center;padding:24px}
img{width:180px}h1{font-size:28px;margin:24px 0 8px}p{color:#3d4a50}a{color:#0d3d40;font-weight:600}nav a{display:inline-block;margin:6px 10px}</style></head>
<body><main><a href="/"><img src="/assets/dmc-logo-cropped.webp" alt="DMC Seville Event"></a>
<h1>Sorry, this page does not exist</h1><p>The page may have moved. These pages may help:</p>
<nav><a href="/">Home</a><a href="/incentive-trip-sevilla/">Incentive trips</a><a href="/group-travel-to-seville/">Group travel</a><a href="/inspiration/">Inspiration</a><a href="/contact/">Contact</a></nav></main></body></html>
""")

# README
open(os.path.join(REPO, "README.md"), "w", encoding="utf-8").write("""# DMC Seville Event – website (www.dmcsevilleevent.com)

Static website built from Claude Design ("WEB DMC SEVILLE EVENT") and published on Loading (Plesk) from this repository.

- Every page is pre-rendered HTML (`/<page>/index.html`) so Google, Bing and AI tools can read it without JavaScript.
  The Design template is kept inside `<template id="dc-src">`; `support.js` takes it over after load so menus, filters and pickers work.
- `fotos/` – web-ready photos (WebP, no GPS data). New photos go here first. `FOTOS.md` lists the raw links for Claude Design.
- `uploads/`, `assets/` – older photos and logos used by the pages (converted to WebP, max 1920 px).
- `.htaccess` – https + www, 301 redirects from the old WordPress addresses, 404 page.
- Do not edit the pages here by hand: make changes in Claude Design, download, and rebuild with Claude Code.
""")
print("done")
