"""Step 2: pre-render every page with headless Chrome and write the static site.
usage: python -I render.py <src_dir> <site_dir> <port> [Only-This.dc.html ...]
Each page becomes /<slug>/index.html: full HTML (title, meta, JSON-LD, all text and <img>)
for search engines and AI tools, plus the original Design template in a <template>, which the
Design runtime takes over after load so menus, filters and pickers keep working.
"""
import sys, os, re, json, shutil, subprocess
from bs4 import BeautifulSoup

SRC, SITE, PORT = sys.argv[1], sys.argv[2], sys.argv[3]
ONLY = sys.argv[4:]
URLS = json.load(open(os.path.join(SRC, "_urls.json")))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MOBILE = {}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra", "mobile-header.py"), encoding="utf-8").read(), MOBILE)
RUNTIME_SCRIPTS = ("react", "support.js", "image-slot.js", "babel")

BOOT = """<script>
(function(){
  var t=document.getElementById('dc-src'), s=document.getElementById('dc-static');
  if(!t||!s) return;
  function load(src,cb){var e=document.createElement('script');e.src=src;e.onload=cb;document.body.appendChild(e);}
  function dedupe(){var seen={};document.querySelectorAll('script[type="application/ld+json"]').forEach(function(e){var k=e.textContent.trim();if(seen[k])e.remove();else seen[k]=1;});}
  function go(){
    s.parentNode.insertBefore(document.importNode(t.content,true), s.nextSibling);
    var obs=new MutationObserver(function(){var r=document.getElementById('dc-root');
      if(r&&r.firstElementChild){obs.disconnect();setTimeout(function(){s.remove();dedupe();setTimeout(dedupe,1500);},60);}});
    obs.observe(document.body,{childList:true,subtree:true});
    load('/image-slot.js',function(){load('/support.js');});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',go);else go();
})();
</script>"""

# Google Analytics 4 (same property as the old WordPress site) with Consent Mode:
# nothing is stored until the visitor accepts statistics cookies.
HEAD_EXTRA = """<meta name="google-site-verification" content="H0RdhqivH3abdaZlze3v44QQ5XISVadKqWreEA0e7PA">
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
var c=null;try{c=localStorage.getItem('dmc-consent');}catch(e){}
gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:c==='yes'?'granted':'denied'});
gtag('js',new Date());gtag('config','G-EN4YBPBV42');
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-EN4YBPBV42"></script>"""

CONSENT = """<div id="dmc-consent" hidden style="position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:560px;margin:0 auto;background:#0d3d40;color:#fff;font-family:Montserrat,sans-serif;font-size:14px;line-height:1.5;padding:16px 18px;border-radius:6px;box-shadow:0 6px 24px rgba(0,0,0,.25)">
We use Google Analytics cookies to see how visitors use our website. Do you accept statistics cookies? <a href="/privacy-policy/" style="color:#15cad2;text-decoration:underline">More info</a>
<div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap"><button type="button" data-v="yes" style="cursor:pointer;border:0;background:#15cad2;color:#0d3d40;font-weight:600;padding:8px 16px;border-radius:3px;font-family:inherit">Accept</button><button type="button" data-v="no" style="cursor:pointer;border:1px solid #fff;background:transparent;color:#fff;padding:8px 16px;border-radius:3px;font-family:inherit">Decline</button></div></div>
<script>
(function(){var b=document.getElementById('dmc-consent'),v=null;try{v=localStorage.getItem('dmc-consent');}catch(e){}
if(!v)b.hidden=false;
b.addEventListener('click',function(e){var x=e.target.getAttribute('data-v');if(!x)return;try{localStorage.setItem('dmc-consent',x);}catch(e){}
if(x==='yes')gtag('consent','update',{analytics_storage:'granted'});b.hidden=true;});
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-cookie-settings]');if(!a)return;e.preventDefault();
try{localStorage.removeItem('dmc-consent');}catch(x){}gtag('consent','update',{analytics_storage:'denied'});
document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();if(n.indexOf('_ga')===0)document.cookie=n+'=;Max-Age=0;path=/;domain=.dmcsevilleevent.com';});b.hidden=false;});})();
</script>"""

# Contact page: fill the form from the activity pickers (?activity=&guests=&time=), set the anti-robot time token,
# show error messages from send.php. Runs again when the Design runtime re-draws the page.
CONTACT_JS = """<script>
(function(){var q=new URLSearchParams(location.search),t0=Date.now(),done=new WeakSet();
var msg={fast:'Please take a moment to fill in the form and send it again.',limit:'You have already sent several requests. We will be in touch soon.',missing:'Please fill in all fields marked with *.',email:'Please check your e-mail address.',consent:'Please accept the privacy policy.',links:'Please remove web links from your message.',send:'Sorry, something went wrong. Please e-mail events@dmcsevilleevent.com or call +34 637 87 87 68.'};
function init(){var f=document.getElementById('dmc-enquiry');if(!f||done.has(f))return;done.add(f);
f.t.value=String(t0);f.page.value=location.href;
if(q.get('activity')&&!f.activity.value)f.activity.value=q.get('activity')+(q.get('time')?' ('+q.get('time')+')':'');
if(q.get('guests')&&!f.guests.value)f.guests.value=q.get('guests');
var e=q.get('error');if(e&&msg[e]&&!f.querySelector('.dmc-err')){var d=document.createElement('p');d.className='dmc-err';d.textContent=msg[e];d.style.cssText='grid-column:1/-1;background:#fbeaea;color:#8a1c1c;padding:10px 14px;margin:0;border-radius:2px';f.insertBefore(d,f.firstChild);}}
init();new MutationObserver(init).observe(document.body,{childList:true,subtree:true});})();
</script>"""
THANKS_JS = """<script>gtag('event','generate_lead',{event_category:'contact',event_label:'website form'});</script>"""

def source_blocks(page_text):
    m1 = re.search(r"<x-dc(?:\s[^>]*)?>.*</x-dc>", page_text, re.S)
    m2 = re.search(r'<script type="text/x-dc" data-dc-script[^>]*>.*?</script>', page_text, re.S)
    xdc = m1.group(0) if m1 else ""
    xdc = re.sub(r'<script src="/image-slot\.js"></script>', "", xdc)
    return xdc + "\n" + (m2.group(0) if m2 else "")

RADIUS = {"rect": "0", "circle": "50%", "pill": "9999px"}

def slot_to_img(soup, slot, idx):
    src = slot.get("src", "")
    style = slot.get("style", "")
    shape = slot.get("shape", "rounded")
    rad = RADIUS.get(shape, (slot.get("radius") or "12") + "px")
    if not src or "{{" in src:
        div = soup.new_tag("div", style=style + ";background:#e9eeee;border-radius:" + rad)
        slot.replace_with(div); return False
    fit = "contain" if (slot.get("fit") or "cover").lower() == "contain" else "cover"
    img = soup.new_tag("img", src=src, alt=slot.get("alt") or slot.get("placeholder") or "")
    img["style"] = style + ";display:block;object-fit:" + fit + ";border-radius:" + rad
    img["decoding"] = "async"
    if idx == 0:
        img["fetchpriority"] = "high"
    else:
        img["loading"] = "lazy"
    slot.replace_with(img); return True

def build(name, url):
    page_text = open(os.path.join(SRC, name), encoding="utf-8").read()
    dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                          "--virtual-time-budget=15000", "--window-size=1366,900", "--dump-dom",
                          f"http://127.0.0.1:{PORT}/{name}"], capture_output=True, text=True, timeout=180).stdout
    soup = BeautifulSoup(dom, "html.parser")
    root = soup.find(id="dc-root")
    if not root or not root.get_text(strip=True):
        raise SystemExit(f"{name}: page did not render")
    for s in soup.find_all("script"):
        src = s.get("src", "")
        if s.get("type") == "text/x-dc" or s.has_attr("data-dc-script") or any(k in src for k in RUNTIME_SCRIPTS):
            s.decompose()
    for x in soup.find_all("x-dc"):
        x.decompose()
    # SEO tags: one of each, all in <head>. Prefer the page's own head tags; template copies
    # (data-dc-tpl) are used only when the page has none, and are moved into <head>.
    def seo_key(el):
        if el.name == "title": return ("title",)
        if el.name == "meta" and (el.get("name") in ("description", "robots", "twitter:card") or el.get("property")):
            return ("meta", el.get("name"), el.get("property"))
        if el.name == "link" and "canonical" in (el.get("rel") or []): return ("canonical",)
        return None
    tags = [(seo_key(el), el) for el in soup.find_all(["title", "meta", "link"]) if seo_key(el)]
    best = {}
    for k, el in tags:
        if k not in best or (best[k].has_attr("data-dc-tpl") and not el.has_attr("data-dc-tpl")):
            best[k] = el
    keep = set(id(e) for e in best.values())
    for k, el in tags:
        if id(el) not in keep: el.decompose()
    for el in best.values():
        if el.has_attr("data-dc-tpl"): del el["data-dc-tpl"]
        if el.find_parent("head") is None:
            soup.head.append(el.extract())
    root["id"] = "dc-static"
    n = 0
    for el in list(soup.find_all(["image-slot", "img"])):
        if el.name == "image-slot":
            if slot_to_img(soup, el, n): n += 1
        else:
            if n == 0: el["fetchpriority"] = "high"
            elif not el.get("loading"): el["loading"] = "lazy"
            n += 1
    head = soup.head
    head.insert(0, BeautifulSoup('<base href="/">', "html.parser"))
    head.append(BeautifulSoup("<style>x-dc{display:none!important}</style>", "html.parser"))
    head.append(BeautifulSoup(HEAD_EXTRA, "html.parser"))
    head.append(BeautifulSoup(MOBILE["CSS"], "html.parser"))
    tpl = soup.new_tag("template", id="dc-src")
    root.insert_after(tpl)
    html = str(soup)
    html = html.replace('<template id="dc-src"></template>',
                        '<template id="dc-src">' + source_blocks(page_text) + "</template>\n" + CONSENT + "\n" + MOBILE["JS"] + "\n" + BOOT
                        + (CONTACT_JS if url == "/contact/" else "") + (THANKS_JS if url == "/contact/thank-you/" else ""), 1)
    if not html.lstrip().lower().startswith("<!doctype"):
        html = "<!DOCTYPE html>\n" + html
    out_dir = os.path.join(SITE, url.strip("/"))
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(html)
    text_len = len(root.get_text(" ", strip=True))
    print(f"{name:42} -> {url:62} text {text_len:6} chars, images {n}")

pages = ONLY or list(URLS)
for name in pages:
    build(name, URLS[name])
