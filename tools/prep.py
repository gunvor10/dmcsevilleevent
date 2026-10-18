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
