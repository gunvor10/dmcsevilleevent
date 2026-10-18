# DMC Seville Event – website (www.dmcsevilleevent.com)

Static website built from Claude Design ("WEB DMC SEVILLE EVENT") and published on Loading (Plesk) from this repository.

- Every page is pre-rendered HTML (`/<page>/index.html`) so Google, Bing and AI tools can read it without JavaScript.
  The Design template is kept inside `<template id="dc-src">`; `support.js` takes it over after load so menus, filters and pickers work.
- `fotos/` – web-ready photos (WebP, no GPS data). New photos go here first. `FOTOS.md` lists the raw links for Claude Design.
- `uploads/`, `assets/` – older photos and logos used by the pages (converted to WebP, max 1920 px).
- `.htaccess` – https + www, 301 redirects from the old WordPress addresses, 404 page.
- Do not edit the pages here by hand: make changes in Claude Design, download, and rebuild with Claude Code.
