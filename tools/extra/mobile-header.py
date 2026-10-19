"""Mobile header with burger menu + menu link fixes, applied to SiteHeader.dc.html by prep.py.
Desktop look is unchanged. Below 900 px: the turquoise top bar is hidden, the logo is smaller,
and the menu opens from a burger button (CSS + a small script in render.py toggles html.nav-open).
Skipped automatically if a future Design download already has its own burger menu.
"""

def apply(t):
    if "data-nav-toggle" in t or "burger" in t.lower():
        return t, False
    # sub-items of Team Building pointed at the Team Building page instead of their own pages
    t = t.replace('<a href="/trip/team-building-seville/" style="color:#5a6b70;padding:4px 10px 4px 22px;border-radius:4px;font-size:13px;">Treasure Hunt in Seville</a>',
                  '<a href="/treasure-hunt-in-seville/" style="color:#5a6b70;padding:4px 10px 4px 22px;border-radius:4px;font-size:13px;">Treasure Hunt in Seville</a>')
    t = t.replace('<a href="/trip/team-building-seville/" style="color:#5a6b70;padding:4px 10px 4px 22px;border-radius:4px;font-size:13px;">Movie Making in Seville</a>',
                  '<a href="/movie-making-in-seville/" style="color:#5a6b70;padding:4px 10px 4px 22px;border-radius:4px;font-size:13px;">Movie Making in Seville</a>')
    t = t.replace('<a href="/trip/team-building-seville/" style="color:#5a6b70;padding:4px 10px 8px 22px;border-radius:4px;font-size:13px;">Painting Team Building</a>',
                  '<a href="/painting-team-building-in-seville/" style="color:#5a6b70;padding:4px 10px 8px 22px;border-radius:4px;font-size:13px;">Painting Team Building</a>')
    # mark the parts so the mobile CSS can find them
    t = t.replace('<div style="background:#15cad2;color:#ffffff;font-family:\'Varela Round\'', '<div data-nav="topbar" style="background:#15cad2;color:#ffffff;font-family:\'Varela Round\'', 1)
    t = t.replace('<header style="display:flex;', '<header data-nav="bar" style="position:relative;display:flex;', 1)
    burger = ('<button type="button" data-nav-toggle="1" aria-label="Menu" style="display:none;background:none;border:0;cursor:pointer;'
              'padding:8px;margin-left:auto;flex-direction:column;gap:5px;">'
              '<span style="display:block;width:26px;height:3px;background:#0d3d40;border-radius:2px;"></span>'
              '<span style="display:block;width:26px;height:3px;background:#0d3d40;border-radius:2px;"></span>'
              '<span style="display:block;width:26px;height:3px;background:#0d3d40;border-radius:2px;"></span></button>\n    ')
    t = t.replace('<nav style="display:flex;', burger + '<nav data-nav="menu" style="display:flex;', 1)
    return t, True

CSS = """<style id="dmc-mobile-nav">
@media (max-width:900px){
  [data-nav="topbar"]{display:none!important}
  header[data-nav="bar"]{padding:10px 18px!important;flex-wrap:nowrap!important}
  header[data-nav="bar"] img{height:50px!important}
  [data-nav-toggle]{display:flex!important}
  nav[data-nav="menu"]{display:none!important;position:absolute;top:100%;left:0;right:0;z-index:60;background:#ffffff;
    flex-direction:column!important;align-items:stretch!important;gap:0!important;padding:4px 18px 18px;
    box-shadow:0 12px 24px rgba(0,0,0,.12);max-height:calc(100vh - 80px);overflow-y:auto}
  html.nav-open nav[data-nav="menu"]{display:flex!important}
  nav[data-nav="menu"]>div,nav[data-nav="menu"]>a{padding:14px 2px;border-bottom:1px solid #edf1f1;font-size:16px!important}
  nav[data-nav="menu"]>div>button{font-size:16px!important;width:100%;text-align:left!important}
  nav[data-nav="menu"]>div>div{position:static!important;box-shadow:none!important;min-width:0!important;
    grid-template-columns:1fr!important;padding:6px 0 0 8px!important}
}
/* Phones: Design's fixed side-by-side layouts (text + photo, numbered lists) stack in one column,
   4-photo galleries become 2 x 2, wide card grids become one card per row. */
@media (max-width:760px){
  [style*="minmax(0px, 1fr) minmax(0px, 0.8fr)"],[style*="minmax(0px, 0.8fr) minmax(0px, 1fr)"],
  [style*="minmax(0px, 1.3fr) minmax(0px, 0.9fr)"],[style*="minmax(0px, 0.8fr) minmax(0px, 1.2fr)"],
  [style*="minmax(0px, 1fr) minmax(0px, 1fr)"],[style*="minmax(0px, 1fr) 320px"],
  [style*="minmax(0,1fr) minmax(0,0.8fr)"],[style*="minmax(0,0.8fr) minmax(0,1fr)"],
  [style*="minmax(0,1.3fr) minmax(0,0.9fr)"],[style*="minmax(0,0.8fr) minmax(0,1.2fr)"],
  [style*="minmax(0,1fr) minmax(0,1fr)"],[style*="minmax(0,1fr) 320px"],
  [style*="grid-template-columns: 1fr 1fr"],[style*="grid-template-columns:1fr 1fr"],
  [style*="repeat(2, minmax(0px, 1fr))"],[style*="repeat(2,minmax(0,1fr))"],
  [style*="minmax(340px"],[style*="minmax(280px"],[style*="minmax(260px"]{
    grid-template-columns:minmax(0,1fr)!important;gap:28px!important}
  [style*="repeat(4, minmax(0px, 1fr))"],[style*="repeat(4,minmax(0,1fr))"],
  [style*="repeat(4, 1fr)"],[style*="repeat(4,1fr)"],[style*="repeat(3, 1fr)"],[style*="repeat(3,1fr)"]{
    grid-template-columns:repeat(2,minmax(0,1fr))!important}
  section[style*="padding"]{padding-left:20px!important;padding-right:20px!important}
  /* destination pages: day-by-day programme (photo beside text) */
  div:has(> div[style*="height: 160px"][style*="flex: 0 0 auto"]),div:has(> div[style*="height:160px"][style*="flex:none"]){flex-direction:column!important;gap:16px!important}
  div[style*="height: 160px"][style*="flex: 0 0 auto"],div[style*="height:160px"][style*="flex:none"]{width:100%!important;height:190px!important}
  div[style*="padding: 30px 34px"]{padding:22px 18px!important}
  /* groups page: service cards (photo beside text) */
  :has(> [style*="width: 38%"]),:has(> [style*="width:38%"]){flex-direction:column!important}
  [style*="width: 38%"],[style*="width:38%"]{width:100%!important;height:200px!important}
}
</style>"""

JS = """<script>
document.addEventListener('click',function(e){
  var b=e.target.closest&&e.target.closest('[data-nav-toggle]');
  if(b){document.documentElement.classList.toggle('nav-open');return;}
  if(e.target.closest&&e.target.closest('nav[data-nav="menu"] a'))document.documentElement.classList.remove('nav-open');
});
</script>"""
