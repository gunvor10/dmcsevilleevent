#!/usr/bin/env python3
"""Add Cloudflare Web Analytics (cookieless, no consent banner needed) to the pages in the repo
and save the token in tools/render.py, so future rebuilds from Claude Design keep it.

Usage:  python3 -I tools/add_cloudflare.py TOKEN [repo_dir]
Running it twice is safe (pages that already have the tag are skipped).
"""
import glob
import os
import re
import sys

MARK = "<!-- cloudflare-web-analytics -->"


def main():
    if len(sys.argv) < 2 or not re.fullmatch(r"[0-9a-f]{32}", sys.argv[1].strip()):
        sys.exit("Usage: add_cloudflare.py TOKEN [repo_dir]  (token = 32 characters, 0-9 a-f)")
    token = sys.argv[1].strip()
    root = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    tag = (MARK + "\n<script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
           "data-cf-beacon='{\"token\": \"" + token + "\"}'></script>\n")
    changed = 0
    pages = [p for p in glob.glob(os.path.join(root, "**", "*.html"), recursive=True)
             if os.sep + "tools" + os.sep not in p and not p.endswith(".dc.html")]
    for path in pages:
        text = open(path, encoding="utf-8").read()
        if MARK in text or "</head>" not in text:
            continue
        open(path, "w", encoding="utf-8").write(text.replace("</head>", tag + "</head>", 1))
        changed += 1
    render = os.path.join(root, "tools", "render.py")
    src = open(render, encoding="utf-8").read()
    src2 = re.sub(r'^CF_TOKEN = ".*"$', 'CF_TOKEN = "' + token + '"', src, count=1, flags=re.M)
    if src2 != src:
        open(render, "w", encoding="utf-8").write(src2)
    print(f"{changed} of {len(pages)} pages updated; render.py token {'saved' if src2 != src else 'unchanged'}")


if __name__ == "__main__":
    main()
