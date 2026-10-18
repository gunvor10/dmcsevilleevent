# Rebuilding the site from a new Claude Design download

1. Unzip "WEB DMC SEVILLE EVENT.zip" into an empty scratch folder (EXPORT).
2. `python3 -m venv venv && venv/bin/pip install pillow beautifulsoup4`
3. `venv/bin/python -I tools/prep.py EXPORT SRC` – copies, converts photos to WebP, rewrites links to the clean URLs (URL map = SEO-LAUNCH-CHECKLIST.md table).
4. Serve SRC: `cd SRC && python3 -m http.server 8766 --bind 127.0.0.1`
5. `venv/bin/python -I tools/render.py SRC SITE 8766` – headless Chrome renders every page to SITE/<slug>/index.html (adds GA4 + consent banner + Search Console tag).
6. `venv/bin/python -I tools/assemble.py SRC SITE <this repo> tools/htaccess.txt` – copies pages + used photos into the repo, writes .htaccess (keeps tools/ itself? – copy tools back if assemble removed it).
7. Check, commit, push. Plesk (Loading) deploys automatically from GitHub.
