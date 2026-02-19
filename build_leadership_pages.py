"""
build_leadership_pages.py - Rebuilds leadership-directory.html for every
district using REAL contact data from the Texas Special Ed directory.
"""

import os
import re
import json

SITE_DOMAIN = "https://texasspecialed.com"
LINK_BUNDLE = "https://buy.stripe.com/YOUR_BUNDLE_LINK"

# Real contact data keyed by district slug
CONTACTS = {
    # REGION 4 - Houston Metro
    "houston-isd": {},
    "dallas-isd": {
        "exec_director_name": "Dr. Kay Wilcots",
        "exec_director_email": "kwilcots@dallasisd.org",
        "main_phone": "972-581-4662",
        "dyslexia_coordinator": "Naida Vega",
    },
    "cypress-fairbanks-isd": {
        "dyslexia_coordinator": "Danielle Olivier",
    },
    "katy-isd": {
        "exec_director_name": "Dr. Gwen Coffey",
        "main_phone": "281-396-6000",
        "office_address": "6301 S. Stadium Ln, Katy, TX 77494",
    },
    "fort-bend-isd": {
        "main_phone": "281-634-1000",
        "office_address": "16431 Lexington Blvd, Sugar Land, TX 77479",
        "records_clerk": "Antoinette Adams",
    },
    "plano-isd": {
        "exec_director_name": "Mackenzie Casall",
        "main_phone": "469-752-8240",
        "office_address": "2700 W 15th St, Plano, TX 75075",
        "records_clerk": "Betty Copeland",
    },
    "pasadena-isd": {
        "exec_director_name": "Michelle LeBleu",
        "exec_director_email": "mlebleu@pasadenaisd.org",
        "main_phone": "713-740-5379",
        "office_address": "3920 Mickey Gilley Blvd, Pasadena, TX 77505",
        "evaluation_coordinator": "Jessica Alanis",
        "records_clerk": "Kathryn Garcia",
    },
    "spring-isd": {
        "main_phone": "281-891-6000",
        "office_address": "16717 Ella Blvd, Houston, TX 77090",
        "records_clerk": "Shavon Brown",
    },
    "carrollton-farmers-branch-isd": {
        "exec_director_name": "Monica Johnson",
        "main_phone": "972-968-6100",
        "office_address": "1445 N Perry Rd, Carrollton, TX 75006",
        "dyslexia_coordinator": "Nancy Gallegos",
        "records_clerk": "Mary Duncan",
    },
    "mckinney-isd": {
        "main_phone": "469-302-4000",
        "office_address": "One Duvall St, McKinney, TX 75069",
        "autism_specialist": "Micah Jason Reed",
        "evaluation_coordinator": "Micah Jason Reed",
    },
    "wylie-isd": {
        "main_phone": "972-429-2370",
        "dyslexia_coordinator": "Angela Waters",
    },
    "rockwall-isd": {
        "exec_director_name": "Melissa Melton",
        "exec_director_email": "melissa.melton@rockwallisd.org",
        "main_phone": "972-771-0605",
        "office_address": "1050 Williams St, Rockwall, TX 75087",
    },
    "new-caney-isd": {
        "autism_specialist": "Amber Snyder",
    },
    "forney-isd": {
        "exec_director_name": "Laura Merchant",
        "exec_director_email": "info@edu.forneyisd.net",
        "main_phone": "469-762-4100",
        "office_address": "701 S. Bois D'Arc St, Forney, TX 75126",
        "dyslexia_coordinator": "Tana Richardson",
        "autism_specialist": "Karen Sanders",
        "evaluation_coordinator": "Jamie Wilson",
    },
    "friendswood-isd": {
        "exec_director_name": "Ashley Ashna",
        "exec_director_email": "aashna@fisdk12.net",
        "main_phone": "281-482-1267",
        "office_address": "302 Laurel Dr, Friendswood, TX 77546",
    },
    "alief-isd": {
        "main_phone": "281-498-8110",
        "dyslexia_coordinator": "Sheirly Alexandre",
    },
    # REGION 20 - San Antonio
    "northside-isd": {
        "exec_director_name": "Veronica Mechler",
        "exec_director_email": "veronica.mechler@nisd.net",
        "main_phone": "210-397-8740",
    },
    "north-east-isd": {
        "exec_director_name": "Vanessa S. Kosar",
        "exec_director_email": "vshowm@neisd.net",
        "main_phone": "210-407-0185",
    },
    "san-antonio-isd": {
        "exec_director_name": "Lisa Franke",
        "exec_director_email": "lfranke1@saisd.net",
        "main_phone": "210-354-9565",
    },
    "comal-isd": {
        "exec_director_name": "Michele Martella",
        "exec_director_email": "michele.martella@comalisd.org",
        "main_phone": "830-221-2088",
    },
    "judson-isd": {
        "exec_director_name": "Kerry Armstead",
        "exec_director_email": "karmstead@judsonisd.org",
        "main_phone": "210-945-5348",
    },
    "schertz-cibolo-universal-city-isd": {
        "exec_director_name": "Suanne Chang-Ponce",
        "exec_director_email": "schangponce@scucisd.org",
        "main_phone": "210-945-6448",
    },
    "georgetown-isd": {
        "exec_director_name": "Sheri Ogden",
        "exec_director_email": "ogdens@georgetownisd.org",
    },
    "east-central-isd": {
        "exec_director_name": "Marissa Perez",
        "exec_director_email": "marissa.perez@ecisd.net",
        "main_phone": "210-648-7861",
        "office_address": "6674 New Sulphur Springs Rd, San Antonio, TX",
    },
    "seguin-isd": {
        "exec_director_name": "Rebecca Bird",
        "exec_director_email": "rbird@seguin.k12.tx.us",
        "main_phone": "830-401-8651",
        "office_address": "1221 E. Kingsbury, Seguin, TX 78155",
        "records_clerk": "Genae Mccann",
    },
    # REGION 13 - Austin
    "austin-isd": {
        "exec_director_name": "Kim Pollard",
        "exec_director_email": "kimberley.pollard@austinisd.org",
        "main_phone": "512-414-1700",
        "office_address": "4000 S. I-H 35 Frontage Rd, Austin, TX 78704",
        "dyslexia_coordinator": "Suzann Vera",
    },
    "san-marcos-cisd": {
        "main_phone": "512-393-6800",
        "dyslexia_coordinator": "Emily McKinney",
    },
    # REGION 11 - Fort Worth
    "arlington-isd": {
        "main_phone": "682-867-7692",
        "office_address": "690 E. Lamar Blvd, Arlington, TX 76011",
        "records_clerk": "Dori Seimet",
    },
    "northwest-isd": {
        "exec_director_name": "Kristine Kelly",
        "dyslexia_coordinator": "Ruth Ann Beagle",
        "evaluation_coordinator": "Gail Atkinson",
    },
    "crowley-isd": {
        "exec_director_name": "Tamika Williams",
        "exec_director_email": "tamika.williams@crowley.k12.tx.us",
        "main_phone": "817-297-5300",
        "office_address": "1900 Crowley Pride Dr, Fort Worth, TX 76036",
        "records_clerk": "Gevell Swan",
    },
    "keller-isd": {
        "main_phone": "817-744-1265",
        "office_address": "350 Keller Parkway, Keller, TX 76248",
        "records_clerk": "Alison Rea",
    },
    # REGION 19 - El Paso
    "el-paso-isd": {
        "dyslexia_coordinator": "Xarfie Salvosa",
    },
    # REGION 18 - Midland/Odessa
    "ector-county-isd": {
        "dyslexia_coordinator": "Autym Bruno",
    },
    # REGION 2 - Corpus Christi
    "corpus-christi-isd": {
        "exec_director_name": "Dr. Jennifer Arismendi",
        "main_phone": "361-878-2680",
        "office_address": "801 Leopard, Corpus Christi, TX 78401",
    },
    # REGION 6 - Bryan
    "bryan-isd": {
        "exec_director_name": "Dr. Catherine George",
        "exec_director_email": "catherine.george@bryanisd.org",
        "main_phone": "979-209-2780",
        "office_address": "1307 Memorial Dr, Bryan, TX 77802",
        "records_clerk": "Kimberly Adams",
    },
    # REGION 12 - Waco
    "waco-isd": {
        "main_phone": "254-755-9473",
        "office_address": "501 Franklin Ave, Waco, TX 76701",
        "evaluation_coordinator": "Cathy Parker",
    },
}

# All possible contact fields with default empty string
ALL_FIELDS = [
    "exec_director_name", "exec_director_email", "main_phone",
    "office_address", "dyslexia_coordinator", "autism_specialist",
    "evaluation_coordinator", "records_clerk"
]

# Role display config: (field, label, why_it_matters)
ROLES = [
    ("exec_director_name",
     "Executive Director of Special Education",
     "Chief compliance officer for IDEA and TEA. Direct all written requests, complaints, and escalations here."),
    ("dyslexia_coordinator",
     "Dyslexia Coordinator",
     "Oversees dyslexia screening and the 2024 Texas Dyslexia Handbook compliance. Contact if your child has not been screened or lacks structured literacy services."),
    ("autism_specialist",
     "Autism Specialist / BCBA",
     "Ensures ARD committees address all 11 required Autism Supplement strategies under Commissioner's Rule 89.1055."),
    ("evaluation_coordinator",
     "Evaluation Coordinator",
     "Manages FIE evaluations and the strict 45-school-day timeline. Contact if your child's evaluation is overdue."),
    ("records_clerk",
     "Special Education Records Clerk",
     "Handles IEP/FIIE records, TREx transfers, and FERPA requests. Contact when transferring schools or requesting records."),
]

GLOBAL_CSS = """<style>
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1e293b;background:#fff;line-height:1.6;}
  .site-header{background:#0f172a;padding:14px 0;}
  .navbar{max-width:1100px;margin:0 auto;padding:0 20px;display:flex;align-items:center;}
  .container{max-width:860px;margin:0 auto;padding:40px 20px;}
  h1{font-size:2rem;margin-bottom:20px;color:#0f172a;}
  h2{font-size:1.5rem;margin:30px 0 10px;color:#0f172a;}
  p{margin-bottom:14px;color:#374151;}
  a{color:#2563eb;}
  .site-footer{background:#0f172a;color:#94a3b8;text-align:center;padding:30px 20px;margin-top:60px;font-size:0.85rem;}
  table{width:100%;border-collapse:collapse;margin-bottom:30px;}
  th{text-align:left;padding:10px 14px;border:1px solid #e2e8f0;background:#f1f5f9;font-size:0.85rem;color:#475569;}
  td{padding:11px 14px;border:1px solid #e2e8f0;font-size:0.9rem;vertical-align:top;}
  tr:hover td{background:#f8fafc;}
  .badge-ok{display:inline-block;background:#dcfce7;color:#166534;padding:2px 9px;border-radius:12px;font-size:0.75rem;font-weight:700;}
  .badge-no{display:inline-block;background:#fef9c3;color:#854d0e;padding:2px 9px;border-radius:12px;font-size:0.75rem;}
  .info-box{background:#f0f9ff;border-left:4px solid #0ea5e9;padding:16px 20px;border-radius:4px;margin:20px 0;font-size:0.9rem;}
  .warn-box{background:#fff7ed;border-left:4px solid #f97316;padding:16px 20px;border-radius:4px;margin:20px 0;font-size:0.9rem;}
  .contact-bar{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:18px 22px;margin-bottom:28px;display:flex;flex-wrap:wrap;gap:20px;}
  .contact-bar p{margin:0;font-size:0.95rem;}
  .tips-box{background:#f8fafc;border-radius:8px;padding:25px;margin:40px 0;}
  .tips-box h2{margin-bottom:14px;}
</style>"""

HEADER = '<header class="site-header"><nav class="navbar"><a href="/"><img src="/images/texasspecialed-logo.png" alt="Texas Special Ed" width="200"></a></nav></header>'
FOOTER = '<footer class="site-footer"><p>&copy; 2026 TexasSpecialEd.com &nbsp;|&nbsp; Not legal advice. For advocacy information only.</p><p style="margin-top:8px;"><a href="/privacy" style="color:#64748b;">Privacy</a> &nbsp;|&nbsp; <a href="/sitemap.xml" style="color:#64748b;">Sitemap</a></p></footer>'


def slug_to_name(slug):
    name = slug.replace("-", " ").title()
    name = name.replace(" Isd", " ISD").replace(" Cisd", " CISD")
    return name


def get_contacts(slug):
    base = {f: "" for f in ALL_FIELDS}
    base.update(CONTACTS.get(slug, {}))
    return base


def count_fields(contacts):
    return sum(1 for f in ALL_FIELDS if contacts.get(f))


def contact_bar(contacts):
    phone = contacts.get("main_phone", "")
    addr = contacts.get("office_address", "")
    if not phone and not addr:
        return ""
    items = []
    if phone:
        items.append(f'<p><strong>Main Phone:</strong> <a href="tel:{phone}">{phone}</a></p>')
    if addr:
        mq = addr.replace(" ", "+")
        items.append(f'<p><strong>Office:</strong> <a href="https://maps.google.com/?q={mq}" target="_blank" rel="noopener">{addr}</a></p>')
    return f'<div class="contact-bar">{"".join(items)}</div>'


def staff_table(name, contacts):
    rows = ""
    for field, label, why in ROLES:
        val = contacts.get(field, "")

        if field == "exec_director_name":
            email = contacts.get("exec_director_email", "")
            if val and email:
                cell = f'{val}<br><a href="mailto:{email}" style="font-size:0.85rem;">{email}</a>'
                badge = '<span class="badge-ok">Verified</span>'
            elif val:
                cell = val
                badge = '<span class="badge-ok">Name only</span>'
            elif email:
                cell = f'<a href="mailto:{email}">{email}</a>'
                badge = '<span class="badge-ok">Email only</span>'
            else:
                cell = '<span style="color:#94a3b8;font-style:italic;">Not on file</span>'
                badge = '<span class="badge-no">Not Found</span>'
        else:
            if val:
                cell = val
                badge = '<span class="badge-ok">Verified</span>'
            else:
                cell = '<span style="color:#94a3b8;font-style:italic;">Not on file &mdash; check district site</span>'
                badge = '<span class="badge-no">Not Found</span>'

        rows += f"""
  <tr>
    <td style="font-weight:600;width:26%;">{label}</td>
    <td style="width:36%;">{cell}</td>
    <td style="width:12%;text-align:center;">{badge}</td>
    <td style="width:26%;color:#64748b;font-size:0.82rem;">{why}</td>
  </tr>"""

    return f"""<table>
  <thead>
    <tr>
      <th>Role</th>
      <th>Name / Contact</th>
      <th>Status</th>
      <th>Why This Matters</th>
    </tr>
  </thead>
  <tbody>{rows}
  </tbody>
</table>"""


def status_banner(name, found):
    if found == 0:
        return f'<div class="warn-box"><strong>No verified data on file for {name}.</strong> Visit the district website or call the main office directly. Do not send formal correspondence without first confirming the correct contact.</div>'
    elif found < 4:
        return f'<div class="warn-box"><strong>Partial data:</strong> {found} of 8 fields verified. Confirm contacts with the district before sending official documents.</div>'
    else:
        return f'<div class="info-box"><strong>{found} of 8 fields verified</strong> from TEA AskTED and district records. Staff changes frequently &mdash; confirm before sending formal correspondence.</div>'


def tips_section(name):
    return f"""

<section style="margin:40px 0;">
  <h2>How to Find {name} Special Education Contacts Yourself</h2>
  <p>If contact information is not listed above, you have several reliable paths to find the correct person at {name}. The most authoritative source in Texas is the <strong>AskTED directory</strong> (Texas Education Directory), maintained by the Texas Education Agency at askted.tea.texas.gov. Every Texas public school district is legally required to keep their special education director contact current in AskTED. Search for "{name}" and look for the Special Education Director or Child Find Contact entry. This data is updated daily and reflects the person currently designated by the district to receive official correspondence.</p>
  <p>The second path is the district's official website. Navigate to the district homepage and look for a "Departments" or "Student Services" menu. Special Education is almost always listed as a top-level department. Once on the department page, look for a staff directory, contact page, or "About Us" section. If the site lists a general department email such as sped@[district].net, that is an appropriate starting point for initial inquiries, but you should still request the name of the current Executive Director before sending any formal legal documents.</p>
  <p>If neither of those produces a current name and email, Texas law gives you a third option: a <strong>Public Information Act (PIA) request</strong>, also known as an open records request. Under Texas Government Code Chapter 552, you have the right to request the name, title, and work email of any district employee. Submit the request in writing to the district's Public Information Officer. The district must respond within 10 business days. This is a formal legal right and districts cannot refuse to provide basic staff contact information through this channel.</p>
  <p>Once you have confirmed the correct contact, follow the communication best practices below to ensure every message you send creates a clear, timestamped paper trail.</p>
</section>

<section style="margin:40px 0;padding:25px;background:#fef9c3;border-left:5px solid #ca8a04;border-radius:4px;">
  <h2 style="color:#713f12;margin-bottom:14px;">Your Legal Rights When Contacting {name}</h2>
  <p>Parents of children receiving or seeking special education services in {name} have specific, enforceable legal rights that govern how the district must respond to your communications. Understanding these rights before you reach out is essential.</p>
  <p><strong>The right to a written response.</strong> Under the Individuals with Disabilities Education Act (IDEA), when you submit a written request &mdash; whether for an evaluation, records, or an ARD meeting &mdash; the district must respond in writing. A verbal response to a written request does not satisfy the district's legal obligation. If a staff member calls you in response to a written request, always follow up by asking them to confirm the response in writing.</p>
  <p><strong>The right to prior written notice.</strong> Before {name} proposes or refuses to take any action regarding your child's identification, evaluation, educational placement, or provision of a Free Appropriate Public Education (FAPE), they must provide you with written notice explaining their reasoning, the options they considered, and why they rejected those options. This is called Prior Written Notice (PWN) and it is required by 34 CFR 300.503. If {name} has taken an action affecting your child's special education services without providing PWN, that is a procedural violation you can raise in a TEA State Complaint.</p>
  <p><strong>The right to your child's records within 45 days.</strong> Under FERPA (Family Educational Rights and Privacy Act), you have the right to inspect and review your child's education records. Texas school districts, including {name}, must respond to a records request within 45 days. Special education records &mdash; including all IEPs, FIE evaluations, ARD meeting notes, and progress reports &mdash; are included. You may request copies, and while the district may charge a reasonable fee for copies, they cannot charge a fee that effectively prevents you from exercising your right.</p>
  <p><strong>The right to file a complaint if they do not respond.</strong> If {name} does not respond appropriately to your written communications, you have the right to file a State Complaint with the Texas Education Agency at no cost. The TEA must resolve State Complaints within 60 calendar days. You can also file a complaint with the U.S. Department of Education's Office for Civil Rights (OCR) if you believe the district has discriminated against your child based on disability. Both of these options are entirely free and do not require an attorney.</p>
</section>

<section style="margin:40px 0;">
  <h2>Communication Best Practices for {name} Parents</h2>
  <p><strong>Always write, never only call.</strong> Phone calls leave no legal record. After every phone conversation with any {name} staff member, send a follow-up email within 24 hours restating what was discussed, what was agreed to, and any next steps. Begin the email with "Per our phone call today..." This transforms an off-the-record conversation into documented correspondence.</p>
  <p><strong>Use a specific subject line on every email.</strong> Every message you send to {name} Special Education should start with the same format: <em>"Written Request &mdash; [Your Child's Full Name] &mdash; [Today's Date]"</em>. This signals to the recipient that the email is a formal communication, not an informal inquiry, and it creates an indexed paper trail that is searchable if a dispute ever goes to a due process hearing.</p>
  <p><strong>Send formal requests by certified mail in addition to email.</strong> When you are requesting an evaluation, invoking due process rights, filing a formal complaint, or revoking consent, send a physical letter via USPS Certified Mail with Return Receipt Requested. The green return receipt card, once signed and returned to you, is legal proof that {name} received your correspondence on a specific date. This date matters because it starts legal clocks &mdash; the 45-school-day evaluation timeline, for example, begins from written consent, not from when the district acknowledges receipt verbally.</p>
  <p><strong>BCC your personal email on every message.</strong> Always send a blind carbon copy to your own personal email address on every message you send to {name}. Your sent folder in a school district email system is controlled by the district. Your own BCC copy is timestamped by your email provider and entirely in your control.</p>
  <p><strong>Keep a dedicated folder.</strong> Create a physical or digital folder specifically for your child's {name} special education communications. Include printed or saved copies of every email, every IEP, every evaluation report, every ARD meeting notice, and every letter. If a dispute escalates to a TEA State Complaint or due process hearing, the parent who has organized records has an enormous advantage.</p>
</section>
"""


def schema(slug, name, contacts):
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": contacts.get("exec_director_name") or "Director of Special Education",
        "jobTitle": "Executive Director of Special Education",
        "worksFor": {
            "@type": "EducationalOrganization",
            "name": name,
            "url": f"{SITE_DOMAIN}/districts/{slug}/"
        }
    }
    if contacts.get("exec_director_email"):
        person["email"] = contacts["exec_director_email"]
    if contacts.get("main_phone"):
        person["telephone"] = contacts["main_phone"]
    if contacts.get("office_address"):
        person["address"] = {"@type": "PostalAddress", "streetAddress": contacts["office_address"]}
    return f'<script type="application/ld+json">{json.dumps(person, indent=2)}</script>'


def sales_card():
    return f"""<div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:white;padding:30px;border-radius:8px;text-align:center;margin:40px 0;">
  <span style="background:#d4af37;color:#000;padding:5px 15px;font-weight:bold;border-radius:20px;font-size:0.8rem;">BEST VALUE</span>
  <h3 style="color:white;margin-top:15px;">"I'm overwhelmed. Give me everything."</h3>
  <p style="color:#e2e8f0;">Get the complete <strong>Parent Protection Bundle</strong>: ARD Prep, Behavior Defense, Dyslexia, and Accommodations.</p>
  <a href="{LINK_BUNDLE}" style="background:#d4af37;color:#000;padding:12px 25px;text-decoration:none;font-weight:bold;border-radius:4px;display:inline-block;margin-top:10px;">Get All 6 Kits for $97</a>
</div>"""


def build_page(slug):
    name = slug_to_name(slug)
    contacts = get_contacts(slug)
    found = count_fields(contacts)
    canonical = f"{SITE_DOMAIN}/districts/{slug}/leadership-directory.html"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} Special Education Contacts | Staff Directory</title>
  <meta name="description" content="Verified special education staff for {name}: Executive Director, Dyslexia Coordinator, Autism Specialist, Evaluation Coordinator, and Records Clerk.">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{name} Special Education Staff Directory">
  <meta property="og:url" content="{canonical}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary">
{GLOBAL_CSS}
</head>
<body>
{HEADER}
<main class="container">
  <h1>{name} Special Education Staff Directory</h1>
  <p style="color:#64748b;margin-bottom:20px;">
    Contact data sourced from the TEA AskTED directory and district records.
    Staff assignments change &mdash; always confirm before sending formal documents.
  </p>

  {status_banner(name, found)}
  {contact_bar(contacts)}
  {staff_table(name, contacts)}

  <div class="warn-box">
    <strong>&#x26A0;&#xFE0F; Verify Before Sending Official Documents</strong><br>
    Before submitting a written evaluation request, due process notice, or formal complaint,
    call the main office to confirm the correct name and current email. Misdirected
    correspondence does not pause legal timelines.
  </div>

  {tips_section(name)}
  {sales_card()}

  <p style="margin-top:30px;margin-bottom:10px;">
    <a href="index.html">&larr; Back to {name} Special Education Hub</a>
  </p>
</main>
{FOOTER}
{schema(slug, name, contacts)}
</body>
</html>"""


if __name__ == "__main__":
    root = "districts"
    if not os.path.exists(root):
        print(f"[ERROR] '{root}' folder not found. Run from the same directory as districts/")
        exit(1)

    slugs = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    print(f"Found {len(slugs)} district folders. Real data for {len(CONTACTS)} districts.\n")

    written = with_data = no_data = 0

    for slug in slugs:
        out = os.path.join(root, slug, "leadership-directory.html")
        html = build_page(slug)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        found = count_fields(get_contacts(slug))
        written += 1
        if found:
            with_data += 1
            print(f"  [OK]          {slug_to_name(slug)} — {found}/8 fields")
        else:
            no_data += 1
            print(f"  [PLACEHOLDER] {slug_to_name(slug)} — no data yet")

    print(f"\nDone. {written} pages written: {with_data} with data, {no_data} placeholders.")
    print("To add more data: update CONTACTS dict and re-run. All other pages stay untouched.")