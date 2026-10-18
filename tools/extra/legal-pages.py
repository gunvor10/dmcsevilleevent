"""Extra pages that are not (yet) in Claude Design: privacy & cookie policy, legal notice, contact thank-you page.
Imported by prep.py, which writes them as .dc.html pages in the same style as the Travel Guarantee page.
Company facts: Come to Spain Events SLU, NIF B90380494 (as on supplier invoices), tourism licence 41-7397-2.
"""

UPDATED = "19 October 2026"
P = 'font-weight:300;font-size:16px;line-height:1.85;color:#3d4a50;margin:0 0 16px;'
H2 = "font-family:'Montserrat',sans-serif;font-weight:800;font-size:clamp(19px,2.4vw,23px);margin:36px 0 12px;color:#0d3d40;"
LI = 'font-weight:300;font-size:16px;line-height:1.8;color:#3d4a50;margin:0 0 6px;'
A = 'color:#0d3d40;font-weight:600;text-decoration:underline;'

def p(t): return f'<p style="{P}">{t}</p>'
def h(t): return f'<h2 style="{H2}">{t}</h2>'
def ul(*items): return '<ul style="margin:0 0 16px;padding-left:22px;">' + "".join(f'<li style="{LI}">{i}</li>' for i in items) + "</ul>"

COMPANY = ul(
    "<b>Company:</b> Come to Spain Events SLU (trading as DMC Seville Event)",
    "<b>NIF / VAT:</b> B90380494",
    "<b>Address:</b> C/ Milano Govinda 35, 41020 Sevilla, Spain",
    '<b>E-mail:</b> <a style="' + A + '" href="mailto:events@dmcsevilleevent.com">events@dmcsevilleevent.com</a> · <b>Phone:</b> +34 637 87 87 68',
    "<b>Tourism licence (travel agency):</b> 41-7397-2",
)

PAGES = {
 "Privacy-Policy.dc.html": dict(
  url="/privacy-policy/", title="Privacy & Cookie Policy | DMC Seville Event", label="YOUR DATA",
  h1="Privacy &amp; Cookie Policy",
  desc="How DMC Seville Event (Come to Spain Events SLU) handles personal data from enquiries, bookings and website statistics, and which cookies we use.",
  body=p(f"Last updated: {UPDATED}") + h("Who is responsible for your data") + COMPANY
   + h("What data we collect and why")
   + ul("<b>Enquiries</b> (contact form, e-mail, phone or WhatsApp): name, company, e-mail, phone and the details of your event, to answer your request and prepare a proposal. Legal basis: your consent and steps prior to a contract (GDPR art. 6.1.a and 6.1.b).",
        "<b>Bookings</b>: names of participants, dietary needs, travel details and invoicing data, to organise your programme and meet our legal and tax obligations (GDPR art. 6.1.b and 6.1.c).",
        "<b>Website statistics</b>: Google Analytics, only if you accept statistics cookies (GDPR art. 6.1.a).")
   + h("Who we share data with")
   + p("We only share what is needed to deliver your event: hotels, venues, restaurants, transport companies, guides and other suppliers you have booked through us. Our website and e-mail are hosted by Loading (Spain). Google Analytics is provided by Google Ireland Ltd; Google may process data in the USA under the EU–US Data Privacy Framework. We never sell your data.")
   + h("How long we keep it")
   + p("Enquiries that do not lead to a booking are deleted after two years. Booking and invoicing data are kept for as long as Spanish tax and commercial law requires (normally six years).")
   + h("Your rights")
   + p('You can ask for access, correction, deletion, restriction, portability or object to the use of your data, and withdraw your consent at any time, by writing to <a style="' + A + '" href="mailto:events@dmcsevilleevent.com">events@dmcsevilleevent.com</a>. If you are not satisfied with our answer you can complain to the Spanish Data Protection Agency (<a style="' + A + '" href="https://www.aepd.es" rel="noopener">www.aepd.es</a>).')
   + h("Cookies")
   + p("We only use statistics cookies if you accept them in the banner. Without your consent, Google Analytics runs in a privacy mode without cookies.")
   + ul("<b>dmc-consent</b> (your browser's local storage, no expiry): remembers whether you accepted or declined statistics cookies.",
        "<b>_ga, _ga_EN4YBPBV42</b> (Google Analytics, 2 years): count visits and show us which pages are useful. Only set after you accept.")
   + p("The website also loads fonts from Google Fonts, which means your IP address is sent to Google when a page opens.")
   + p('<a href="#" data-cookie-settings="1" style="' + A + '">Change your cookie choice</a>'),
 ),
 "Legal-Notice.dc.html": dict(
  url="/legal-notice/", title="Legal Notice | DMC Seville Event", label="AVISO LEGAL",
  h1="Legal Notice",
  desc="Legal notice (aviso legal) for www.dmcsevilleevent.com: company details of Come to Spain Events SLU, conditions of use and intellectual property.",
  body=p(f"Last updated: {UPDATED}") + p("In accordance with Spanish Law 34/2002 on Information Society Services and Electronic Commerce (LSSI-CE), we provide the following information about the owner of this website:") + COMPANY
   + h("Purpose of the website")
   + p("This website presents the destination management services of DMC Seville Event: meetings, incentive trips, events, team building and group travel in Seville and Andalusia. Prices and programmes shown are indicative; a booking is only confirmed by a written proposal and agreement.")
   + h("Conditions of use")
   + p("By using this website you agree to use it lawfully. We do our best to keep the information correct and up to date, but we cannot guarantee that it is free of errors, and we are not responsible for the content of external websites we link to.")
   + h("Intellectual property")
   + p("Texts, photos, logos and design on this website belong to Come to Spain Events SLU or are used with permission. They may not be copied or used commercially without our written consent.")
   + h("Privacy and cookies")
   + p('How we handle personal data and cookies is explained in our <a style="' + A + '" href="/privacy-policy/">Privacy &amp; Cookie Policy</a>.')
   + h("Applicable law")
   + p("These conditions are governed by Spanish law. For any dispute, the courts of Seville shall have jurisdiction, unless the law gives consumers the right to go to the courts of their place of residence."),
 ),
 "Thank-You.dc.html": dict(
  url="/contact/thank-you/", title="Thank You | DMC Seville Event", label="MESSAGE SENT", noindex=True,
  h1="Thank You for Your Request",
  desc="Thank you for contacting DMC Seville Event.",
  body=p("We have received your message and will reply within one working day, usually much sooner.")
   + p('If it is urgent, call or WhatsApp Gunvor on <a style="' + A + '" href="tel:+34637878768">+34 637 87 87 68</a>.')
   + p('<a style="' + A + '" href="/inspiration/">Get inspired while you wait →</a>'),
 ),
}

def page(name, d):
    url = "https://www.dmcsevilleevent.com" + d["url"]
    robots = '<meta name="robots" content="noindex">\n' if d.get("noindex") else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{d['title']}</title>
<meta name="description" content="{d['desc']}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DMC Seville Event">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{d['title']}">
<meta property="og:description" content="{d['desc']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://www.dmcsevilleevent.com/fotos/about-us/about-us-hero-gunvor-at-setas-sunset.webp">
<meta name="twitter:card" content="summary_large_image">
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Varela+Round&display=swap" rel="stylesheet">
<style>body{{margin:0;}}a{{text-decoration:none;}}*{{box-sizing:border-box;}}</style>
</helmet>
<div style="font-family:'Montserrat',sans-serif;color:#1f2d33;background:#fffdfb;">
  <dc-import name="SiteHeader" hint-size="100%,120"></dc-import>
  <section style="position:relative;overflow:hidden;height:clamp(300px,46svh,440px);">
    <div style="position:absolute;inset:0;background:linear-gradient(135deg,#0d3d40,#15cad2);"></div>
    <div style="position:relative;z-index:2;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px;color:#ffffff;">
      <div style="font-family:'Varela Round',sans-serif;letter-spacing:1.5px;font-size:13px;color:#c9f4f0;margin-bottom:10px;">{d['label']}</div>
      <h1 style="font-family:'Montserrat',sans-serif;font-weight:800;font-size:clamp(28px,4.5vw,46px);margin:0;text-transform:uppercase;letter-spacing:1px;">{d['h1']}</h1>
    </div>
  </section>
  <section style="max-width:860px;margin:0 auto;padding:60px 32px 80px;">
    {d['body']}
  </section>
  <dc-import name="SiteFooter" hint-size="100%,300"></dc-import>
</div>
</x-dc>
</body>
</html>
"""
