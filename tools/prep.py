"""Step 1: copy the Design export into src/, optimise images, rewrite links to the canonical URLs.
usage: python -I prep.py <export_dir> <src_dir>
"""
import sys, os, re, json, shutil, base64, io
from PIL import Image, ImageOps

EXP, SRC = sys.argv[1], sys.argv[2]
if os.path.exists(SRC):
    shutil.rmtree(SRC)
shutil.copytree(EXP, SRC, ignore=shutil.ignore_patterns("screenshots", ".DS_Store"))

# ---- page -> URL map (from SEO-LAUNCH-CHECKLIST.md) ----
URLS = {}
for line in open(os.path.join(SRC, "SEO-LAUNCH-CHECKLIST.md"), encoding="utf-8"):
    m = re.match(r"\|\s*([A-Za-z0-9-]+\.dc\.html)\s*\|\s*(/[^|\s]*)\s*\|", line)
    if m:
        URLS[m.group(1)] = m.group(2)
# ---- extra pages/blocks not (yet) in Design: legal pages, thank-you page, contact form, footer links ----
EXTRA = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra")
ns = {}
exec(open(os.path.join(EXTRA, "legal-pages.py"), encoding="utf-8").read(), ns)
for name, d in ns["PAGES"].items():
    if not os.path.exists(os.path.join(SRC, name)):
        open(os.path.join(SRC, name), "w", encoding="utf-8").write(ns["page"](name, d))
        URLS[name] = d["url"]
        if not d.get("noindex"):
            sm = os.path.join(SRC, "sitemap.xml"); t = open(sm, encoding="utf-8").read()
            if d["url"] not in t:
                t = t.replace("</urlset>", f"  <url>\n    <loc>https://www.dmcsevilleevent.com{d['url']}</loc>\n  </url>\n</urlset>")
                open(sm, "w", encoding="utf-8").write(t)
cp = os.path.join(SRC, "Contact.dc.html"); t = open(cp, encoding="utf-8").read()
if "dmc-enquiry" not in t and "<form" not in t:
    form = open(os.path.join(EXTRA, "contact-form.html"), encoding="utf-8").read()
    t = t.replace('  <dc-import name="SiteFooter"', form + '  <dc-import name="SiteFooter"', 1)
    open(cp, "w", encoding="utf-8").write(t); print("contact form added")
fp = os.path.join(SRC, "SiteFooter.dc.html"); t = open(fp, encoding="utf-8").read()
if "/privacy-policy/" not in t:
    t = t.replace("All Rights Reserved.", 'All Rights Reserved. · <a href="/privacy-policy/" style="color:inherit;">Privacy &amp; Cookies</a> · <a href="/legal-notice/" style="color:inherit;">Legal Notice</a>', 1)
    open(fp, "w", encoding="utf-8").write(t); print("footer legal links added")
json.dump(URLS, open(os.path.join(SRC, "_urls.json"), "w"), indent=1)
print("pages in URL map:", len(URLS))

TEXT_EXT = (".html", ".js", ".json", ".xml", ".txt", ".md")
def text_files():
    for root, _, files in os.walk(SRC):
        for f in files:
            if f.endswith(TEXT_EXT) and f != ".image-slots.state.json":
                yield os.path.join(root, f)

# ---- 1. dropped image stored in the image-slot sidecar -> real file ----
state_p = os.path.join(SRC, ".image-slots.state.json")
state = json.load(open(state_p))
baked = {}
for slot, v in state.items():
    u = v.get("u", "")
    if u.startswith("data:image"):
        raw = base64.b64decode(u.split(",", 1)[1])
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        im.thumbnail((1920, 1920), Image.LANCZOS)
        name = f"uploads/slot-{slot}.webp"
        im.save(os.path.join(SRC, name), "WEBP", quality=82, method=6)
        baked[slot] = "./" + name
json.dump({}, open(state_p, "w"))
for p in text_files():
    if not p.endswith(".dc.html"):
        continue
    t = open(p, encoding="utf-8").read(); o = t
    for slot, src in baked.items():
        def fix(m):
            tag = m.group(0)
            if ' src="' in tag:
                return re.sub(r' src="[^"]*"', f' src="{src}"', tag)
            return tag.replace("<image-slot", f'<image-slot src="{src}"', 1)
        t = re.sub(r'<image-slot[^>]*\bid="' + re.escape(slot) + r'"[^>]*>', fix, t)
    if t != o:
        open(p, "w", encoding="utf-8").write(t); print("baked slot image into", os.path.basename(p))

# ---- 2. optimise images in uploads/ and assets/ (jpg/png -> webp, max 1920 px) ----
renames = {}
for folder in ("uploads", "assets"):
    for f in os.listdir(os.path.join(SRC, folder)):
        p = os.path.join(SRC, folder, f)
        base, ext = os.path.splitext(f)
        if ext.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        if folder == "assets" and os.path.getsize(p) < 150_000:
            continue  # small logos stay as they are
        im = ImageOps.exif_transpose(Image.open(p))
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        im.thumbnail((1920, 1920), Image.LANCZOS)
        out = os.path.join(SRC, folder, base + ".webp")
        if os.path.exists(out) and out != p:
            out = os.path.join(SRC, folder, base + "-" + ext.lower().strip(".") + ".webp")
        for q in (82, 76, 70, 64):
            im.save(out, "WEBP", quality=q, method=6)
            if os.path.getsize(out) <= 300_000:
                break
        os.remove(p)
        renames[f"{folder}/{f}"] = f"{folder}/{os.path.basename(out)}"
print("images converted:", len(renames))

# ---- 3. rewrite references in all text files ----
def page_url(name, rest=""):
    return URLS.get(name, "/") + rest

n_links = 0
for p in text_files():
    t = open(p, encoding="utf-8").read(); o = t
    for a, b in renames.items():
        t = t.replace(a, b)
    # links between pages: ./Name.dc.html(?query)(#hash) -> /canonical/
    def link(m):
        global n_links
        n_links += 1
        return page_url(m.group(1))
    t = re.sub(r"\./([A-Za-z0-9-]+\.dc\.html)(?=[\"'?#\s)])", link, t)
    # files: make root-relative so they work from every URL
    t = re.sub(r"(?<![A-Za-z0-9_/.])\./(fotos|uploads|assets)/", r"/\1/", t)
    t = t.replace('src="./support.js"', 'src="/support.js"').replace('src="./image-slot.js"', 'src="/image-slot.js"')
    if t != o:
        open(p, "w", encoding="utf-8").write(t)
print("page links rewritten:", n_links)
json.dump(renames, open(os.path.join(SRC, "_renames.json"), "w"), indent=1)

# ---- 4. mobile burger menu + menu link fixes (after links are rewritten to clean URLs) ----
mh = {}
exec(open(os.path.join(EXTRA, "mobile-header.py"), encoding="utf-8").read(), mh)
hp = os.path.join(SRC, "SiteHeader.dc.html"); t = open(hp, encoding="utf-8").read()
t2, changed = mh["apply"](t)
if changed:
    open(hp, "w", encoding="utf-8").write(t2); print("mobile burger menu added to header")

# ---- 5. DMC's own social profiles (Design still links the Sevilla Private Guide ones) ----
SOCIAL = {
    "https://www.facebook.com/Sevillaprivateguidegunvor/": "https://www.facebook.com/dmcsevilleevent/",
    "https://www.instagram.com/sevillaprivateguide_gunvor/": "https://www.instagram.com/dmcsevilleevent/",
}
n = 0
for p in text_files():
    t = open(p, encoding="utf-8").read(); o = t
    for a, b in SOCIAL.items():
        t = t.replace(a, b)
    if t != o:
        open(p, "w", encoding="utf-8").write(t); n += 1
print("social links updated in", n, "files")
